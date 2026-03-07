from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict

class FavoriteDatasetResponse(BaseModel):
    """Ответ API с информацией об избранном датасете"""
    
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