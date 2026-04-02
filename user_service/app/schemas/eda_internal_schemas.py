from pydantic import BaseModel, Field


class AttachReportBody(BaseModel):
    """внутренний вызов eda_service"""

    report_id: int = Field(
        ...,
        ge=1,
        description="Идентификатор отчёта",
    )