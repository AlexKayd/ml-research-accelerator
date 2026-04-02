import logging
from sqlalchemy import delete, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from app.domain.user import FavoriteDataset
from app.domain.interfaces import IFavoriteRepository
from app.domain.exceptions import FavoriteAlreadyExistsError
from app.repository.models import FavoriteDatasetORM

logger = logging.getLogger(__name__)


class FavoriteRepository(IFavoriteRepository):
    
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
    
    async def add(
        self,
        user_id: int,
        dataset_id: int
    ) -> FavoriteDataset:
        """Добавляет датасет в избранное пользователя"""
        logger.info(f"Добавление в избранное: user_id={user_id}, dataset_id={dataset_id}")
        
        exists = await self.exists(user_id, dataset_id)
        if exists:
            logger.warning(f"Датасет уже в избранном: user_id={user_id}, dataset_id={dataset_id}")
            raise FavoriteAlreadyExistsError(user_id=user_id, dataset_id=dataset_id)
        
        favorite_orm = FavoriteDatasetORM(
            user_id=user_id,
            dataset_id=dataset_id
        )
        
        self.session.add(favorite_orm)
        try:
            await self.session.flush()
        except IntegrityError as e:

            logger.warning(
                "Датасет уже в избранном (IntegrityError): user_id=%s dataset_id=%s",
                user_id,
                dataset_id,
            )
            raise FavoriteAlreadyExistsError(user_id=user_id, dataset_id=dataset_id) from e
        
        logger.info(f"Датасет добавлен в избранное: user_id={user_id}, dataset_id={dataset_id}")
        return FavoriteDataset(
            user_id=user_id,
            dataset_id=dataset_id
        )
    
    async def remove(self, user_id: int, dataset_id: int) -> bool:
        """Удаляет датасет из избранного пользователя"""
        logger.info(f"Удаление из избранного: user_id={user_id}, dataset_id={dataset_id}")
        
        exists = await self.exists(user_id, dataset_id)
        if not exists:
            logger.warning(f"Связь не найдена для удаления: user_id={user_id}, dataset_id={dataset_id}")
            return False
        
        query = delete(FavoriteDatasetORM).where(
            FavoriteDatasetORM.user_id == user_id,
            FavoriteDatasetORM.dataset_id == dataset_id
        )
        
        await self.session.execute(query)
        await self.session.flush()
        
        logger.info(f"Датасет удалён из избранного: user_id={user_id}, dataset_id={dataset_id}")
        return True
    
    async def exists(self, user_id: int, dataset_id: int) -> bool:
        """Проверяет наличие датасета в избранном пользователя"""
        logger.debug(f"Проверка наличия датасета dataset_id={dataset_id} в избранном пользователя user_id={user_id}")
        
        query = select(FavoriteDatasetORM).where(
            FavoriteDatasetORM.user_id == user_id,
            FavoriteDatasetORM.dataset_id == dataset_id
        )
        result = await self.session.execute(query)
        favorite_orm = result.scalar_one_or_none()
        
        exists = favorite_orm is not None
        logger.debug(f"Датасет dataset_id={dataset_id} {'существует' if exists else 'не существует'} в избранном пользователя user_id={user_id}")
        return exists