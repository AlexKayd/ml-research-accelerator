from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict


class DatasetResponse(BaseModel):
    """Ответ API с полной информацией о датасете"""
    
    model_config = ConfigDict(from_attributes=True)
    
    dataset_id: int = Field(
        ...,
        description="Уникальный идентификатор датасета"
    )
    source: str = Field(
        ...,
        description="Источник данных (kaggle, uci, huggingface)"
    )
    title: str = Field(
        ...,
        description="Название датасета"
    )
    description: Optional[str] = Field(
        None,
        description="Описание датасета"
    )
    tags: List[str] = Field(
        default_factory=list,
        description="Теги датасета"
    )
    file_format: Optional[str] = Field(
        None,
        description="Формат файла (CSV, JSON)"
    )
    file_size_mb: Optional[float] = Field(
        None,
        description="Размер файла в Мб"
    )
    download_url: str = Field(
        ...,
        description="Ссылка для скачивания"
    )
    repository_url: Optional[str] = Field(
        None,
        description="Ссылка на репозиторий"
    )


class DatasetSearchRequest(BaseModel):
    """Запрос на поиск датасетов с фильтрацией"""
    
    model_config = ConfigDict(from_attributes=True)
    
    query: Optional[str] = Field(
        None,
        description="Поисковый запрос (полнотекстовый)"
    )
    sources: Optional[List[str]] = Field(
        None,
        description="Фильтр по источникам"
    )
    file_formats: Optional[List[str]] = Field(
        None,
        description="Фильтр по форматам"
    )
    max_size_mb: Optional[float] = Field(
        None,
        description="Максимальный размер в Мб"
    )
    tags: Optional[List[str]] = Field(
        None,
        description="Фильтр по тегам"
    )
    limit: int = Field(
        20,
        ge=1,
        le=100,
        description="Количество результатов"
    )
    offset: int = Field(
        0,
        ge=0,
        description="Смещение для пагинации"
    )