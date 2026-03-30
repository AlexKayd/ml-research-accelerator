import asyncio
import logging
from datetime import datetime, timedelta
from typing import Optional
import redis.asyncio as redis
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import get_settings
from app.core.celery_config import celery_app
from app.core.minio import get_minio_client
from app.domain.entities import DatasetChangeEvent
from app.domain.value_objects import EDAEventType, ReportStatus
from app.repository.files_repository import FilesRepository
from app.repository.report_repository import ReportRepository
from app.service.report_generation_jobs import mark_processing_and_enqueue_generate
from app.service.report_subscribers_redis import get_report_subscribers_sync, pop_report_subscribers_sync
from app.sse.sse_broker import publish_report_deleted_sync, publish_report_deleting_sync

logger = logging.getLogger(__name__)


class AggregationEventService:

    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._settings = get_settings()
        self._files = FilesRepository(session)
        self._reports = ReportRepository(session)

    async def process_event(self, event: DatasetChangeEvent) -> None:
        """Разбирает событие file_updated/file_deleted и ставит нужные Celery-задачи"""
        file_id = event.file_id
        if file_id is None:
            file_id = await self._files.resolve_file_id(
                dataset_id=event.dataset_id,
                file_name=event.file_name,
            )

        if file_id is None:
            logger.info(
                "Событие %s: file_id не найден (dataset_id=%s file_name=%r) - пропуск",
                event.event_type.value,
                event.dataset_id,
                event.file_name,
            )
            return

        report = await self._reports.get_by_file_id(file_id)
        if report is None:
            logger.debug(
                "Событие %s: отчёта нет для file_id=%s - ничего не делаем",
                event.event_type.value,
                file_id,
            )
            return

        if event.event_type == EDAEventType.FILE_DELETED:
            await self._handle_file_deleted(report_id=int(report.report_id or 0), status=report.status)
            return

        if event.event_type == EDAEventType.FILE_UPDATED:
            await self._handle_file_updated(
                report_id=int(report.report_id or 0),
                status=report.status,
                new_file_hash=event.file_hash,
                old_report_hash=report.input_file_hash,
            )
            return

        logger.warning("Неизвестный event_type=%s", event.event_type)

    async def _handle_file_updated(
        self,
        report_id: int,
        status: ReportStatus,
        new_file_hash: Optional[str],
        old_report_hash: Optional[str],
    ) -> None:
        """Логика file_updated: сравнение хешей, перегенерация или ожидалка при processing"""
        new_h = (new_file_hash or "").strip().lower() or None
        old_h = (old_report_hash or "").strip().lower() or None

        if new_h is not None and old_h is not None and new_h == old_h:
            logger.info(
                "file_updated: хеши совпали, отчёт актуален - report_id=%s",
                report_id,
            )
            return

        if status in (ReportStatus.COMPLETED, ReportStatus.FAILED):
            await mark_processing_and_enqueue_generate(self._session, report_id=report_id)
            return

        if status == ReportStatus.PROCESSING:
            await self._enqueue_regen_waiter(report_id=report_id)
            return

        logger.info("file_updated: статус=%s - пропуск (report_id=%s)", status.value, report_id)

    async def _handle_file_deleted(self, report_id: int, status: ReportStatus) -> None:
        """Логика file_deleted: постановка delete_report_task или пропуск по статусу"""
        if status in (ReportStatus.COMPLETED, ReportStatus.FAILED):
            await asyncio.to_thread(
                celery_app.send_task,
                "app.celery.tasks.delete_report_task",
                kwargs={"report_id": report_id},
                queue=self._settings.CELERY_EDA_QUEUE,
            )
            logger.info("Поставлена delete_report_task: report_id=%s", report_id)
            return

        if status == ReportStatus.PROCESSING:
            logger.info("file_deleted: отчёт processing - ждём завершения, report_id=%s", report_id)
            return

        logger.info("file_deleted: статус=%s - пропуск (report_id=%s)", status.value, report_id)

    async def _enqueue_regen_waiter(self, report_id: int) -> None:
        """Ставит ожидалку regen_waiter_task"""
        key = f"eda:regen_waiter:{report_id}"
        ttl = int(self._settings.WAITER_MAX_WAIT_MINUTES) * 60 + 60

        client = redis.from_url(self._settings.REDIS_URL, encoding="utf-8", decode_responses=True)
        try:
            was_set = await client.set(name=key, value="1", nx=True, ex=ttl)
            if not was_set:
                logger.debug("Ожидалка уже поставлена: report_id=%s", report_id)
                return
        finally:
            try:
                await client.aclose()
            except Exception:
                pass

        await asyncio.to_thread(
            celery_app.send_task,
            "app.celery.tasks.regen_waiter_task",
            kwargs={"report_id": report_id},
            queue=self._settings.CELERY_WAITER_QUEUE,
        )
        logger.info("Поставлена regen_waiter_task: report_id=%s", report_id)


