from typing import Optional
from app.core.config import get_settings


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


class InvalidDatasetError(DomainException):
    """Исключение, возникающее при некорректных данных датасета
    Используется когда поля датасета не проходят валидацию"""
    
    def __init__(self, message: str, field_name: Optional[str] = None):
        details = {"field_name": field_name} if field_name else {}
        super().__init__(message, details)


class InvalidFileError(DomainException):
    """Исключение, возникающее при некорректных данных файла
    Используется когда поля файла не проходят валидацию"""
    
    def __init__(self, message: str, file_name: Optional[str] = None):
        details = {"file_name": file_name} if file_name else {}
        super().__init__(message, details)


class DatasetTooLargeError(DomainException):
    """Исключение, возникающее когда файл датасета превышает максимальный размер
    Используется при валидации датасетов перед скачиванием"""
    
    def __init__(
        self,
        file_name: str,
        file_size_kb: float,
        max_size_kb: Optional[float] = None,
    ):
        if max_size_kb is None:
            max_size_kb = float(get_settings().MAX_FILE_SIZE_KB)

        message = (f"Файл '{file_name}' превышает максимальный размер: "
                  f"{file_size_kb:.2f} КБ (максимум: {max_size_kb} КБ)")
        details = {
            "file_name": file_name,
            "file_size_kb": file_size_kb,
            "max_size_kb": max_size_kb
        }
        super().__init__(message, details)


class NoValidFilesError(DomainException):
    """Исключение, возникающее когда датасет не содержит подходящих файлов
    Используется когда в датасете нет ни одного CSV/JSON файла"""
    
    def __init__(self, external_id: str, source: str):
        message = (f"Датасет '{external_id}' из источника '{source}' "
                  f"не содержит файлов CSV/JSON")
        details = {
            "external_id": external_id,
            "source": source
        }
        super().__init__(message, details)


class SourceUnavailableError(DomainException):
    """Исключение, возникающее когда внешний источник недоступен"""
    
    def __init__(self, source: str, reason: str):
        message = f"Источник '{source}' недоступен: {reason}"
        details = {
            "source": source,
            "reason": reason
        }
        super().__init__(message, details)


class DatasetNotFoundError(DomainException):
    """Исключение, возникающее когда датасет не найден в источнике
    Используется когда API возвращает 404"""
    
    def __init__(self, external_id: str, source: str):
        message = f"Датасет '{external_id}' не найден в источнике '{source}'"
        details = {
            "external_id": external_id,
            "source": source
        }
        super().__init__(message, details)


class AggregationError(DomainException):
    """Исключение, возникающее при ошибке в процессе агрегации"""
    
    def __init__(self, message: str, source: Optional[str] = None, 
                 external_id: Optional[str] = None):
        details = {}
        if source:
            details["source"] = source
        if external_id:
            details["external_id"] = external_id
        
        super().__init__(message, details)


class DatabaseError(DomainException):
    """Исключение, возникающее при ошибке работы с базой данных"""
    
    def __init__(self, message: str, operation: str):
        details = {
            "operation": operation
        }
        super().__init__(message, details)


class HashCalculationError(DomainException):
    """Исключение, возникающее при ошибке вычисления хеша файла."""

    def __init__(self, file_name: str, reason: str):
        message = f"Не удалось вычислить хеш файла '{file_name}': {reason}"
        details = {
            "file_name": file_name,
            "reason": reason,
        }
        super().__init__(message, details)