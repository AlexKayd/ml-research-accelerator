from abc import ABC, abstractmethod
from typing import Optional, List
from datetime import datetime
from app.domain.entities import Dataset, File


class IDatasetRepository(ABC):
    
    @abstractmethod
    async def exists(self, source: str, external_id: str) -> bool:
        """Проверяет существование датасета в бд"""
        pass
    
    @abstractmethod
    async def get_by_id(self, dataset_id: int) -> Optional[Dataset]:
        """Получает датасет по внутреннему ID"""
        pass
    
    @abstractmethod
    async def get_active_datasets_by_source(
        self, 
        source: str, 
        limit: Optional[int] = None,
        offset: int = 0
    ) -> List[Dataset]:
        """Получает список активных датасетов для проверки обновлений"""
        pass
    
    @abstractmethod
    async def save_dataset(self, dataset: Dataset) -> int:
        """Сохраняет датасет в бд"""
        pass
    
    @abstractmethod
    async def save_dataset_with_files(self, dataset: Dataset) -> int:
        """Атомарно сохраняет датасет и все его файлы в одной транзакции"""
        pass
    
    @abstractmethod
    async def update_dataset(self, dataset: Dataset) -> bool:
        """Обновляет существующий датасет"""
        pass
    
    @abstractmethod
    async def update_dataset_status(
        self, 
        dataset_id: int, 
        status: str
    ) -> bool:
        """Обновляет статус датасета"""
        pass
    
    @abstractmethod
    async def update_source_updated_at(
        self,
        dataset_id: int,
        updated_at: Optional[datetime],
    ) -> bool:
        """Обновляет дату последнего обновления из источника"""
        pass
    
    @abstractmethod
    async def delete_file(
        self, 
        dataset_id: int, 
        file_name: str
    ) -> bool:
        """Удаляет файл из датасета"""
        pass
    
    @abstractmethod
    async def add_file(
        self, 
        dataset_id: int, 
        file: File
    ) -> bool:
        """Добавляет файл к существующему датасету"""
        pass
    
    @abstractmethod
    async def update_file(
        self, 
        dataset_id: int, 
        file: File
    ) -> bool:
        """Обновляет информацию о файле"""
        pass
    
    @abstractmethod
    async def get_files_by_dataset(
        self, 
        dataset_id: int
    ) -> List[File]:
        """Получает список всех файлов датасета"""
        pass
    
    @abstractmethod
    async def recalculate_dataset_size(
        self, 
        dataset_id: int
    ) -> float:
        """Пересчитывает общий размер датасета на основе файлов"""
        pass


class ISourceClient(ABC):
    
    @abstractmethod
    async def list_dataset_ids(
        self, 
        batch_size: Optional[int] = None
    ) -> List[str]:
        """Получает список внешних ID всех доступных датасетов"""
        pass
    
    @abstractmethod
    async def get_metadata(
        self, 
        external_id: str
    ) -> dict:
        """Получает метаданные датасета"""
        pass
    
    @abstractmethod
    async def get_files_list(
        self, 
        external_id: str
    ) -> List[dict]:
        """Получает список файлов датасета с их размерами
        Kaggle: все записи из dataset_list_files. UCI: все строки таблицы Dataset Files."""
        pass
    
    @abstractmethod
    async def download_dataset(
        self, 
        external_id: str, 
        target_dir: str
    ) -> str:
        """Скачивает датасет во временную директорию"""
        pass
    
    @abstractmethod
    async def check_dataset_exists(
        self, 
        external_id: str
    ) -> bool:
        """ Проверяет существование датасета в источнике"""
        pass
    
    @abstractmethod
    def get_repository_url(
        self, 
        external_id: str
    ) -> str:
        """Формирует URL страницы датасета в репозитории"""
        pass
    
    @abstractmethod
    def get_download_url(
        self, 
        external_id: str
    ) -> Optional[str]:
        """Формирует URL для скачивания датасета"""
        pass