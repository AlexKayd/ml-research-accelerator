from enum import Enum


class SourceType(str, Enum):

    KAGGLE = "kaggle"
    UCI = "uci"
    
    @classmethod
    def choices(cls) -> list:
        """Возвращает список всех доступных источников"""
        return [source.value for source in cls]
    
    @classmethod
    def is_valid(cls, value: str) -> bool:
        """Проверяет, является ли значение допустимым источником"""
        return value in cls.choices()


class DatasetStatus(str, Enum):

    ACTIVE = "active"
    ERROR = "error"
    DELETED = "deleted"
    
    @classmethod
    def choices(cls) -> list:
        """Возвращает список всех доступных статусов"""
        return [status.value for status in cls]
    
    @classmethod
    def is_valid(cls, value: str) -> bool:
        """Проверяет, является ли значение допустимым статусом"""
        return value in cls.choices()
    
    def is_active(self) -> bool:
        """Проверяет, активен ли датасет"""
        return self == self.ACTIVE
    
    def is_error(self) -> bool:
        """Проверяет, находится ли датасет в состоянии ошибки"""
        return self == self.ERROR
    
    def is_deleted(self) -> bool:
        """Проверяет, удален ли датасет"""
        return self == self.DELETED


class DatasetFormat(str, Enum):

    CSV = "csv"
    JSON = "json"
    
    @classmethod
    def choices(cls) -> list:
        """Возвращает список всех доступных форматов"""
        return [fmt.value for fmt in cls]

    @classmethod
    def is_valid(cls, value: str) -> bool:
        """Проверяет, что строка - один из поддерживаемых форматов"""
        if value is None:
            return False
        return value in cls.choices()