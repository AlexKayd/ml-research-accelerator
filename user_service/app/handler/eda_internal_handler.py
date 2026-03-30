"""
Сервисные вызовы от eda_service: идемпотентная привязка отчёта к пользователю.

Контракт: POST /api/users/{user_id}/reports, тело {"report_id": int},
заголовок X-EDA-Internal-Token (совпадает с EDA_SERVICE_INTERNAL_TOKEN в обоих сервисах).
"""

import logging
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, Header, HTTPException, Path, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.database import get_db
from app.service.user_report_service import UserReportService
from app.repository.user_report_repository import UserReportRepository
from app.repository.report_repository import ReportRepository

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/users", tags=["EDA — внутренние вызовы"])


class AttachReportBody(BaseModel):
    report_id: int = Field(..., ge=1, description="Идентификатор отчёта в ml_platform.reports")


def get_report_service(session: AsyncSession = Depends(get_db)) -> UserReportService:
    return UserReportService(
        user_report_repository=UserReportRepository(session),
        report_repository=ReportRepository(session),
    )


async def verify_eda_internal_token(
    x_eda_internal_token: Annotated[Optional[str], Header()] = None,
) -> None:
    settings = get_settings()
    expected = (settings.EDA_SERVICE_INTERNAL_TOKEN or "").strip()
    if not expected:
        logger.error("EDA_SERVICE_INTERNAL_TOKEN не задан в user_service")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Внутренний эндпойнт EDA не настроен",
        )
    got = (x_eda_internal_token or "").strip()
    if got != expected:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недействительный токен",
        )


@router.post(
    "/{user_id}/reports",
    status_code=status.HTTP_200_OK,
    summary="Привязать отчёт к пользователю (EDA)",
    description="Идемпотентный вызов от eda_service после успешной генерации отчёта",
)
async def attach_report_from_eda(
    user_id: Annotated[int, Path(..., ge=1, description="Пользователь, для которого сохраняем отчёт")],
    body: AttachReportBody,
    _: Annotated[None, Depends(verify_eda_internal_token)],
    report_service: Annotated[UserReportService, Depends(get_report_service)],
) -> dict:
    await report_service.save_report_idempotent(
        user_id=user_id,
        report_id=body.report_id,
    )
    logger.info(
        "EDA: отчёт привязан к пользователю user_id=%s report_id=%s",
        user_id,
        body.report_id,
    )
    return {"message": "ok", "user_id": user_id, "report_id": body.report_id}
