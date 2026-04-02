import asyncio
import logging
from datetime import datetime
from typing import List, Optional, Tuple
from sqlalchemy import delete, select, text, update
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from app.domain.exceptions import DatabaseError
from app.domain.entities import Report
from app.domain.interfaces import IReportRepository
from app.domain.value_objects import ReportStatus
from app.repository.models import ReportORM

logger = logging.getLogger(__name__)


class ReportRepository(IReportRepository):

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, report_id: int) -> Optional[Report]:
        logger.debug("Получение отчёта по report_id=%s", report_id)
        try:
            q = select(ReportORM).where(ReportORM.report_id == report_id)
            res = await self.session.execute(q)
            row = res.scalar_one_or_none()

            return self._orm_to_domain(row) if row is not None else None

        except SQLAlchemyError as e:
            logger.error("Ошибка get_by_id (report_id=%s): %s", report_id, e, exc_info=True)
            raise DatabaseError(
                f"Не удалось получить отчёт report_id={report_id}: {e}",
                operation="get_by_id",
            )

    async def get_by_file_id(self, file_id: int) -> Optional[Report]:
        logger.debug("Получение отчёта по file_id=%s", file_id)

        try:
            q = select(ReportORM).where(ReportORM.file_id == file_id)
            res = await self.session.execute(q)
            row = res.scalar_one_or_none()
            return self._orm_to_domain(row) if row is not None else None

        except SQLAlchemyError as e:
            logger.error("Ошибка get_by_file_id (file_id=%s): %s", file_id, e, exc_info=True)
            raise DatabaseError(
                f"Не удалось получить отчёт по file_id={file_id}: {e}",
                operation="get_by_file_id",
            )

    async def create_processing_report_with_advisory_lock(self, file_id: int) -> Report:
        """Создаёт reports строку со статусом processing"""
        attempts = 3
        lock_key = int(file_id)

        for i in range(attempts):
            got_lock = await self._try_advisory_lock(lock_key)
            if got_lock:
                
                try:
                    existing = await self.get_by_file_id(file_id)
                    if existing is not None:
                        logger.debug(
                            "Отчёт уже существует: file_id=%s report_id=%s",
                            file_id,
                            existing.report_id,
                        )
                        return existing

                    now = datetime.now()
                    orm = ReportORM(
                        file_id=file_id,
                        status=ReportStatus.PROCESSING.value,
                        updated_at=None,
                        processing_started_at=now,
                        error_message=None,
                        bucket_name=None,
                        object_key=None,
                        input_file_hash=None,
                    )
                    self.session.add(orm)
                    await self.session.flush()
                    await self.session.refresh(orm)

                    logger.info(
                        "Создан отчёт со статусом processing: report_id=%s file_id=%s",
                        orm.report_id,
                        file_id,
                    )
                    return self._orm_to_domain(orm)
                except Exception:
                    await self.session.rollback()
                    logger.error(
                        "Ошибка создания отчёта processing (file_id=%s)",
                        file_id,
                        exc_info=True,
                    )
                    raise
                finally:
                    await self._advisory_unlock(lock_key)

            await asyncio.sleep(0.1)
            logger.debug(
                "Advisory lock занят (file_id=%s), попытка %s/%s",
                file_id,
                i + 1,
                attempts,
            )

        existing = await self.get_by_file_id(file_id)
        if existing is not None:
            return existing

        raise RuntimeError(
            f"Не удалось создать отчёт: advisory lock занят, и отчёт так и не появился (file_id={file_id})"
        )

    async def lock_for_update(self, report_id: int) -> Report:
        """Возвращает Report под блокировкой FOR UPDATE"""
        logger.debug("Блокировка отчёта FOR UPDATE: report_id=%s", report_id)

        try:
            q = select(ReportORM).where(ReportORM.report_id == report_id).with_for_update()
            res = await self.session.execute(q)
            row = res.scalar_one_or_none()
            if row is None:
                raise RuntimeError(f"Отчёт не найден для блокировки: report_id={report_id}")
            return self._orm_to_domain(row)

        except SQLAlchemyError as e:

            logger.error("Ошибка lock_for_update (report_id=%s): %s", report_id, e, exc_info=True)
            raise DatabaseError(
                f"Не удалось заблокировать отчёт report_id={report_id} FOR UPDATE: {e}",
                operation="lock_for_update",
            )

    async def mark_processing(self, report_id: int, started_at: datetime) -> None:
        """Переводит отчёт в processing"""
        logger.debug("Перевод отчёта в processing: report_id=%s", report_id)

        try:
            q = (
                update(ReportORM)
                .where(ReportORM.report_id == report_id)
                .values(
                    status=ReportStatus.PROCESSING.value,
                    processing_started_at=started_at,
                    error_message=None,
                )
            )
            await self.session.execute(q)
            await self.session.flush()

        except SQLAlchemyError as e:
            
            logger.error("Ошибка mark_processing (report_id=%s): %s", report_id, e, exc_info=True)
            raise DatabaseError(
                f"Не удалось перевести отчёт report_id={report_id} в processing: {e}",
                operation="mark_processing",
            )

    async def mark_failed_if_processing_started_at_matches(
        self,
        report_id: int,
        processing_started_at: datetime,
        error_message: str,
    ) -> bool:
        """CAS-обновление: failed только если status=processing и processing_started_at совпадает"""
        logger.debug(
            "CAS failed: report_id=%s processing_started_at=%s",
            report_id,
            processing_started_at.isoformat(),
        )
        try:
            q = (
                update(ReportORM)
                .where(
                    ReportORM.report_id == report_id,
                    ReportORM.status == ReportStatus.PROCESSING.value,
                    ReportORM.processing_started_at == processing_started_at,
                )
                .values(
                    status=ReportStatus.FAILED.value,
                    error_message=(error_message or "").strip() or "неизвестная ошибка",
                )
            )
            res = await self.session.execute(q)
            await self.session.flush()
            return bool(res.rowcount == 1)

        except SQLAlchemyError as e:
            logger.error(
                "Ошибка CAS failed (report_id=%s): %s",
                report_id,
                e,
                exc_info=True,
            )
            raise DatabaseError(
                f"Не удалось CAS-обновление failed для report_id={report_id}: {e}",
                operation="mark_failed_if_processing_started_at_matches",
            )

    async def mark_completed_if_processing_started_at_matches(
        self,
        report_id: int,
        processing_started_at: datetime,
        bucket_name: str,
        object_key: str,
        input_file_hash: str,
        completed_at: datetime,
    ) -> bool:
        """
        CAS-обновление: completed только если status=processing и processing_started_at совпадает"""
        logger.debug(
            "CAS completed: report_id=%s processing_started_at=%s",
            report_id,
            processing_started_at.isoformat(),
        )
        try:
            q = (
                update(ReportORM)
                .where(
                    ReportORM.report_id == report_id,
                    ReportORM.status == ReportStatus.PROCESSING.value,
                    ReportORM.processing_started_at == processing_started_at,
                )
                .values(
                    status=ReportStatus.COMPLETED.value,
                    bucket_name=bucket_name,
                    object_key=object_key,
                    input_file_hash=(input_file_hash or "").strip().lower() or None,
                    updated_at=completed_at,
                    error_message=None,
                )
            )
            res = await self.session.execute(q)
            await self.session.flush()
            return bool(res.rowcount == 1)

        except SQLAlchemyError as e:
            logger.error(
                "Ошибка CAS completed (report_id=%s): %s",
                report_id,
                e,
                exc_info=True,
            )
            raise DatabaseError(
                f"Не удалось CAS-обновление completed для report_id={report_id}: {e}",
                operation="mark_completed_if_processing_started_at_matches",
            )

    async def mark_deleting(self, report_id: int) -> None:
        """Переводит отчёт в deleting"""
        logger.debug("Перевод отчёта в deleting: report_id=%s", report_id)

        try:
            q = (
                update(ReportORM)
                .where(ReportORM.report_id == report_id)
                .values(status=ReportStatus.DELETING.value)
            )
            await self.session.execute(q)
            await self.session.flush()

        except SQLAlchemyError as e:
            logger.error("Ошибка mark_deleting (report_id=%s): %s", report_id, e, exc_info=True)
            raise DatabaseError(
                f"Не удалось перевести отчёт report_id={report_id} в deleting: {e}",
                operation="mark_deleting",
            )

    async def delete_report_row(self, report_id: int) -> None:
        logger.debug("Удаление строки reports: report_id=%s", report_id)

        try:
            q = delete(ReportORM).where(ReportORM.report_id == report_id)
            await self.session.execute(q)
            await self.session.flush()

        except SQLAlchemyError as e:
            logger.error("Ошибка delete_report_row (report_id=%s): %s", report_id, e, exc_info=True)
            raise DatabaseError(
                f"Не удалось удалить строку отчёта report_id={report_id}: {e}",
                operation="delete_report_row",
            )

    async def mark_stuck_processing_reports_failed(
        self,
        stuck_before: datetime,
        error_message: str,
    ) -> Tuple[int, List[int]]:
        """Находит отчёты в processing с processing_started_at < stuck_before, переводит в failed с указанным error_message"""
        try:
            q = select(ReportORM.report_id).where(
                ReportORM.status == ReportStatus.PROCESSING.value,
                ReportORM.processing_started_at.is_not(None),
                ReportORM.processing_started_at < stuck_before,
            )
            res = await self.session.execute(q)
            ids = [int(x) for x in res.scalars().all()]
            if not ids:
                return 0, []

            msg = (error_message or "").strip() or "отчёт завис"
            upd = (
                update(ReportORM)
                .where(
                    ReportORM.report_id.in_(ids),
                    ReportORM.status == ReportStatus.PROCESSING.value,
                )
                .values(status=ReportStatus.FAILED.value, error_message=msg)
            )
            r = await self.session.execute(upd)
            await self.session.flush()
            count = int(r.rowcount or 0)

            logger.warning("Зависшие отчёты помечены как failed: %s шт.", count)
            return count, ids

        except SQLAlchemyError as e:
            logger.error("Ошибка mark_stuck_processing_reports_failed: %s", e, exc_info=True)
            raise DatabaseError(
                f"Не удалось пометить зависшие отчёты: {e}",
                operation="mark_stuck_processing_reports_failed",
            )

    async def _try_advisory_lock(self, key: int) -> bool:
        """Пытается взять advisory lock"""
        try:
            res = await self.session.execute(
                text("SELECT pg_try_advisory_lock(:key)"),
                {"key": key},
            )
            val = res.scalar_one()
            return bool(val)
            
        except SQLAlchemyError as e:
            logger.error("Ошибка pg_try_advisory_lock(%s): %s", key, e, exc_info=True)
            raise DatabaseError(
                f"Не удалось взять advisory lock key={key}: {e}",
                operation="pg_try_advisory_lock",
            )

    async def _advisory_unlock(self, key: int) -> None:
        """Разблокирует advisory lock"""
        try:
            await self.session.execute(text("SELECT pg_advisory_unlock(:key)"), {"key": key})

        except SQLAlchemyError as e:
            logger.warning("Не удалось pg_advisory_unlock(%s): %s", key, e, exc_info=True)

    def _orm_to_domain(self, orm: ReportORM) -> Report:
        status: ReportStatus = (
            ReportStatus(orm.status) if isinstance(orm.status, str) else orm.status
        )
        return Report(
            report_id=int(orm.report_id) if orm.report_id is not None else None,
            file_id=int(orm.file_id),
            bucket_name=orm.bucket_name,
            object_key=orm.object_key,
            input_file_hash=orm.input_file_hash,
            status=status,
            updated_at=orm.updated_at,
            processing_started_at=orm.processing_started_at,
            error_message=orm.error_message,
        )