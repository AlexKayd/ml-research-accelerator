from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, Any
from app.domain.exceptions import InvalidReportError, InvalidEventError
from app.domain.value_objects import ReportStatus, EDAEventType


def _normalize_hash(value: Optional[str]) -> Optional[str]:
    """Приводит хеш к нижнему регистру и убирает пробелы"""
    if value is None:
        return None
    v = value.strip().lower()
    return v or None


@dataclass
class Report:

    file_id: int
    status: ReportStatus = ReportStatus.PROCESSING

    report_id: Optional[int] = None
    bucket_name: Optional[str] = None
    object_key: Optional[str] = None
    input_file_hash: Optional[str] = None
    updated_at: Optional[datetime] = None
    processing_started_at: Optional[datetime] = None
    error_message: Optional[str] = None

    def __post_init__(self):

        if self.file_id <= 0:
            raise InvalidReportError("file_id должен быть положительным числом", "file_id")

        if isinstance(self.status, str):
            if not ReportStatus.is_valid(self.status):
                raise InvalidReportError(f"Недопустимый статус отчёта: {self.status}", "status")
            self.status = ReportStatus(self.status)

        self.input_file_hash = _normalize_hash(self.input_file_hash)

        if self.object_key is not None and len(self.object_key) > 512:
            raise InvalidReportError(
                f"object_key не должен превышать 512 символов (текущая длина: {len(self.object_key)})",
                "object_key",
            )

    @staticmethod
    def build_default_object_key(file_id: int) -> str:
        """Формирует ключ объекта отчёта в MinIO"""
        return f"reports/{file_id}/report.html"

    def mark_processing(self, started_at: Optional[datetime] = None) -> None:
        """Переводит отчёт в processing"""
        self.status = ReportStatus.PROCESSING
        self.processing_started_at = started_at or datetime.now()
        self.error_message = None

    def mark_completed(
        self,
        bucket_name: str,
        object_key: str,
        input_file_hash: str,
        completed_at: Optional[datetime] = None,
    ) -> None:
        """Переводит отчёт в completed"""
        if not bucket_name:
            raise InvalidReportError("bucket_name не может быть пустым", "bucket_name")
        if not object_key:
            raise InvalidReportError("object_key не может быть пустым", "object_key")
        if not input_file_hash:
            raise InvalidReportError("input_file_hash не может быть пустым", "input_file_hash")

        self.bucket_name = bucket_name
        self.object_key = object_key
        self.input_file_hash = _normalize_hash(input_file_hash)
        self.status = ReportStatus.COMPLETED
        self.updated_at = completed_at or datetime.now()
        self.error_message = None

    def mark_failed(self, error_message: str) -> None:
        """Переводит отчёт в failed с текстом ошибки"""
        self.status = ReportStatus.FAILED
        self.error_message = (error_message or "").strip() or "неизвестная ошибка"

    def mark_deleting(self) -> None:
        """Переводит отчёт в deleting"""
        self.status = ReportStatus.DELETING

    def to_dict(self) -> dict:
        return {
            "report_id": self.report_id,
            "file_id": self.file_id,
            "bucket_name": self.bucket_name,
            "object_key": self.object_key,
            "input_file_hash": self.input_file_hash,
            "status": self.status.value if isinstance(self.status, ReportStatus) else self.status,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "processing_started_at": (self.processing_started_at.isoformat() if self.processing_started_at else None),
            "error_message": self.error_message,
        }


@dataclass
class FileInfo:

    file_id: int
    dataset_id: int
    file_name: str
    is_data: bool = True
    file_hash: Optional[str] = None

    def __post_init__(self):

        if self.file_id <= 0:
            raise InvalidReportError("file_id должен быть положительным числом", "file_id")
        if self.dataset_id <= 0:
            raise InvalidReportError("dataset_id должен быть положительным числом", "dataset_id")
        if not self.file_name or not self.file_name.strip():
            raise InvalidReportError("file_name не может быть пустым", "file_name")
        self.file_hash = _normalize_hash(self.file_hash)


@dataclass
class DatasetInfo:

    dataset_id: int
    download_url: Optional[str] = None

    def __post_init__(self):

        if self.dataset_id <= 0:
            raise InvalidReportError("dataset_id должен быть положительным числом", "dataset_id")


@dataclass
class DatasetChangeEvent:

    event_type: EDAEventType
    dataset_id: int
    file_name: str

    file_id: Optional[int] = None
    file_hash: Optional[str] = None
    external_id: Optional[str] = None
    source: Optional[str] = None

    def __post_init__(self):

        if isinstance(self.event_type, str):
            if not EDAEventType.is_valid(self.event_type):
                raise InvalidEventError(
                    f"Недопустимый event_type: {self.event_type}", event_type=self.event_type
                )
            self.event_type = EDAEventType(self.event_type)

        if self.dataset_id <= 0:
            raise InvalidEventError("dataset_id должен быть положительным числом", self.event_type.value)
        if not self.file_name or not self.file_name.strip():
            raise InvalidEventError("file_name не может быть пустым", self.event_type.value)

        if self.file_id is not None and self.file_id <= 0:
            raise InvalidEventError("file_id должен быть положительным числом", self.event_type.value)

        self.file_hash = _normalize_hash(self.file_hash)

    @classmethod
    def from_kwargs(cls, kwargs: Dict[str, Any]) -> "DatasetChangeEvent":
        if not kwargs:
            raise InvalidEventError("Пустое сообщение события", None)
        return cls(
            event_type=kwargs.get("event_type"),
            dataset_id=int(kwargs.get("dataset_id") or 0),
            file_name=kwargs.get("file_name") or "",
            file_id=kwargs.get("file_id"),
            file_hash=kwargs.get("file_hash"),
            external_id=kwargs.get("external_id"),
            source=kwargs.get("source"),
        )