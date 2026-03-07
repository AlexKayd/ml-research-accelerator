import logging
from typing import List, Optional
from app.domain.interfaces import IDatasetRepository

logger = logging.getLogger(__name__)


class DatasetService:
    
    def __init__(self, dataset_repository: IDatasetRepository) -> None:
        self.dataset_repository = dataset_repository
    
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
        """Выполняет поиск датасетов по каталогу"""
        if query is not None:
            query = query.strip() or None
        if sources is not None and len(sources) == 0:
            sources = None
        if file_formats is not None and len(file_formats) == 0:
            file_formats = None
        if tags is not None and len(tags) == 0:
            tags = None
        
        if limit <= 0:
            limit = 20
        if limit > 200:
            limit = 200
        
        logger.info(
            "Запрос поиска датасетов: query=%r, sources=%s, file_formats=%s, "
            "max_size_mb=%s, tags=%s, limit=%s, offset=%s",
            query, sources, file_formats, max_size_mb, tags, limit, offset,
        )
        
        datasets = await self.dataset_repository.search_datasets(
            query=query,
            sources=sources,
            file_formats=file_formats,
            max_size_mb=max_size_mb,
            tags=tags,
            limit=limit,
            offset=offset,
        )
        
        logger.info("Найдено датасетов по запросу: %d", len(datasets))
        return datasets