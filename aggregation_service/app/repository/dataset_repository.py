import logging
from typing import Optional, List
from datetime import datetime
from sqlalchemy import select, delete, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from app.domain.interfaces import IDatasetRepository
from app.domain.entities import Dataset, File
from app.domain.value_objects import SourceType, DatasetStatus, DatasetFormat
from app.domain.exceptions import DatabaseError
from app.repository.models import DatasetORM, FileORM
from app.core.config import get_settings

logger = logging.getLogger(__name__)


class DatasetRepository(IDatasetRepository):

    
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
    
    async def exists(self, source: str, external_id: str) -> bool:
        """Проверяет существование датасета по источнику и внешнему ID"""
        logger.debug(f"Проверка существования датасета: source={source}, external_id={external_id}")
        
        query = select(DatasetORM.dataset_id).where(
            DatasetORM.source == source,
            DatasetORM.external_id == external_id
        )
        result = await self.session.execute(query)
        dataset_id_result = result.scalar_one_or_none()
        
        exists = dataset_id_result is not None
        logger.debug(f"Датасет {'существует' if exists else 'не существует'}: source={source}, external_id={external_id}")
        return exists

    
    async def get_by_id(self, dataset_id: int) -> Optional[Dataset]:
        """Получает датасет по внутреннему ID"""
        logger.debug(f"Получение датасета по ID: dataset_id={dataset_id}")
        
        query = select(DatasetORM).where(DatasetORM.dataset_id == dataset_id)
        result = await self.session.execute(query)
        dataset_orm = result.scalar_one_or_none()
        
        if dataset_orm is None:
            logger.debug(f"Датасет не найден: dataset_id={dataset_id}")
            return None
        
        dataset = self._orm_to_domain(dataset_orm)
        logger.debug(f"Датасет получен: dataset_id={dataset_id}, title={dataset.title}")
        return dataset
    
    async def get_active_datasets_by_source(
        self, 
        source: str, 
        limit: Optional[int] = None,
        offset: int = 0
    ) -> List[Dataset]:
        """Получает список активных датасетов для проверки обновлений"""
        eff_limit = (
            int(limit) if limit is not None else int(get_settings().UPDATE_BATCH_SIZE)
        )
        logger.debug(
            "Получение активных датасетов: source=%s, limit=%s, after_dataset_id=%s",
            source,
            eff_limit,
            offset,
        )

        query = select(DatasetORM).where(
            DatasetORM.source == source,
            DatasetORM.status == DatasetStatus.ACTIVE.value,
            DatasetORM.dataset_id > offset,
        )
        query = query.order_by(DatasetORM.dataset_id.asc())
        query = query.limit(eff_limit)
        
        result = await self.session.execute(query)
        datasets_orm = result.scalars().all()
        
        datasets = [self._orm_to_domain(ds) for ds in datasets_orm]
        logger.debug(f"Получено {len(datasets)} активных датасетов для источника {source}")
        return datasets
    
    async def save_dataset(self, dataset: Dataset) -> int:
        """Сохраняет датасет в бд"""
        logger.debug(f"Сохранение датасета: source={dataset.source}, external_id={dataset.external_id}")
        
        try:
            dataset_orm = self._domain_to_orm(dataset)
            self.session.add(dataset_orm)
            await self.session.flush()
            await self.session.refresh(dataset_orm)
            
            dataset_id = dataset_orm.dataset_id
            logger.debug(f"Датасет подготовлен к сохранению (flush): dataset_id={dataset_id}")
            return dataset_id
            
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при подготовке датасета к сохранению: {e}")
            raise DatabaseError(f"Не удалось подготовить датасет к сохранению: {e}", operation="save_dataset")
    
    async def save_dataset_with_files(self, dataset: Dataset) -> int:
        """Атомарно сохраняет датасет и все его файлы в одной транзакции"""
        logger.debug(f"Подготовка к сохранению датасета с файлами: source={dataset.source}, external_id={dataset.external_id}, файлов={len(dataset.files)}")
        
        try:
            dataset_orm = self._domain_to_orm(dataset)
            self.session.add(dataset_orm)
            await self.session.flush()
            await self.session.refresh(dataset_orm)
            
            dataset_id = dataset_orm.dataset_id
            
            for file in dataset.files:
                file_orm = self._file_domain_to_orm(file, dataset_id)
                self.session.add(file_orm)
            
            await self.session.flush()
            
            logger.debug(f"Датасет с файлами подготовлен к сохранению (flush): dataset_id={dataset_id}, файлов={len(dataset.files)}")
            return dataset_id
            
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при подготовке датасета с файлами: {e}")
            raise DatabaseError(f"Не удалось подготовить датасет с файлами: {e}", operation="save_dataset_with_files")
    
    async def update_dataset(self, dataset: Dataset) -> bool:
        """Обновляет существующий датасет"""
        logger.debug(f"Обновление датасета: dataset_id={dataset.dataset_id}")
        
        try:
            query = select(DatasetORM).where(
                DatasetORM.dataset_id == dataset.dataset_id
            )
            result = await self.session.execute(query)
            dataset_orm = result.scalar_one_or_none()
            
            if dataset_orm is None:
                logger.warning(f"Датасет не найден для обновления: dataset_id={dataset.dataset_id}")
                return False
            
            dataset_orm.title = dataset.title
            dataset_orm.description = dataset.description
            dataset_orm.tags = dataset.tags
            dataset_orm.dataset_format = dataset.dataset_format.value if dataset.dataset_format else None
            dataset_orm.dataset_size_kb = dataset.dataset_size_kb
            dataset_orm.status = dataset.status.value if isinstance(dataset.status, DatasetStatus) else dataset.status
            dataset_orm.download_url = dataset.download_url
            dataset_orm.repository_url = dataset.repository_url
            dataset_orm.source_updated_at = dataset.source_updated_at
            
            await self.session.flush()
            logger.debug(f"Датасет подготовлен к обновлению (flush): dataset_id={dataset.dataset_id}")
            return True
            
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при обновлении датасета: {e}")
            raise DatabaseError(f"Не удалось обновить датасет: {e}", operation="update_dataset")
    
    async def update_dataset_status(
        self, 
        dataset_id: int, 
        status: str
    ) -> bool:
        """Обновляет статус датасета"""
        logger.debug(f"Обновление статуса датасета: dataset_id={dataset_id}, status={status}")
        
        try:
            query = select(DatasetORM).where(DatasetORM.dataset_id == dataset_id)
            result = await self.session.execute(query)
            dataset_orm = result.scalar_one_or_none()
            
            if dataset_orm is None:
                logger.warning(f"Датасет не найден для обновления статуса: dataset_id={dataset_id}")
                return False
            
            dataset_orm.status = status
            await self.session.flush()
            
            logger.debug(f"Статус датасета подготовлен к обновлению (flush): dataset_id={dataset_id}, status={status}")
            return True
            
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при обновлении статуса датасета: {e}")
            raise DatabaseError(f"Не удалось обновить статус датасета: {e}", operation="update_dataset_status")
    
    async def update_source_updated_at(
        self, 
        dataset_id: int, 
        updated_at: datetime
    ) -> bool:
        """Обновляет дату последнего обновления из источника"""
        logger.debug(f"Обновление source_updated_at: dataset_id={dataset_id}, updated_at={updated_at}")
        
        try:
            query = select(DatasetORM).where(DatasetORM.dataset_id == dataset_id)
            result = await self.session.execute(query)
            dataset_orm = result.scalar_one_or_none()
            
            if dataset_orm is None:
                logger.warning(f"Датасет не найден для обновления даты: dataset_id={dataset_id}")
                return False
            
            dataset_orm.source_updated_at = updated_at
            await self.session.flush()
            
            logger.debug(f"Дата обновления датасета подготовлена к обновлению (flush): dataset_id={dataset_id}")
            return True
            
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при обновлении даты датасета: {e}")
            raise DatabaseError(f"Не удалось обновить дату датасета: {e}", operation="update_source_updated_at")
    
    async def delete_file(
        self, 
        dataset_id: int, 
        file_name: str
    ) -> bool:
        """Удаляет файл из датасета"""
        logger.debug(f"Удаление файла: dataset_id={dataset_id}, file_name={file_name}")
        
        try:
            query = delete(FileORM).where(
                FileORM.dataset_id == dataset_id,
                FileORM.file_name == file_name
            )
            result = await self.session.execute(query)
            await self.session.flush()
            
            deleted_count = result.rowcount
            logger.debug(f"Файл подготовлен к удалению (flush): {deleted_count} записей")
            return deleted_count > 0
            
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при удалении файла: {e}")
            raise DatabaseError(f"Не удалось удалить файл: {e}", operation="delete_file")
    
    async def add_file(
        self, 
        dataset_id: int, 
        file: File
    ) -> bool:
        """Добавляет файл к существующему датасету"""
        logger.debug(f"Добавление файла: dataset_id={dataset_id}, file_name={file.file_name}")
        
        try:
            file_orm = self._file_domain_to_orm(file, dataset_id)
            self.session.add(file_orm)
            await self.session.flush()
            
            logger.debug(f"Файл подготовлен к добавлению (flush): dataset_id={dataset_id}, file_name={file.file_name}")
            return True
            
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при добавлении файла: {e}")
            raise DatabaseError(f"Не удалось добавить файл: {e}", operation="add_file")
    
    async def update_file(
        self, 
        dataset_id: int, 
        file: File
    ) -> bool:
        """Обновляет информацию о файле"""
        logger.debug(f"Обновление файла: dataset_id={dataset_id}, file_name={file.file_name}")
        
        try:
            query = select(FileORM).where(
                FileORM.dataset_id == dataset_id,
                FileORM.file_name == file.file_name
            )
            result = await self.session.execute(query)
            file_orm = result.scalar_one_or_none()
            
            if file_orm is None:
                logger.warning(f"Файл не найден для обновления: dataset_id={dataset_id}, file_name={file.file_name}")
                return False
            
            file_orm.file_size_kb = file.file_size_kb
            file_orm.file_hash = file.file_hash
            file_orm.is_data = file.is_data
            file_orm.file_updated_at = file.file_updated_at or func.current_timestamp()
            
            await self.session.flush()
            logger.debug(f"Файл подготовлен к обновлению (flush): dataset_id={dataset_id}, file_name={file.file_name}")
            return True
            
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при обновлении файла: {e}")
            raise DatabaseError(f"Не удалось обновить файл: {e}", operation="update_file")
    
    async def get_files_by_dataset(
        self, 
        dataset_id: int
    ) -> List[File]:
        """Получает список всех файлов датасета"""
        logger.debug(f"Получение файлов датасета: dataset_id={dataset_id}")
        
        query = select(FileORM).where(FileORM.dataset_id == dataset_id)
        result = await self.session.execute(query)
        files_orm = result.scalars().all()
        
        files = [self._file_orm_to_domain(f) for f in files_orm]
        logger.debug(f"Получено {len(files)} файлов для датасета {dataset_id}")
        return files
    
    async def recalculate_dataset_size(
        self, 
        dataset_id: int
    ) -> float:
        """Пересчитывает общий размер датасета на основе файлов"""
        logger.debug(f"Пересчёт размера датасета: dataset_id={dataset_id}")
        
        query = select(func.sum(FileORM.file_size_kb)).where(
            FileORM.dataset_id == dataset_id
        )
        result = await self.session.execute(query)
        total_size_kb = result.scalar() or 0.0
        
        update_query = select(DatasetORM).where(DatasetORM.dataset_id == dataset_id)
        update_result = await self.session.execute(update_query)
        dataset_orm = update_result.scalar_one_or_none()
        
        if dataset_orm:
            dataset_orm.dataset_size_kb = total_size_kb
            await self.session.flush()
        
        logger.debug(f"Размер датасета пересчитан (flush): dataset_id={dataset_id}, size_kb={total_size_kb}")
        return total_size_kb
    
    def _orm_to_domain(self, dataset_orm: DatasetORM) -> Dataset:
        source = SourceType(dataset_orm.source) if isinstance(dataset_orm.source, str) else dataset_orm.source
        status = DatasetStatus(dataset_orm.status) if isinstance(dataset_orm.status, str) else dataset_orm.status
        dataset_format = None
        if dataset_orm.dataset_format:
            dataset_format = DatasetFormat(dataset_orm.dataset_format) if isinstance(dataset_orm.dataset_format, str) else dataset_orm.dataset_format
        
        dataset = Dataset(
            dataset_id=dataset_orm.dataset_id,
            source=source,
            external_id=dataset_orm.external_id,
            title=dataset_orm.title,
            description=dataset_orm.description,
            tags=dataset_orm.tags or [],
            dataset_format=dataset_format,
            dataset_size_kb=float(dataset_orm.dataset_size_kb) if dataset_orm.dataset_size_kb else 0.0,
            status=status,
            download_url=dataset_orm.download_url,
            repository_url=dataset_orm.repository_url,
            source_updated_at=dataset_orm.source_updated_at
        )
        
        return dataset
    
    def _domain_to_orm(self, dataset: Dataset) -> DatasetORM:
        dataset_orm = DatasetORM(
            dataset_id=dataset.dataset_id,
            source=dataset.source.value if isinstance(dataset.source, SourceType) else dataset.source,
            external_id=dataset.external_id,
            title=dataset.title,
            description=dataset.description,
            tags=dataset.tags,
            dataset_format=dataset.dataset_format.value if dataset.dataset_format else None,
            dataset_size_kb=dataset.dataset_size_kb,
            status=dataset.status.value if isinstance(dataset.status, DatasetStatus) else dataset.status,
            download_url=dataset.download_url,
            repository_url=dataset.repository_url,
            source_updated_at=dataset.source_updated_at,
        )

        return dataset_orm

    def _file_domain_to_orm(self, file: File, dataset_id: int) -> FileORM:
        file_orm = FileORM(
            dataset_id=dataset_id,
            file_name=file.file_name,
            file_size_kb=file.file_size_kb,
            file_hash=file.file_hash,
            is_data=file.is_data,
            file_updated_at=file.file_updated_at or func.current_timestamp()
        )
        
        return file_orm
    
    def _file_orm_to_domain(self, file_orm: FileORM) -> File:
        file = File(
            file_name=file_orm.file_name,
            file_size_kb=float(file_orm.file_size_kb) if file_orm.file_size_kb else 0.0,
            is_data=file_orm.is_data,
            file_hash=file_orm.file_hash,
            file_updated_at=file_orm.file_updated_at
        )
        
        return file