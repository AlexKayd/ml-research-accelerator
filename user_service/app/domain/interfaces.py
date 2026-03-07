from abc import ABC, abstractmethod
from typing import Optional, List
from app.domain.user import User, FavoriteDataset, UserReport


class IUserRepository(ABC):

    @abstractmethod
    async def create(self, user: User) -> User:
        """Создаёт нового пользователя"""
        pass
    
    @abstractmethod
    async def get_by_id(self, user_id: int) -> Optional[User]:
        """Получает пользователя по айди"""
        pass
    
    @abstractmethod
    async def get_by_login(self, login: str) -> Optional[User]:
        """Получает пользователя по логину"""
        pass

    @abstractmethod
    async def exists_by_login(self, login: str) -> bool:
        """Проверяет существование пользователя с данным логином"""
        pass


class IDatasetRepository(ABC):
    
    @abstractmethod
    async def exists(self, dataset_id: int) -> bool:
        """Проверяет существование датасета по айди"""
        pass
    
    @abstractmethod
    async def get_metadata_batch(self, dataset_ids: List[int]) -> List[dict]:
        """Получает метаданные нескольких датасетов по айди"""
        pass
    
    @abstractmethod
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
        """Поиск датасетов с фильтрацией"""
        pass


class IReportRepository(ABC):
    
    @abstractmethod
    async def exists(self, report_id: int) -> bool:
        """Проверяет существование отчёта по айди"""
        pass
    
    @abstractmethod
    async def get_metadata_batch(self, report_ids: List[int]) -> List[dict]:
        """Получает метаданные нескольких отчётов по айди"""
        pass
    
    @abstractmethod
    async def get_full_metadata(self, report_id: int) -> Optional[dict]:
        """Получает полную метаинформацию по одному отчёту"""
        pass


class IUserReportRepository(ABC):
    
    @abstractmethod
    async def add(
        self, 
        user_id: int, 
        report_id: int
    ) -> UserReport:
        """Сохраняет отчёт в историю пользователя"""
        pass
    
    @abstractmethod
    async def remove(self, user_id: int, report_id: int) -> bool:
        """Удаляет отчёт из истории пользователя"""
        pass

    @abstractmethod
    async def get_all_by_user(self, user_id: int) -> List[UserReport]:
        """Получает все отчёты в истории пользователя"""
        pass
    
    @abstractmethod
    async def exists(self, user_id: int, report_id: int) -> bool:
        """Проверяет наличие отчёта в истории пользователя"""
        pass


class IFavoriteRepository(ABC):
    
    @abstractmethod
    async def add(
        self, 
        user_id: int, 
        dataset_id: int
    ) -> FavoriteDataset:
        """Добавляет датасет в избранное пользователя"""
        pass
    
    @abstractmethod
    async def remove(self, user_id: int, dataset_id: int) -> bool:
        """Удаляет датасет из избранного пользователя"""
        pass
    
    @abstractmethod
    async def get_all_by_user(self, user_id: int) -> list[FavoriteDataset]:
        """Получает все избранные датасеты пользователя"""
        pass
    
    @abstractmethod
    async def exists(self, user_id: int, dataset_id: int) -> bool:
        """Проверяет наличие датасета в избранном пользователя"""
        pass