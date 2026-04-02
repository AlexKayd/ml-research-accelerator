import logging
from typing import List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.domain.interfaces import IReportRepository
from app.repository.models import ReportORM, DatasetORM, FileORM, UserReportORM

logger = logging.getLogger(__name__)


class ReportRepository(IReportRepository):

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def exists(self, report_id: int) -> bool:

        logger.debug("Проверка существования отчёта: report_id=%s", report_id)
        query = select(ReportORM.report_id).where(ReportORM.report_id == report_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none() is not None

    async def get_user_reports_list(self, user_id: int) -> List[dict]:
        """Список истории отчётов пользователя"""
        logger.debug("Список истории отчётов: user_id=%s", user_id)
        query = (
            select(
                ReportORM.report_id,
                ReportORM.status,
                ReportORM.updated_at,
                ReportORM.bucket_name,
                ReportORM.object_key,
                FileORM.file_id,
                FileORM.file_name,
                DatasetORM.dataset_id,
                DatasetORM.source,
                DatasetORM.title,
                DatasetORM.repository_url,
            )
            .join(UserReportORM, (UserReportORM.report_id == ReportORM.report_id) & (UserReportORM.user_id == user_id))
            .join(FileORM, FileORM.file_id == ReportORM.file_id)
            .join(DatasetORM, DatasetORM.dataset_id == FileORM.dataset_id)
            .order_by(DatasetORM.dataset_id.asc(), ReportORM.report_id.asc())
        )
        result = await self.session.execute(query)
        rows = result.all()
        return [
            {
                "report_id": int(row.report_id),
                "status": row.status,
                "updated_at": row.updated_at,
                "bucket_name": row.bucket_name,
                "object_key": row.object_key,
                "file_id": int(row.file_id),
                "file_name": row.file_name,
                "dataset_id": int(row.dataset_id),
                "source": row.source,
                "title": row.title,
                "repository_url": row.repository_url,
            }
            for row in rows
        ]