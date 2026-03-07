import logging
from typing import Annotated, List, Optional
from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.service.dataset_service import DatasetService
from app.schemas.dataset_schemas import DatasetResponse
from app.repository.dataset_repository import DatasetRepository

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Датасеты"])


def get_dataset_service(session: AsyncSession = Depends(get_db)) -> DatasetService:
    dataset_repo = DatasetRepository(session)
    return DatasetService(dataset_repository=dataset_repo)


@router.get(
    "",
    response_model=List[DatasetResponse],
    status_code=status.HTTP_200_OK,
    summary="Поиск датасетов",
    description="Поиск датасетов по каталогу с полнотекстовым поиском и фильтрацией"
)
async def search_datasets(
    dataset_service: Annotated[DatasetService, Depends(get_dataset_service)],
    query: Annotated[
        Optional[str],
        Query(description="Поисковый запрос (полнотекстовый)")
    ] = None,
    sources: Annotated[
        Optional[List[str]],
        Query(description="Фильтр по источникам (kaggle, uci, huggingface)")
    ] = None,
    file_formats: Annotated[
        Optional[List[str]],
        Query(description="Фильтр по форматам (CSV, JSON)")
    ] = None,
    max_size_mb: Annotated[
        Optional[float],
        Query(description="Максимальный размер файла в Мб")
    ] = None,
    tags: Annotated[
        Optional[List[str]],
        Query(description="Фильтр по тегам")
    ] = None,
    limit: Annotated[
        int,
        Query(ge=1, le=100, description="Количество результатов")
    ] = 20,
    offset: Annotated[
        int,
        Query(ge=0, description="Смещение для пагинации")
    ] = 0,
) -> List[dict]:
    """Поиск датасетов по каталогу"""
    logger.info(f"Поиск датасетов: query={query}, limit={limit}")
    
    datasets = await dataset_service.search_datasets(
        query=query,
        sources=sources,
        file_formats=file_formats,
        max_size_mb=max_size_mb,
        tags=tags,
        limit=limit,
        offset=offset,
    )
    
    logger.info(f"Найдено датасетов: {len(datasets)}")
    return datasets