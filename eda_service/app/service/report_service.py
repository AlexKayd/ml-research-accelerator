import logging
import asyncio
from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import get_settings
from app.domain.entities import Report
from app.domain.exceptions import ReportDeletingError, DatabaseError, ReportNotFoundError
from app.domain.value_objects import ReportStatus
from app.repository.files_repository import FilesRepository
from app.repository.report_repository import ReportRepository
from app.service.report_generator import ReportGenerator
from app.service.report_generation_jobs import enqueue_generate_task_only, mark_processing_and_enqueue_generate
from app.service.report_subscribers_redis import register_report_subscriber, schedule_user_report_attach_once
from app.schemas.report_schemas import GenerateReportResponse
from app.sse.sse_broker import publish_report_ready_sync
from app.sse.sse_broker import publish_report_deleting_sync

logger = logging.getLogger(__name__)


class ReportService:

    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._settings = get_settings()
        self._reports = ReportRepository(session)
        self._files = FilesRepository(session)
        self._generator = ReportGenerator()

    async def get_or_create_report(self, file_id: int, user_id: int) -> GenerateReportResponse:
        """Возвращает статус, URL или создаёт отчёт и ставит задачу генерации"""
        report = await self._reports.get_by_file_id(file_id)

        if report is None:
            report = await self._reports.create_processing_report_with_advisory_lock(file_id=file_id)
            rid = int(report.report_id or 0)
            await register_report_subscriber(rid, user_id)
            await enqueue_generate_task_only(report_id=rid)
            return GenerateReportResponse(report_id=rid, status="processing", report_url=None)

        if report.status == ReportStatus.DELETING:
            await asyncio.to_thread(
                publish_report_deleting_sync,
                int(user_id),
                int(report.report_id or 0),
            )
            raise ReportDeletingError(int(report.report_id or 0))

        if report.status == ReportStatus.COMPLETED:
            should_regen = await self._should_regenerate_due_to_stale(report, file_id=file_id)
            if should_regen:
                rid = int(report.report_id or 0)
                await register_report_subscriber(rid, user_id)
                await mark_processing_and_enqueue_generate(self._session, report_id=rid)
                return GenerateReportResponse(report_id=rid, status="processing", report_url=None)

            url = self._build_report_url(report)
            rid_done = int(report.report_id or 0)
            await schedule_user_report_attach_once(rid_done, user_id)

            if url:
                await asyncio.to_thread(publish_report_ready_sync, int(user_id), int(rid_done), str(url))
            return GenerateReportResponse(
                report_id=rid_done,
                status="completed",
                report_url=url,
            )

        if report.status == ReportStatus.PROCESSING:
            rid = int(report.report_id or 0)
            await register_report_subscriber(rid, user_id)
            return GenerateReportResponse(
                report_id=rid,
                status="processing",
                report_url=None,
            )

        if report.status == ReportStatus.FAILED:
            rid = int(report.report_id or 0)
            await register_report_subscriber(rid, user_id)
            await mark_processing_and_enqueue_generate(self._session, report_id=rid)
            return GenerateReportResponse(report_id=rid, status="processing", report_url=None)

        return GenerateReportResponse(
            report_id=int(report.report_id or 0),
            status=str(report.status),
            report_url=None,
        )

    async def get_report_status(
        self,
        report_id: int,
        user_id: Optional[int] = None,
    ) -> GenerateReportResponse:
        """Возвращает текущий статус отчёта"""
        report = await self._reports.get_by_id(report_id)
        if report is None:
            raise ReportNotFoundError(report_id=report_id)

        if report.status == ReportStatus.DELETING:
            raise ReportDeletingError(int(report.report_id or 0))

        if report.status == ReportStatus.COMPLETED:
            rid = int(report.report_id or 0)
            if user_id is not None:
                await schedule_user_report_attach_once(rid, user_id)
            return GenerateReportResponse(
                report_id=rid,
                status="completed",
                report_url=self._build_report_url(report),
            )

        if report.status == ReportStatus.PROCESSING:
            rid = int(report.report_id or 0)
            return GenerateReportResponse(
                report_id=rid,
                status="processing",
                report_url=None,
            )

        if report.status == ReportStatus.FAILED:
            return GenerateReportResponse(
                report_id=int(report.report_id or 0),
                status="failed",
                report_url=None,
                error_message=report.error_message,
            )

        return GenerateReportResponse(
            report_id=int(report.report_id or 0),
            status=str(report.status),
            report_url=None,
        )

    async def _should_regenerate_due_to_stale(self, report: Report, file_id: int) -> bool:
        """Проверяет, нужно ли перегенерировать completed-отчёт по возрасту и хешу файла"""
        if report.updated_at is None:
            return False

        stale_after = int(self._settings.REPORT_STALE_AFTER_HOURS)
        if stale_after <= 0:
            return False

        if datetime.now() - report.updated_at <= timedelta(hours=stale_after):
            return False

        info = await self._files.get_file_and_dataset_info(file_id)
        if info is None:
            raise DatabaseError(
                f"Не удалось найти file/dataset для file_id={file_id}",
                operation="get_file_and_dataset_info",
            )
        file_info, dataset_info = info

        new_hash = await self._generator.compute_input_file_hash_from_dataset_zip(
            file_info=file_info,
            dataset_info=dataset_info,
        )

        old_hash = (report.input_file_hash or "").strip().lower() or None
        if old_hash is None:
            return True
        return new_hash != old_hash

    def _build_report_url(self, report: Report) -> Optional[str]:
        """Формирует публичный URL HTML-отчёта в MinIO"""
        if not report.object_key:
            return None
        from app.core.minio import get_minio_client

        return get_minio_client().build_report_url(report.object_key)