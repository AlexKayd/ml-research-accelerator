from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict


class ReportPreview(BaseModel):
    """Превью содержимого отчёта"""
    model_config = ConfigDict(from_attributes=True)
    
    total_rows: Optional[int] = Field(
        None,
        description="Количество строк в датасете"
    )
    total_columns: Optional[int] = Field(
        None,
        description="Количество столбцов"
    )
    missing_values: Optional[int] = Field(
        None,
        description="Количество пропущенных значений"
    )


class UserReportResponse(BaseModel):
    """Информация об отчёте в истории пользователя (метаданные отчёта + метаданные датасета + превью)"""
    model_config = ConfigDict(from_attributes=True)
    
    report_id: int = Field(
        ...,
        description="Уникальный идентификатор отчёта"
    )
    dataset_id: int = Field(
        ...,
        description="Уникальный идентификатор датасета"
    )
    status: str = Field(
        ...,
        description="Статус генерации отчёта"
    )
    title: str = Field(
        ...,
        description="Название датасета"
    )
    source: str = Field(
        ...,
        description="Источник данных (kaggle, uci, huggingface)"
    )
    description: Optional[str] = Field(
        None,
        description="Описание датасета"
    )
    tags: Optional[List[str]] = Field(
        None,
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
    dataset_status: str = Field(
        ...,
        description="Статус датасета (active или deleted)"
    )
    
    preview: Optional[ReportPreview] = Field(
        None
    )


class ReportFullResponse(UserReportResponse):
    """Полный ответ API с содержимым отчёта"""
    model_config = ConfigDict(from_attributes=True)
    
    content: Optional[Dict[str, Any]] = Field(
        None,
        description="Полное содержимое EDA-отчёта"
    )