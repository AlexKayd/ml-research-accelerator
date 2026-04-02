import logging
from typing import Annotated, List
from fastapi import APIRouter, Depends, status, Path
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.security import get_current_user
from app.domain.user import User as DomainUser
from app.service.favorite_service import FavoriteService
from app.schemas.favorite_schemas import FavoriteDatasetResponse
from app.schemas.common import MessageResponse
from app.repository.favorite_repository import FavoriteRepository
from app.repository.dataset_repository import DatasetRepository

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/favorites", tags=["Избранное"])


def get_favorite_service(session: AsyncSession = Depends(get_db)) -> FavoriteService:
    favorite_repo = FavoriteRepository(session)
    dataset_repo = DatasetRepository(session)
    
    return FavoriteService(
        favorite_repository=favorite_repo,
        dataset_repository=dataset_repo,
    )


@router.post(
    "/{dataset_id}",
    response_model=MessageResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Добавить датасет в избранное",
    description="Добавить датасет в избранное пользователя"
)
async def add_to_favorites(
    dataset_id: Annotated[int, Path(..., description="Идентификатор датасета")],
    current_user: Annotated[DomainUser, Depends(get_current_user)],
    favorite_service: Annotated[FavoriteService, Depends(get_favorite_service)],
) -> dict:
    """Добавить датасет в избранное"""
    await favorite_service.add_to_favorites(
        user_id=current_user.user_id,
        dataset_id=dataset_id,
    )
    
    logger.info(f"Датасет dataset_id={dataset_id} добавлен в избранное: user_id={current_user.user_id}")
    return {"message": "Датасет успешно добавлен в избранное"}


@router.get(
    "",
    response_model=List[FavoriteDatasetResponse],
    status_code=status.HTTP_200_OK,
    summary="Получить избранные датасеты",
    description=("Получить все избранные датасеты пользователя"),
)
async def get_all_favorites(
    current_user: Annotated[DomainUser, Depends(get_current_user)],
    favorite_service: Annotated[FavoriteService, Depends(get_favorite_service)],
) -> List[dict]:
    """Получить все избранные датасеты"""
    logger.info(f"Получение избранных: user_id={current_user.user_id}")
    
    favorites = await favorite_service.get_all_favorites_with_details(
        user_id=current_user.user_id
    )
    
    logger.info(f"Найдено избранных: {len(favorites)}")
    return favorites


@router.delete(
    "/{dataset_id}",
    status_code=status.HTTP_200_OK,
    summary="Удалить датасет из избранного",
    description="Удалить датасет из избранного пользователя"
)
async def remove_from_favorites(
    dataset_id: Annotated[int, Path(..., description="Идентификатор датасета")],
    current_user: Annotated[DomainUser, Depends(get_current_user)],
    favorite_service: Annotated[FavoriteService, Depends(get_favorite_service)],
) -> dict:
    """Удалить датасет из избранного"""
    
    await favorite_service.remove_from_favorites(
        user_id=current_user.user_id,
        dataset_id=dataset_id,
    )
    
    logger.info(f"Датасет dataset_id={dataset_id} удалён из избранного: user_id={current_user.user_id}")
    return {"message": "Датасет успешно удалён из избранного"}