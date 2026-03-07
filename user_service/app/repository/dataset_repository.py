import logging
from typing import Optional, List
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import cast, ARRAY, Text
from app.domain.interfaces import IDatasetRepository
from app.repository.models import DatasetORM

logger = logging.getLogger(__name__)


class DatasetRepository(IDatasetRepository):
    
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
    
    async def exists(self, dataset_id: int) -> bool:
        """Проверяет существование датасета по айди"""
        logger.debug(f"Проверка существования датасета: dataset_id={dataset_id}")
        
        query = select(DatasetORM.dataset_id).where(DatasetORM.dataset_id == dataset_id)
        result = await self.session.execute(query)
        dataset_id_result = result.scalar_one_or_none()
        
        exists = dataset_id_result is not None
        logger.debug(f"Датасет {'существует' if exists else 'не существует'}: dataset_id={dataset_id}")
        return exists
    
    async def get_metadata_batch(self, dataset_ids: List[int]) -> List[dict]:
        """Получает метаданные нескольких датасетов по айди"""
        if not dataset_ids:
            return []
        
        logger.debug(f"Получение метаданных для {len(dataset_ids)} датасетов")
        
        query = select(DatasetORM).where(
            DatasetORM.dataset_id.in_(dataset_ids)
        )
        result = await self.session.execute(query)
        datasets_orm = result.scalars().all()
        
        return [
            {
                "dataset_id": ds.dataset_id,
                "source": ds.source,
                "title": ds.title,
                "description": ds.description,
                "tags": ds.tags or [],
                "file_format": ds.file_format,
                "file_size_mb": float(ds.file_size_mb) if ds.file_size_mb else None,
                "download_url": ds.download_url,
                "repository_url": ds.repository_url
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
        offset: int = 0
    ) -> List[dict]:
        """Выполняет полнотекстовый поиск и фильтрацию датасетов"""
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
            query, sources, file_formats, max_size_mb, tags, limit, offset,
        )
        
        conditions = []
        
        if query:
            ts_query = func.plainto_tsquery("english", query)
            conditions.append(DatasetORM.search_vector.op("@@")(ts_query))
        
        if sources:
            conditions.append(DatasetORM.source.in_(sources))
        
        if file_formats:
            conditions.append(DatasetORM.file_format.in_(file_formats))
        
        if max_size_mb is not None:
            conditions.append(DatasetORM.file_size_mb <= max_size_mb)
        
        if tags:
            conditions.append(DatasetORM.tags.op('&&')(cast(tags, ARRAY(Text))))
        
        stmt = select(DatasetORM)
        if conditions:
            stmt = stmt.where(*conditions)
        
        stmt = stmt.order_by(DatasetORM.last_updated.desc(), DatasetORM.dataset_id.desc())
        stmt = stmt.limit(limit).offset(offset)
        
        result = await self.session.execute(stmt)
        datasets_orm = result.scalars().all()
        
        logger.debug("Найдено датасетов по запросу: %d", len(datasets_orm))
        
        return [
            self._orm_to_dict(ds)
            for ds in datasets_orm
        ]
    
    def _orm_to_dict(self, dataset_orm: DatasetORM) -> dict:
        """Конвертирует ORM модель в словарь"""
        return {
            "dataset_id": dataset_orm.dataset_id,
            "source": dataset_orm.source,
            "title": dataset_orm.title,
            "description": dataset_orm.description,
            "tags": dataset_orm.tags or [],
            "file_format": dataset_orm.file_format,
            "file_size_mb": float(dataset_orm.file_size_mb) if dataset_orm.file_size_mb else None,
            "download_url": dataset_orm.download_url,
            "repository_url": dataset_orm.repository_url,
        }