import logging
from typing import List, Optional
from sqlalchemy import cast, case, func, literal, select, ARRAY, Text, and_
from sqlalchemy.ext.asyncio import AsyncSession
from app.domain.interfaces import IDatasetRepository
from app.repository.models import DatasetORM, FileORM, FavoriteDatasetORM, ReportORM, UserReportORM

logger = logging.getLogger(__name__)


class DatasetRepository(IDatasetRepository):

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def exists(self, dataset_id: int) -> bool:
        """Проверяет существование датасета по айди"""

        logger.debug("Проверка существования датасета: dataset_id=%s", dataset_id)
        query = select(DatasetORM.dataset_id).where(DatasetORM.dataset_id == dataset_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none() is not None

    async def get_non_data_files_by_dataset_id(self, dataset_id: int) -> List[dict]:
        """Файлы датасета, которые не являются data"""
        query = (
            select(
                FileORM.file_id,
                FileORM.file_name,
                FileORM.file_size_kb,
                FileORM.file_updated_at,
            )
            .where(FileORM.dataset_id == dataset_id)
            .where(FileORM.is_data.is_(False))
            .order_by(FileORM.file_id.asc())
        )
        result = await self.session.execute(query)
        rows = result.all()
        return [
            {
                "file_id": int(r.file_id),
                "file_name": r.file_name,
                "file_size_kb": float(r.file_size_kb) if r.file_size_kb is not None else None,
                "file_updated_at": r.file_updated_at,
            }
            for r in rows
        ]

    async def get_datasets_with_data_files_and_user_reports_by_dataset_ids(
        self,
        *,
        user_id: int,
        dataset_ids: List[int],
    ) -> List[dict]:
        """Возвращает датасеты с их data-файлами и отчётом пользователя по каждому файлу"""
        if not dataset_ids:
            return []

        query = (
            select(
                DatasetORM.dataset_id,
                DatasetORM.source,
                DatasetORM.title,
                DatasetORM.description,
                DatasetORM.tags,
                DatasetORM.dataset_format,
                DatasetORM.dataset_size_kb,
                DatasetORM.status,
                DatasetORM.download_url,
                DatasetORM.repository_url,
                DatasetORM.source_updated_at,
                FileORM.file_id,
                FileORM.file_name,
                FileORM.file_size_kb,
                FileORM.file_updated_at,
                UserReportORM.report_id.label("user_report_id"),
                case(
                    (FavoriteDatasetORM.user_id.is_not(None), True),
                    else_=False,
                ).label("is_favorite"),
            )
            .join(FileORM, FileORM.dataset_id == DatasetORM.dataset_id)
            .outerjoin(
                FavoriteDatasetORM,
                and_(
                    FavoriteDatasetORM.dataset_id == DatasetORM.dataset_id,
                    FavoriteDatasetORM.user_id == user_id,
                ),
            )
            .outerjoin(ReportORM, ReportORM.file_id == FileORM.file_id)
            .outerjoin(
                UserReportORM,
                and_(
                    UserReportORM.user_id == user_id,
                    UserReportORM.report_id == ReportORM.report_id,
                ),
            )
            .where(DatasetORM.dataset_id.in_(dataset_ids))
            .where(FileORM.is_data.is_(True))
            .order_by(DatasetORM.dataset_id.asc(), FileORM.file_id.asc())
        )

        result = await self.session.execute(query)
        rows = result.all()
        return self._rows_to_dataset_with_files(rows)

    async def get_favorite_datasets_with_data_files_and_user_reports(
        self,
        *,
        user_id: int,
    ) -> List[dict]:
        """Возвращает избранные датасеты пользователя с их data-файлами и отчётом пользователя по каждому файлу"""
        query = (
            select(
                DatasetORM.dataset_id,
                DatasetORM.source,
                DatasetORM.title,
                DatasetORM.description,
                DatasetORM.tags,
                DatasetORM.dataset_format,
                DatasetORM.dataset_size_kb,
                DatasetORM.status,
                DatasetORM.download_url,
                DatasetORM.repository_url,
                DatasetORM.source_updated_at,
                FileORM.file_id,
                FileORM.file_name,
                FileORM.file_size_kb,
                FileORM.file_updated_at,
                UserReportORM.report_id.label("user_report_id"),
                literal(True).label("is_favorite"),
            )
            .join(FavoriteDatasetORM, FavoriteDatasetORM.dataset_id == DatasetORM.dataset_id)
            .join(FileORM, FileORM.dataset_id == DatasetORM.dataset_id)
            .outerjoin(ReportORM, ReportORM.file_id == FileORM.file_id)
            .outerjoin(
                UserReportORM,
                and_(
                    UserReportORM.user_id == user_id,
                    UserReportORM.report_id == ReportORM.report_id,
                ),
            )
            .where(FavoriteDatasetORM.user_id == user_id)
            .where(FileORM.is_data.is_(True))
            .order_by(DatasetORM.dataset_id.asc(), FileORM.file_id.asc())
        )

        result = await self.session.execute(query)
        rows = result.all()
        return self._rows_to_dataset_with_files(rows)

    async def search_datasets_with_data_files_and_user_reports(
        self,
        *,
        user_id: int,
        query: Optional[str] = None,
        sources: Optional[List[str]] = None,
        file_formats: Optional[List[str]] = None,
        max_size_mb: Optional[float] = None,
        tags: Optional[List[str]] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[dict]:
        """Поиск датасетов + data-файлы + наличие отчёта у пользователя по каждому файлу"""
        if query is not None:
            query = query.strip() or None
        if sources is not None and len(sources) == 0:
            sources = None
        if file_formats is not None and len(file_formats) == 0:
            file_formats = None
        if tags is not None and len(tags) == 0:
            tags = None

        conditions = []

        if query:
            ts_query = func.plainto_tsquery("english", query)
            conditions.append(DatasetORM.search_vector.op("@@")(ts_query))

        if sources:
            conditions.append(DatasetORM.source.in_(sources))

        if file_formats:
            conditions.append(DatasetORM.dataset_format.in_(file_formats))

        if max_size_mb is not None:
            max_kb = max_size_mb * 1024.0
            conditions.append(DatasetORM.dataset_size_kb <= max_kb)

        if tags:
            conditions.append(DatasetORM.tags.op("&&")(cast(tags, ARRAY(Text))))

        stmt = select(DatasetORM.dataset_id).where(DatasetORM.status == "active")
        if conditions:
            stmt = stmt.where(*conditions)
        stmt = stmt.order_by(
            DatasetORM.source_updated_at.desc(),
            DatasetORM.dataset_id.desc(),
        )
        stmt = stmt.limit(limit).offset(offset)

        result = await self.session.execute(stmt)
        dataset_ids = [int(x) for x in result.scalars().all()]

        return await self.get_datasets_with_data_files_and_user_reports_by_dataset_ids(
            user_id=user_id,
            dataset_ids=dataset_ids,
        )

    def _rows_to_dataset_with_files(self, rows: list) -> List[dict]:
        out_by_id: dict[int, dict] = {}

        for row in rows:
            dataset_id = int(row.dataset_id)
            ds = out_by_id.get(dataset_id)
            if ds is None:
                ds = {
                    "dataset_id": dataset_id,
                    "source": row.source,
                    "title": row.title,
                    "description": row.description,
                    "tags": row.tags or [],
                    "dataset_format": row.dataset_format,
                    "dataset_size_kb": float(row.dataset_size_kb) if row.dataset_size_kb is not None else None,
                    "status": row.status,
                    "download_url": row.download_url,
                    "repository_url": row.repository_url,
                    "source_updated_at": row.source_updated_at,
                    "is_favorite": bool(row.is_favorite),
                    "files": [],
                }
                out_by_id[dataset_id] = ds


            if row.file_id is None:
                continue

            report_id = int(row.user_report_id) if row.user_report_id is not None else None
            ds["files"].append(
                {
                    "file_id": int(row.file_id),
                    "file_name": row.file_name,
                    "file_size_kb": float(row.file_size_kb) if row.file_size_kb is not None else None,
                    "file_updated_at": row.file_updated_at,
                    "has_user_report": report_id is not None,
                }
            )

        return list(out_by_id.values())