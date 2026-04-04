from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class UserReportListItemResponse(BaseModel):
    """История отчётов пользователя (users_reports + метаданные отчёта/файла/датасета)"""

    model_config = ConfigDict(from_attributes=True)

    report_id: int = Field(
        ...,
        description="Идентификатор отчёта",
    )
    status: str = Field(
        ...,
        description="Статус отчёта (completed, failed, processing, deleting)",
    )
    updated_at: Optional[datetime] = Field(
        None,
        description="Дата обновления отчёта",
    )

    bucket_name: Optional[str] = Field(
        None,
        description="MinIO bucket",
    )
    object_key: Optional[str] = Field(
        None,
        description="MinIO object_key",
    )
    report_url: Optional[str] = Field(
        None,
        description="Публичный URL отчёта в MinIO ",
    )
    file_id: int = Field(
        ...,
        description="Идентификатор файла",
    )
    file_name: str = Field(
        ...,
        description="Имя файла",
    )
    dataset_id: int = Field(
        ...,
        description="Идентификатор датасета",
    )
    source: str = Field(
        ...,
        description="Источник датасета",
    )
    title: str = Field(
        ...,
        description="Название датасета",
    )
    repository_url: Optional[str] = Field(
        None,
        description="URL страницы датасета в репозитории",
    )
    dataset_status: str = Field(
        ...,
        description="Статус датасета (active, error, deleted)",
    )
    dataset_updated_at: Optional[datetime] = Field(
        None,
        description="Дата обновления датасета в источнике",
    )