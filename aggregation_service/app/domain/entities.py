from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List
from app.domain.value_objects import SourceType, DatasetStatus, DatasetFormat
from app.domain.exceptions import InvalidDatasetError, InvalidFileError


@dataclass
class File:

    file_name: str
    file_size_kb: float
    is_data: bool = True
    file_hash: Optional[str] = None
    file_updated_at: Optional[datetime] = None
    file_id: Optional[int] = None
    
    def __post_init__(self):

        if not self.file_name or len(self.file_name.strip()) == 0:
            raise InvalidFileError("Имя файла не может быть пустым")
        
        if self.file_size_kb < 0:
            raise InvalidFileError(
                f"Размер файла не может быть отрицательным: {self.file_size_kb}",
                file_name=self.file_name
            )
        
        if not self.is_data:
            self.file_hash = None
        
        if self.file_updated_at is None:
            self.file_updated_at = datetime.now()
    
    def to_dict(self) -> dict:
        return {
            "file_id": self.file_id,
            "file_name": self.file_name,
            "file_size_kb": self.file_size_kb,
            "file_hash": self.file_hash,
            "is_data": self.is_data,
            "file_updated_at": self.file_updated_at.isoformat() if self.file_updated_at else None
        }


@dataclass
class Dataset:

    source: SourceType
    external_id: str
    title: str
    description: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    dataset_format: Optional[DatasetFormat] = None
    dataset_size_kb: float = 0.0
    status: DatasetStatus = field(default_factory=lambda: DatasetStatus.ACTIVE)
    download_url: Optional[str] = None
    repository_url: Optional[str] = None
    source_updated_at: Optional[datetime] = None
    files: List[File] = field(default_factory=list)
    dataset_id: Optional[int] = None
    
    def __post_init__(self):

        if isinstance(self.source, str):
            if not SourceType.is_valid(self.source):
                raise InvalidDatasetError(
                    f"Неподдерживаемый источник: {self.source}",
                    field_name="source"
                )
            self.source = SourceType(self.source)
        
        if not self.external_id or len(self.external_id.strip()) == 0:
            raise InvalidDatasetError(
                "Внешний ID не может быть пустым",
                field_name="external_id"
            )
        
        if not self.title or len(self.title.strip()) == 0:
            raise InvalidDatasetError(
                "Название датасета не может быть пустым",
                field_name="title"
            )
        
        if len(self.title) > 500:
            raise InvalidDatasetError(
                f"Название датасета не должно превышать 500 символов (текущая длина: {len(self.title)})",
                field_name="title"
            )
        
        if isinstance(self.status, str):
            if not DatasetStatus.is_valid(self.status):
                raise InvalidDatasetError(
                    f"Недопустимый статус: {self.status}",
                    field_name="status"
                )
            self.status = DatasetStatus(self.status)
        
        if self.dataset_format is not None and isinstance(self.dataset_format, str):
            if not DatasetFormat.is_valid(self.dataset_format):
                raise InvalidDatasetError(
                    f"Недопустимый формат: {self.dataset_format}",
                    field_name="dataset_format"
                )
            self.dataset_format = DatasetFormat(self.dataset_format)
        
        if self.dataset_size_kb < 0:
            raise InvalidDatasetError(
                f"Общий размер датасета не может быть отрицательным: {self.dataset_size_kb}",
                field_name="dataset_size_kb"
            )
    
    def add_file(self, file: File):
        """Добавляет файл в датасет"""
        self.files.append(file)
        self.dataset_size_kb = sum(f.file_size_kb for f in self.files)
    
    def mark_as_error(self):
        """Помечает датасет как ошибочный"""
        self.status = DatasetStatus.ERROR
    
    def mark_as_deleted(self):
        """Помечает датасет как удаленный"""
        self.status = DatasetStatus.DELETED
    
    def mark_as_active(self):
        """Помечает датасет как активный"""
        self.status = DatasetStatus.ACTIVE
    
    def to_dict(self) -> dict:
        return {
            "dataset_id": self.dataset_id,
            "source": self.source.value if isinstance(self.source, SourceType) else self.source,
            "external_id": self.external_id,
            "title": self.title,
            "description": self.description,
            "tags": self.tags,
            "dataset_format": self.dataset_format.value if self.dataset_format else None,
            "dataset_size_kb": self.dataset_size_kb,
            "status": self.status.value if isinstance(self.status, DatasetStatus) else self.status,
            "download_url": self.download_url,
            "repository_url": self.repository_url,
            "source_updated_at": self.source_updated_at.isoformat() if self.source_updated_at else None,
            "files_count": len(self.files)
        }


@dataclass
class AggregationResult:

    success: bool = True
    datasets_processed: int = 0
    datasets_added: int = 0
    datasets_skipped: int = 0
    datasets_failed: int = 0
    datasets_updated: int = 0
    files_processed: int = 0
    errors: List[str] = field(default_factory=list)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    def add_error(self, error_message: str):
        """Добавляет ошибку в список"""
        self.errors.append(error_message)
        self.success = False
    
    def mark_dataset_processed(
        self,
        added: bool = False,
        skipped: bool = False,
        failed: bool = False,
        updated: bool = False,
    ):
        """Отмечает обработку датасета"""
        self.datasets_processed += 1
        if added:
            self.datasets_added += 1
        if skipped:
            self.datasets_skipped += 1
        if failed:
            self.datasets_failed += 1
            self.success = False
        if updated:
            self.datasets_updated += 1

    def merge_from(self, other: "AggregationResult") -> None:
        """Суммирует счётчики"""
        self.datasets_processed += other.datasets_processed
        self.datasets_added += other.datasets_added
        self.datasets_skipped += other.datasets_skipped
        self.datasets_failed += other.datasets_failed
        self.datasets_updated += other.datasets_updated
        self.files_processed += other.files_processed
        self.errors.extend(other.errors)
        if not other.success:
            self.success = False
    
    def add_files_processed(self, count: int):
        """Добавляет количество обработанных файлов"""
        self.files_processed += count
    
    def get_summary(self, process_title: str = "Агрегация") -> str:
        """Возвращает краткую сводку операции агрегации"""
        return (f"{process_title} завершена: {'успешно' if self.success else 'с ошибками'}\n"
                f"  Обработано датасетов: {self.datasets_processed}\n"
                f"  Добавлено: {self.datasets_added}\n"
                f"  Пропущено: {self.datasets_skipped}\n"
                f"  С ошибками: {self.datasets_failed}\n"
                f"  Обработано файлов: {self.files_processed}\n"
                f"  Ошибок: {len(self.errors)}")

    def get_update_summary(self, process_title: str = "Проверка обновлений") -> str:
        """Сводка для проверки обновлений"""
        return (
            f"{process_title} завершена: {'успешно' if self.success else 'с ошибками'}\n"
            f"  Обработано датасетов: {self.datasets_processed}\n"
            f"  Обновлено: {self.datasets_updated}\n"
            f"  Пропущено: {self.datasets_skipped}\n"
            f"  С ошибками: {self.datasets_failed}\n"
            f"  Обработано файлов: {self.files_processed}\n"
            f"  Ошибок: {len(self.errors)}"
        )

    def to_dict(self) -> dict:
        return {
            "success": self.success,
            "datasets_processed": self.datasets_processed,
            "datasets_added": self.datasets_added,
            "datasets_skipped": self.datasets_skipped,
            "datasets_failed": self.datasets_failed,
            "datasets_updated": self.datasets_updated,
            "files_processed": self.files_processed,
            "errors": self.errors,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None
        }