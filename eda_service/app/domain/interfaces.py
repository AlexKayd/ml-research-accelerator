from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional, Tuple
from app.domain.entities import Report, FileInfo, DatasetInfo


class IReportRepository(ABC):

    @abstractmethod
    async def get_by_id(self, report_id: int) -> Optional[Report]:
        """Получает отчёт по внутреннему report_id"""
        pass

    @abstractmethod
    async def get_by_file_id(self, file_id: int) -> Optional[Report]:
        """Получает отчёт по file_id"""
        pass

    @abstractmethod
    async def create_processing_report_with_advisory_lock(self, file_id: int) -> Report:
        """Создаёт строку reports для file_id со статусом processing"""
        pass

    @abstractmethod
    async def lock_for_update(self, report_id: int) -> Report:
        """Возвращает Report под блокировкой FOR UPDATE"""
        pass

    @abstractmethod
    async def mark_processing(self, report_id: int, started_at: datetime) -> None:
        """Переводит отчёт в processing и выставляет processing_started_at"""
        pass

    @abstractmethod
    async def mark_failed_if_processing_started_at_matches(
        self,
        report_id: int,
        processing_started_at: datetime,
        error_message: str,
    ) -> bool:
        """CAS-обновление в failed при совпадении processing_started_at"""
        pass

    @abstractmethod
    async def mark_completed_if_processing_started_at_matches(
        self,
        report_id: int,
        processing_started_at: datetime,
        bucket_name: str,
        object_key: str,
        input_file_hash: str,
        completed_at: datetime,
    ) -> bool:
        """CAS-обновление в completed при совпадении processing_started_at"""
        pass

    @abstractmethod
    async def mark_deleting(self, report_id: int) -> None:
        """Переводит отчёт в статус deleting"""
        pass

    @abstractmethod
    async def delete_report_row(self, report_id: int) -> None:
        """Удаляет строку отчёта из БД"""
        pass


class IFilesRepository(ABC):

    @abstractmethod
    async def resolve_file_id(self, dataset_id: int, file_name: str) -> Optional[int]:
        """Находит file_id по (dataset_id, file_name) или возвращает None"""
        pass

    @abstractmethod
    async def get_file_info(self, file_id: int) -> Optional[FileInfo]:
        """Возвращает метаданные файла по file_id"""
        pass

    @abstractmethod
    async def get_dataset_info(self, dataset_id: int) -> Optional[DatasetInfo]:
        """Возвращает данные датасета по dataset_id"""
        pass

    @abstractmethod
    async def get_file_and_dataset_info(self, file_id: int) -> Optional[Tuple[FileInfo, DatasetInfo]]:
        """Возвращает пару (файл, датасет) по file_id"""
        pass


class IReportStorage(ABC):

    @property
    @abstractmethod
    def reports_bucket(self) -> str:
        """Имя bucket для HTML-отчётов в MinIO"""
        pass

    @abstractmethod
    async def upload_report_html(self, object_key: str, html_content: str) -> None:
        """Загружает HTML отчёта в хранилище"""
        pass

    @abstractmethod
    async def delete_report_object(self, object_key: str) -> None:
        """Удаляет объект отчёта из хранилища"""
        pass

    @abstractmethod
    def build_report_url(self, object_key: str) -> str:
        """Формирует публичный URL"""
        pass


class IUserServiceClient(ABC):

    @abstractmethod
    async def attach_report_to_user(self, user_id: int, report_id: int) -> None:
        """Вызывает POST /api/users/{user_id}/reports"""
        pass