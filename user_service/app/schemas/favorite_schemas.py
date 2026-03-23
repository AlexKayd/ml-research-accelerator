from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict


class FavoriteDatasetResponse(BaseModel):
    """Избранный датасет с метаданными (sql/ddl.sql)."""

    model_config = ConfigDict(from_attributes=True)

    dataset_id: int = Field(..., description="Идентификатор датасета")
    source: str = Field(..., description="Источник данных")
    title: str = Field(..., description="Название датасета")
    description: Optional[str] = Field(None, description="Описание")
    tags: List[str] = Field(default_factory=list, description="Теги")
    dataset_format: Optional[str] = Field(None, description="Формат данных (csv, json)")
    dataset_size_kb: Optional[float] = Field(
        None,
        description="Суммарный размер файлов, КБ",
    )
    download_url: Optional[str] = Field(None, description="Ссылка для скачивания")
    repository_url: Optional[str] = Field(None, description="Страница в репозитории")
    status: str = Field(..., description="Статус датасета")