class RegenWaiterService:

    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._settings = get_settings()
        self._reports = ReportRepository(session)

    async def wait_and_regenerate(self, report_id: int) -> None:
        """Ожидает смену статуса отчёта и при необходимости ставит перегенерацию"""
        deadline = datetime.now() + timedelta(minutes=int(self._settings.WAITER_MAX_WAIT_MINUTES))
        poll = int(self._settings.WAITER_POLL_INTERVAL_SECONDS)

        while datetime.now() < deadline:
            report = await self._reports.get_by_id(report_id)
            if report is None:
                logger.info("Ожидалка: отчёт исчез из бд, report_id=%s", report_id)
                await self._clear_dedup_key(report_id)
                return

            if report.status in (ReportStatus.COMPLETED, ReportStatus.FAILED):
                await self._clear_dedup_key(report_id)
                await mark_processing_and_enqueue_generate(self._session, report_id=report_id)
                logger.info(
                    "Ожидалка: перегенерация после terminal статуса report_id=%s (без notify user_service)",
                    report_id,
                )
                return

            if report.status == ReportStatus.DELETING:
                logger.info("Ожидалка: отчёт deleting - выходим, report_id=%s", report_id)
                await self._clear_dedup_key(report_id)
                return

            await asyncio.sleep(poll)

        logger.warning("Ожидалка: таймаут ожидания, report_id=%s", report_id)
        await self._clear_dedup_key(report_id)

    async def _clear_dedup_key(self, report_id: int) -> None:
        """Удаляет ключ ожидалки в Redis"""
        key = f"eda:regen_waiter:{report_id}"
        client = redis.from_url(self._settings.REDIS_URL, encoding="utf-8", decode_responses=True)
        try:
            await client.delete(key)
        finally:
            try:
                await client.aclose()
            except Exception:
                pass


class DeleteReportService:

    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._reports = ReportRepository(session)

    async def delete_report(self, report_id: int) -> None:
        """Переводит отчёт в deleting, удаляет объект в MinIO и строку в бд"""
        report = await self._reports.lock_for_update(report_id)

        if report.status == ReportStatus.DELETING:
            logger.info("delete_report: уже deleting, report_id=%s", report_id)
            return

        await self._reports.mark_deleting(report_id)
        await self._session.commit()

        subscribers = await asyncio.to_thread(get_report_subscribers_sync, int(report_id))
        for uid in sorted(subscribers):
            await asyncio.to_thread(publish_report_deleting_sync, int(uid), int(report_id))

        object_key = report.object_key or report.build_default_object_key(report.file_id)
        minio = get_minio_client()

        deleted = False
        last_error = None
        for attempt in range(3):
            try:
                await minio.delete_report_object(object_key)
                deleted = True
                break
            except Exception as e:
                last_error = e
                await asyncio.sleep(1.0 * (2**attempt))

        if not deleted:
            logger.error(
                "delete_report: не удалось удалить объект из MinIO (report_id=%s key=%s): %s",
                report_id,
                object_key,
                last_error,
                exc_info=True,
            )

        await self._reports.delete_report_row(report_id)
        await self._session.commit()

        subscribers = await asyncio.to_thread(pop_report_subscribers_sync, int(report_id))
        for uid in sorted(subscribers):
            await asyncio.to_thread(publish_report_deleted_sync, int(uid), int(report_id))

        logger.info("delete_report: строка отчёта удалена, report_id=%s", report_id)