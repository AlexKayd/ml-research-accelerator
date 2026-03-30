from dataclasses import dataclass
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


@dataclass
class GenerateReportResponse:
    """Ответ сервиса на запрос генерации или получения статуса отчёта"""

    report_id: int
    status: str
    report_url: Optional[str]
    error_message: Optional[str] = None


class GeneratedReportArtifact(BaseModel):
    """Результат генерации"""

    model_config = ConfigDict(from_attributes=True)

    html: str = Field(..., description="Содержимое HTML-отчёта")
    input_file_hash: str = Field(
        ...,
        description="SHA-256 содержимого входного файла",
    )
    bucket_name: str = Field(..., description="Имя bucket в MinIO")
    object_key: str = Field(..., description="Ключ объекта в MinIO")


class GenerateReportRequest(BaseModel):
    """Тело запроса POST /reports/generate"""

    model_config = ConfigDict(from_attributes=True)

    file_id: int = Field(
        ...,
        ge=1,
        description="Идентификатор файла из таблицы files",
    )


class GenerateReportResponseModel(BaseModel):
    """Ответ API"""

    model_config = ConfigDict(from_attributes=True)

    report_id: int = Field(..., description="Идентификатор отчёта")
    status: str = Field(..., description="Статус отчёта")
    report_url: Optional[str] = Field(None, description="URL готового отчёта")
    error_message: Optional[str] = Field(
        None,
        description="Сообщение об ошибке при статусе failed",
    )