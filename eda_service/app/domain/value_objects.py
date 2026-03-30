from enum import Enum


class ReportStatus(str, Enum):

    COMPLETED = "completed"
    FAILED = "failed"
    PROCESSING = "processing"
    DELETING = "deleting"

    @classmethod
    def choices(cls) -> list:
        """Возвращает список всех допустимых статусов"""
        return [s.value for s in cls]

    @classmethod
    def is_valid(cls, value: str) -> bool:
        """Проверяет, является ли значение допустимым статусом отчёта"""
        if value is None:
            return False
        return value in cls.choices()

    def is_terminal(self) -> bool:
        """Проверяет, является ли статус конечным (completed или failed)"""
        return self in (self.COMPLETED, self.FAILED)


class EDAEventType(str, Enum):

    FILE_UPDATED = "file_updated"
    FILE_DELETED = "file_deleted"

    @classmethod
    def choices(cls) -> list:
        """Возвращает список всех типов событий EDA"""
        return [e.value for e in cls]

    @classmethod
    def is_valid(cls, value: str) -> bool:
        """Проверяет, является ли значение допустимым типом события"""
        if value is None:
            return False
        return value in cls.choices()