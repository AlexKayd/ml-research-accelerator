import logging
from typing import List, Optional
from app.domain.interfaces import IDatasetRepository

logger = logging.getLogger(__name__)


class DatasetService:
    
    def __init__(self, dataset_repository: IDatasetRepository) -> None:
        self.dataset_repository = dataset_repository
    
    async def search_datasets(
        self,
        user_id: int,
        query: Optional[str] = None,
        sources: Optional[List[str]] = None,
        file_formats: Optional[List[str]] = None,
        max_size_mb: Optional[float] = None,
        tags: Optional[List[str]] = None,
        limit: int = 20,
        offset: int = 0
    ) -> List[dict]:
        """Поиск датасетов по каталогу + data-файлы + наличие отчёта по файлу для пользователя"""
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
            "Запрос поиска датасетов: user_id=%s query=%r sources=%s file_formats=%s "
            "max_size_mb=%s tags=%s limit=%s offset=%s",
            user_id, query, sources, file_formats, max_size_mb, tags, limit, offset,
        )

        datasets = await self.dataset_repository.search_datasets_with_data_files_and_user_reports(
            user_id=user_id,
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

    async def get_non_data_files(self, dataset_id: int) -> dict:
        """Возвращает файлы датасета с is_data=false"""
        files = await self.dataset_repository.get_non_data_files_by_dataset_id(dataset_id)
        return {"dataset_id": dataset_id, "files": files}