from typing import Optional


class DomainException(Exception):

    def __init__(self, message: str, details: Optional[dict] = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}

    def to_dict(self) -> dict:
        return {
            "error_type": self.__class__.__name__,
            "message": self.message,
            "details": self.details
        }


class InvalidReportError(DomainException):
    """Исключение, возникающее при некорректных данных отчёта"""

    def __init__(self, message: str, field_name: Optional[str] = None):
        details = {"field_name": field_name} if field_name else {}
        super().__init__(message, details)


class InvalidEventError(DomainException):
    """Исключение, возникающее при некорректном событии из очереди
    Используется когда не хватает обязательных полей или значения невалидны"""

    def __init__(self, message: str, event_type: Optional[str] = None):
        details = {"event_type": event_type} if event_type else {}
        super().__init__(message, details)


class ReportNotFoundError(DomainException):
    """Исключение, возникающее когда отчёт не найден в бд"""

    def __init__(self, report_id: Optional[int] = None, file_id: Optional[int] = None):
        if report_id is not None:
            msg = f"Отчёт report_id={report_id} не найден"
            details = {"report_id": report_id}
        elif file_id is not None:
            msg = f"Отчёт для file_id={file_id} не найден"
            details = {"file_id": file_id}
        else:
            msg = "Отчёт не найден"
            details = {}
        super().__init__(msg, details)


class ReportDeletingError(DomainException):
    """Исключение, возникающее когда отчёт в процессе удаления
    Используется для ответа 410 пользователю"""

    def __init__(self, report_id: int):
        super().__init__(
            f"Отчёт report_id={report_id} удаляется и недоступен",
            {"report_id": report_id},
        )


class ReportGenerationError(DomainException):
    """Исключение, возникающее при ошибке генерации EDA-отчёта
    Используется при сбоях профилинга, парсинга или данных"""

    def __init__(self, report_id: int, reason: str):
        super().__init__(
            f"Не удалось сгенерировать отчёт report_id={report_id}: {reason}",
            {"report_id": report_id, "reason": reason},
        )


class DatasetArchiveDownloadError(DomainException):
    """Исключение, возникающее при ошибке скачивания архива датасета"""

    def __init__(self, dataset_id: int, download_url: str, reason: str):
        super().__init__(
            f"Не удалось скачать датасет dataset_id={dataset_id}: {reason}",
            {"dataset_id": dataset_id, "download_url": download_url, "reason": reason},
        )


class FileNotFoundInArchiveError(DomainException):
    """Исключение, возникающее когда файл не найден в распакованном архиве"""

    def __init__(self, dataset_id: int, file_name: str):
        super().__init__(
            f"Файл '{file_name}' не найден в архиве датасета dataset_id={dataset_id}",
            {"dataset_id": dataset_id, "file_name": file_name},
        )


class StorageError(DomainException):
    """Исключение, возникающее при ошибке работы с хранилищем MinIO"""

    def __init__(
        self,
        operation: str,
        bucket: Optional[str] = None,
        key: Optional[str] = None,
        reason: Optional[str] = None,
    ):
        details: dict = {"operation": operation}
        if bucket:
            details["bucket"] = bucket
        if key:
            details["object_key"] = key
        if reason:
            details["reason"] = reason
        msg = f"Ошибка хранилища MinIO при операции '{operation}'"
        if reason:
            msg = f"{msg}: {reason}"
        super().__init__(msg, details)


class UserServiceUnavailableError(DomainException):
    """Исключение, возникающее когда user_service временно недоступен
    Используется для сетевых ошибок"""

    def __init__(self, user_id: int, report_id: int, reason: str):
        super().__init__(
            f"user_service недоступен для привязки отчёта: {reason}",
            {"user_id": user_id, "report_id": report_id, "reason": reason},
        )


class UserServiceReportAttachFailedError(DomainException):
    """Исключение при отклонённой привязке отчёта в user_service"""

    def __init__(self, user_id: int, report_id: int, reason: str):
        super().__init__(
            f"Привязка отчёта к user_service отклонена: {reason}",
            {"user_id": user_id, "report_id": report_id, "reason": reason},
        )


class DatabaseError(DomainException):
    """Исключение, возникающее при ошибке работы с базой данных"""

    def __init__(self, message: str, operation: str):
        details = {
            "operation": operation
        }
        super().__init__(message, details)