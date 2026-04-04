from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict


class DatasetFileResponse(BaseModel):
    """Data-файл датасета с флагом наличия отчёта у пользователя"""

    model_config = ConfigDict(from_attributes=True)

    file_id: int = Field(
        ...,
        description="Идентификатор файла",
    )
    file_name: str = Field(
        ...,
        description="Имя файла",
    )
    file_size_kb: Optional[float] = Field(
        None,
        description="Размер файла, КБ",
    )
    file_updated_at: datetime = Field(
        ...,
        description="Дата обновления файла",
    )
    has_user_report: bool = Field(
        ...,
        description="Есть ли у пользователя отчёт в истории по этому файлу",
    )


class DatasetResponse(BaseModel):
    """Ответ API с полной информацией о датасете"""

    model_config = ConfigDict(from_attributes=True)

    dataset_id: int = Field(
        ...,
        description="Уникальный идентификатор датасета",
    )
    source: str = Field(
        ...,
        description="Источник данных (kaggle, uci)",
    )
    title: str = Field(
        ...,
        description="Название датасета",
    )
    description: Optional[str] = Field(
        None,
        description="Описание датасета",
    )
    tags: List[str] = Field(
        default_factory=list,
        description="Теги датасета",
    )
    dataset_format: Optional[str] = Field(
        None,
        description="Основной формат данных (csv, json)",
    )
    dataset_size_kb: Optional[float] = Field(
        None,
        description="Суммарный размер файлов датасета, КБ",
    )
    status: str = Field(
        ...,
        description="Статус датасета (active, error, deleted)",
    )
    download_url: Optional[str] = Field(
        None,
        description="Ссылка для скачивания",
    )
    repository_url: Optional[str] = Field(
        None,
        description="Ссылка на репозиторий",
    )


class DatasetWithFilesResponse(DatasetResponse):
    """Датасет с data-файлами и флагами наличия отчёта у пользователя"""

    model_config = ConfigDict(from_attributes=True)

    files: List[DatasetFileResponse] = Field(
        default_factory=list,
        description="Список файлов датасета, только is_data=true",
    )


class DatasetNonDataFileResponse(BaseModel):
    """Не-data файл датасета"""

    model_config = ConfigDict(from_attributes=True)

    file_id: int = Field(...,
    description="Идентификатор файла"
    )
    file_name: str = Field(
        ...,
        description="Имя файла",
    )
    file_size_kb: Optional[float] = Field(
        None,
        description="Размер файла, КБ",
    )
    file_updated_at: datetime = Field(
        ...,
        description="Дата последнего обновления файла",
    )


class DatasetNonDataFilesResponse(BaseModel):
    """Файлы с is_data=false"""

    model_config = ConfigDict(from_attributes=True)

    dataset_id: int = Field(
        ...,
        description="Идентификатор датасета",
    )
    files: List[DatasetNonDataFileResponse] = Field(
        default_factory=list,
        description="Файлы датасета, только is_data=false",
    )