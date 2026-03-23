from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict


class ReportPreview(BaseModel):
    """Превью (при появлении метаданных из EDA); в БД не хранится."""

    model_config = ConfigDict(from_attributes=True)

    total_rows: Optional[int] = Field(None, description="Количество строк")
    total_columns: Optional[int] = Field(None, description="Количество столбцов")
    missing_values: Optional[int] = Field(None, description="Пропуски")


class UserReportResponse(BaseModel):
    """Метаданные отчёта + датасета; тело отчёта — в MinIO (bucket/object_key)."""

    model_config = ConfigDict(from_attributes=True)

    report_id: int = Field(..., description="Идентификатор отчёта")
    file_id: int = Field(..., description="Файл датасета, для которого отчёт")
    bucket_name: str = Field(..., description="Бакет объектного хранилища")
    object_key: str = Field(..., description="Ключ объекта в хранилище")
    dataset_id: int = Field(..., description="Идентификатор датасета")
    status: str = Field(..., description="Статус отчёта (completed, failed)")
    updated_at: Optional[datetime] = Field(None, description="Обновление отчёта")
    title: str = Field(..., description="Название датасета")
    source: str = Field(..., description="Источник данных")
    description: Optional[str] = Field(None, description="Описание датасета")
    tags: Optional[List[str]] = Field(None, description="Теги")
    dataset_format: Optional[str] = Field(None, description="Формат данных датасета")
    dataset_size_kb: Optional[float] = Field(
        None,
        description="Суммарный размер файлов датасета, КБ",
    )
    download_url: Optional[str] = Field(None, description="Ссылка для скачивания")
    repository_url: Optional[str] = Field(None, description="Страница в репозитории")
    dataset_status: str = Field(
        ...,
        description="Статус датасета (active, error, deleted)",
    )
    preview: Optional[ReportPreview] = Field(None)


class ReportFullResponse(UserReportResponse):
    """Полный ответ; content подставляется сервисом загрузки из MinIO при необходимости."""

    model_config = ConfigDict(from_attributes=True)

    content: Optional[Dict[str, Any]] = Field(
        None,
        description="Содержимое EDA (если загружено из хранилища)",
    )
