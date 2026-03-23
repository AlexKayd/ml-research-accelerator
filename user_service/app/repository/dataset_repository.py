import logging
from typing import List, Optional

from sqlalchemy import cast, func, select, ARRAY, Text
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.interfaces import IDatasetRepository
from app.repository.models import DatasetORM

logger = logging.getLogger(__name__)


class DatasetRepository(IDatasetRepository):

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def exists(self, dataset_id: int) -> bool:
        logger.debug("Проверка существования датасета: dataset_id=%s", dataset_id)
        query = select(DatasetORM.dataset_id).where(DatasetORM.dataset_id == dataset_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none() is not None

    async def get_metadata_batch(self, dataset_ids: List[int]) -> List[dict]:
        if not dataset_ids:
            return []

        logger.debug("Метаданные для %s датасетов", len(dataset_ids))

        query = select(DatasetORM).where(DatasetORM.dataset_id.in_(dataset_ids))
        result = await self.session.execute(query)
        datasets_orm = result.scalars().all()

        return [
            {
                "dataset_id": ds.dataset_id,
                "source": ds.source,
                "title": ds.title,
                "description": ds.description,
                "tags": ds.tags or [],
                "dataset_format": ds.dataset_format,
                "dataset_size_kb": float(ds.dataset_size_kb)
                if ds.dataset_size_kb is not None
                else None,
                "status": ds.status,
                "download_url": ds.download_url,
                "repository_url": ds.repository_url,
            }
            for ds in datasets_orm
        ]

    async def search_datasets(
        self,
        query: Optional[str] = None,
        sources: Optional[List[str]] = None,
        file_formats: Optional[List[str]] = None,
        max_size_mb: Optional[float] = None,
        tags: Optional[List[str]] = None,
        limit: int = 20,
        offset: int = 0,
    ) -> List[dict]:
        """Поиск по полям sql/ddl.sql (dataset_format, dataset_size_kb)."""
        if query is not None:
            query = query.strip() or None
        if sources is not None and len(sources) == 0:
            sources = None
        if file_formats is not None and len(file_formats) == 0:
            file_formats = None
        if tags is not None and len(tags) == 0:
            tags = None

        logger.debug(
            "Поиск датасетов: query=%r, sources=%s, file_formats=%s, "
            "max_size_mb=%s, tags=%s, limit=%s, offset=%s",
            query,
            sources,
            file_formats,
            max_size_mb,
            tags,
            limit,
            offset,
        )

        conditions = []

        if query:
            ts_query = func.plainto_tsquery("english", query)
            conditions.append(DatasetORM.search_vector.op("@@")(ts_query))

        if sources:
            conditions.append(DatasetORM.source.in_(sources))

        # Параметр API file_formats фильтрует колонку dataset_format
        if file_formats:
            conditions.append(DatasetORM.dataset_format.in_(file_formats))

        if max_size_mb is not None:
            max_kb = max_size_mb * 1024.0
            conditions.append(DatasetORM.dataset_size_kb <= max_kb)

        if tags:
            conditions.append(DatasetORM.tags.op("&&")(cast(tags, ARRAY(Text))))

        stmt = select(DatasetORM)
        if conditions:
            stmt = stmt.where(*conditions)

        stmt = stmt.where(DatasetORM.status == "active")
        stmt = stmt.order_by(
            DatasetORM.source_updated_at.desc(),
            DatasetORM.dataset_id.desc(),
        )
        stmt = stmt.limit(limit).offset(offset)

        result = await self.session.execute(stmt)
        datasets_orm = result.scalars().all()

        logger.debug("Найдено датасетов: %s", len(datasets_orm))
        return [self._orm_to_dict(ds) for ds in datasets_orm]

    def _orm_to_dict(self, dataset_orm: DatasetORM) -> dict:
        return {
            "dataset_id": dataset_orm.dataset_id,
            "source": dataset_orm.source,
            "title": dataset_orm.title,
            "description": dataset_orm.description,
            "tags": dataset_orm.tags or [],
            "dataset_format": dataset_orm.dataset_format,
            "dataset_size_kb": float(dataset_orm.dataset_size_kb)
            if dataset_orm.dataset_size_kb is not None
            else None,
            "status": dataset_orm.status,
            "download_url": dataset_orm.download_url,
            "repository_url": dataset_orm.repository_url,
        }
