import logging
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.interfaces import IReportRepository
from app.repository.models import ReportORM, DatasetORM, FileORM, UserReportORM

logger = logging.getLogger(__name__)


def _row_to_list_dict(row) -> dict:
    return {
        "report_id": row.report_id,
        "file_id": row.file_id,
        "bucket_name": row.bucket_name,
        "object_key": row.object_key,
        "dataset_id": row.dataset_id,
        "status": row.status,
        "updated_at": row.updated_at.isoformat() if row.updated_at else None,
        "title": row.title,
        "source": row.source,
        "description": row.description,
        "tags": row.tags,
        "dataset_format": row.dataset_format,
        "dataset_size_kb": float(row.dataset_size_kb)
        if row.dataset_size_kb is not None
        else None,
        "download_url": row.download_url,
        "repository_url": row.repository_url,
        "dataset_status": row.dataset_status,
        "preview": None,
    }


class ReportRepository(IReportRepository):

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def exists(self, report_id: int) -> bool:
        logger.debug("Проверка существования отчёта: report_id=%s", report_id)
        query = select(ReportORM.report_id).where(ReportORM.report_id == report_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none() is not None

    async def get_metadata_for_user_history(self, user_id: int) -> List[dict]:
        """Все отчёты из истории пользователя (users_reports по report_id)."""
        logger.debug("Метаданные отчётов для истории user_id=%s", user_id)
        query = (
            select(
                ReportORM.report_id,
                ReportORM.file_id,
                ReportORM.bucket_name,
                ReportORM.object_key,
                ReportORM.status,
                ReportORM.updated_at,
                FileORM.dataset_id,
                DatasetORM.title,
                DatasetORM.source,
                DatasetORM.description,
                DatasetORM.tags,
                DatasetORM.dataset_format,
                DatasetORM.dataset_size_kb,
                DatasetORM.download_url,
                DatasetORM.repository_url,
                DatasetORM.status.label("dataset_status"),
            )
            .join(FileORM, FileORM.file_id == ReportORM.file_id)
            .join(DatasetORM, DatasetORM.dataset_id == FileORM.dataset_id)
            .join(
                UserReportORM,
                (UserReportORM.report_id == ReportORM.report_id)
                & (UserReportORM.user_id == user_id),
            )
            .order_by(ReportORM.updated_at.desc(), ReportORM.report_id.desc())
        )
        result = await self.session.execute(query)
        rows = result.all()
        out = [_row_to_list_dict(row) for row in rows]
        logger.debug("Найдено записей: %s", len(out))
        return out

    async def get_metadata_batch(self, report_ids: List[int]) -> List[dict]:
        if not report_ids:
            return []
        logger.debug("Получение метаданных отчётов: count=%s", len(report_ids))
        query = (
            select(
                ReportORM.report_id,
                ReportORM.file_id,
                ReportORM.bucket_name,
                ReportORM.object_key,
                ReportORM.status,
                ReportORM.updated_at,
                FileORM.dataset_id,
                DatasetORM.title,
                DatasetORM.source,
                DatasetORM.description,
                DatasetORM.tags,
                DatasetORM.dataset_format,
                DatasetORM.dataset_size_kb,
                DatasetORM.download_url,
                DatasetORM.repository_url,
                DatasetORM.status.label("dataset_status"),
            )
            .join(FileORM, FileORM.file_id == ReportORM.file_id)
            .join(DatasetORM, DatasetORM.dataset_id == FileORM.dataset_id)
            .where(ReportORM.report_id.in_(report_ids))
            .order_by(ReportORM.updated_at.desc(), ReportORM.report_id.desc())
        )
        result = await self.session.execute(query)
        return [_row_to_list_dict(row) for row in result.all()]

    async def get_full_metadata(self, report_id: int) -> dict | None:
        logger.debug("Полная метаинформация отчёта: report_id=%s", report_id)
        query = (
            select(
                ReportORM.report_id,
                ReportORM.file_id,
                ReportORM.bucket_name,
                ReportORM.object_key,
                ReportORM.status,
                ReportORM.updated_at,
                FileORM.dataset_id,
                DatasetORM.title,
                DatasetORM.source,
                DatasetORM.description,
                DatasetORM.tags,
                DatasetORM.dataset_format,
                DatasetORM.dataset_size_kb,
                DatasetORM.download_url,
                DatasetORM.repository_url,
                DatasetORM.status.label("dataset_status"),
            )
            .join(FileORM, FileORM.file_id == ReportORM.file_id)
            .join(DatasetORM, DatasetORM.dataset_id == FileORM.dataset_id)
            .where(ReportORM.report_id == report_id)
        )
        result = await self.session.execute(query)
        row = result.one_or_none()
        if row is None:
            return None
        d = _row_to_list_dict(row)
        d["content"] = None
        return d
