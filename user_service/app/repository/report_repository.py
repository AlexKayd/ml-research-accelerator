import logging
from typing import List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.domain.interfaces import IReportRepository
from app.repository.models import ReportORM, DatasetORM

logger = logging.getLogger(__name__)


class ReportRepository(IReportRepository):
    
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
    
    async def exists(self, report_id: int) -> bool:
        """Проверяет существование отчёта по айди"""
        logger.debug(f"Проверка существования отчёта: report_id={report_id}")
        
        query = select(ReportORM.report_id).where(ReportORM.report_id == report_id)
        result = await self.session.execute(query)
        report_id_result = result.scalar_one_or_none()
        
        exists = report_id_result is not None
        logger.debug(f"Отчёт {'существует' if exists else 'не существует'}: report_id={report_id}")
        return exists
    
    async def get_metadata_batch(self, report_ids: List[int]) -> List[dict]:
        """Получает метаданные (с preview) нескольких отчётов по айди"""
        if not report_ids:
            return []
        
        logger.debug(f"Получение метаданных отчётов: count={len(report_ids)}")
        
        query = (
            select(
                ReportORM.report_id,
                ReportORM.dataset_id,
                ReportORM.status,
                ReportORM.updated_at,
                ReportORM.content,
                DatasetORM.title,
                DatasetORM.source,
                DatasetORM.description,
                DatasetORM.tags,
                DatasetORM.file_format,
                DatasetORM.file_size_mb,
                DatasetORM.download_url,
                DatasetORM.repository_url,
                DatasetORM.status.label("dataset_status"),
            )
            .join(DatasetORM, DatasetORM.dataset_id == ReportORM.dataset_id)
            .where(ReportORM.report_id.in_(report_ids))
            .order_by(ReportORM.updated_at.desc(), ReportORM.report_id.desc())
        )
        
        result = await self.session.execute(query)
        rows = result.all()
        
        reports: List[dict] = []
        for row in rows:
            content = row.content
            reports.append({
                "report_id": row.report_id,
                "dataset_id": row.dataset_id,
                "status": row.status,
                "updated_at": row.updated_at.isoformat() if row.updated_at else None,
                "title": row.title,
                "source": row.source,
                "description": row.description,
                "tags": row.tags,
                "file_format": row.file_format,
                "file_size_mb": float(row.file_size_mb) if row.file_size_mb else None,
                "download_url": row.download_url,
                "repository_url": row.repository_url,
                "dataset_status": row.dataset_status,
                "preview": {
                    "total_rows": content.get("total_rows") if content else None,
                    "total_columns": content.get("total_columns") if content else None,
                    "missing_values": content.get("missing_values") if content else None,
                } if content else None,
            })
        
        logger.debug(f"Найдено отчётов с метаданными: {len(reports)}")
        return reports
    
    async def get_full_metadata(self, report_id: int) -> dict | None:
        """Получает полную метаинформацию по одному отчёту"""
        logger.debug(f"Получение полной метаинформации отчёта: report_id={report_id}")
        
        query = (
            select(
                ReportORM.report_id,
                ReportORM.dataset_id,
                ReportORM.status,
                ReportORM.updated_at,
                ReportORM.content,
                DatasetORM.title,
                DatasetORM.source,
                DatasetORM.description,
                DatasetORM.tags,
                DatasetORM.file_format,
                DatasetORM.file_size_mb,
                DatasetORM.download_url,
                DatasetORM.repository_url,
                DatasetORM.status.label("dataset_status"),
            )
            .join(DatasetORM, DatasetORM.dataset_id == ReportORM.dataset_id)
            .where(ReportORM.report_id == report_id)
        )
        
        result = await self.session.execute(query)
        row = result.one_or_none()
        
        if row is None:
            logger.debug(f"Отчёт не найден для полной метаинформации: report_id={report_id}")
            return None
        
        full = {
            "report_id": row.report_id,
            "dataset_id": row.dataset_id,
            "status": row.status,
            "updated_at": row.updated_at.isoformat() if row.updated_at else None,
            "title": row.title,
            "source": row.source,
            "description": row.description,
            "tags": row.tags,
            "file_format": row.file_format,
            "file_size_mb": float(row.file_size_mb) if row.file_size_mb else None,
            "download_url": row.download_url,
            "repository_url": row.repository_url,
            "dataset_status": row.dataset_status,
            "content": row.content,
        }
        
        logger.debug(f"Полная метаинформация отчёта получена: report_id={report_id}")
        return full