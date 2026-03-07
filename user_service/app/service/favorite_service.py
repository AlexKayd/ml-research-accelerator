import logging
from typing import List
from app.domain.user import FavoriteDataset
from app.domain.interfaces import IFavoriteRepository, IDatasetRepository
from app.domain.exceptions import FavoriteNotFoundError, DatasetNotFoundError

logger = logging.getLogger(__name__)


class FavoriteService:
    
    def __init__(
        self,
        favorite_repository: IFavoriteRepository,
        dataset_repository: IDatasetRepository
    ) -> None:
        self.favorite_repository = favorite_repository
        self.dataset_repository = dataset_repository
    
    async def add_to_favorites(
        self,
        user_id: int,
        dataset_id: int
    ) -> FavoriteDataset:
        """Добавляет датасет в избранное пользователя"""
        logger.info(f"Добавление в избранное: user_id={user_id}, dataset_id={dataset_id}")
        
        dataset_exists = await self.dataset_repository.exists(dataset_id)
        if not dataset_exists:
            logger.warning(f"Датасет не найден для добавления в избранное: dataset_id={dataset_id}")
            raise DatasetNotFoundError(dataset_id=dataset_id)
        
        favorite = await self.favorite_repository.add(user_id, dataset_id)
        
        logger.info(f"Датасет добавлен в избранное: user_id={user_id}, dataset_id={dataset_id}")
        return favorite
    
    async def remove_from_favorites(
        self,
        user_id: int,
        dataset_id: int
    ) -> None:
        """Удаляет датасет из избранного пользователя"""
        logger.info(f"Удаление из избранного: user_id={user_id}, dataset_id={dataset_id}")
        
        removed = await self.favorite_repository.remove(user_id, dataset_id)
        
        if not removed:
            logger.warning(f"Связь не найдена для удаления: user_id={user_id}, dataset_id={dataset_id}")
            raise FavoriteNotFoundError(user_id=user_id, dataset_id=dataset_id)
        
        logger.info(f"Датасет удалён из избранного: user_id={user_id}, dataset_id={dataset_id}")
    

    async def get_all_favorites_with_details(
        self,
        user_id: int
    ) -> List[dict]:
        """Получает все избранные датасеты пользователя с полной метаинформацией"""
        logger.debug(f"Получение избранных с метаданными: user_id={user_id}")
        
        favorites = await self.favorite_repository.get_all_by_user(user_id)
        
        if not favorites:
            return []
        
        dataset_ids = [fav.dataset_id for fav in favorites]
        datasets_metadata = await self.dataset_repository.get_metadata_batch(dataset_ids)
        
        logger.debug(f"Найдено избранных датасетов с метаданными: {len(datasets_metadata)}")
        return datasets_metadata
    
    async def is_favorite(
        self,
        user_id: int,
        dataset_id: int
    ) -> bool:
        """Проверяет, находится ли датасет в избранном пользователя"""
        logger.debug(f"Проверка избранного: user_id={user_id}, dataset_id={dataset_id}")
        
        exists = await self.favorite_repository.exists(user_id, dataset_id)
        
        logger.debug(f"Датасет {'в избранном' if exists else 'не в избранном'}: dataset_id={dataset_id}")
        return exists