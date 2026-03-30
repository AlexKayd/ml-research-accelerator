import logging
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Path, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.jwt_auth import get_current_user_id, verify_generate_rate_limit
from app.domain.exceptions import (
    DatabaseError,
    DatasetArchiveDownloadError,
    FileNotFoundInArchiveError,
    ReportDeletingError,
    ReportNotFoundError,
)
from app.schemas import GenerateReportRequest, GenerateReportResponseModel
from app.service.report_service import ReportService

logger = logging.getLogger(__name__)

router = APIRouter(tags=["EDA-отчеты"])


def get_report_service(session: AsyncSession = Depends(get_db)) -> ReportService:
    return ReportService(session=session)


@router.post(
    "/generate",
    response_model=GenerateReportResponseModel,
    status_code=status.HTTP_200_OK,
    summary="Запросить генерацию отчета",
    description="Body: file_id; пользователь из Bearer JWT. Лимит запросов на пользователя в минуту",
    dependencies=[Depends(verify_generate_rate_limit)],
)
async def generate_report(
    payload: GenerateReportRequest,
    report_service: Annotated[ReportService, Depends(get_report_service)],
    user_id: Annotated[int, Depends(get_current_user_id)],
) -> GenerateReportResponseModel:
    """Инициирует генерацию отчета или возвращает уже готовый результат"""
    try:
        result = await report_service.get_or_create_report(
            file_id=payload.file_id,
            user_id=user_id,
        )
        logger.info(
            "POST /reports/generate: file_id=%s user_id=%s -> report_id=%s status=%s",
            payload.file_id,
            user_id,
            result.report_id,
            result.status,
        )
        return GenerateReportResponseModel.model_validate(result)
    except ReportDeletingError as e:
        raise HTTPException(status_code=status.HTTP_410_GONE, detail=e.message) from e
    except FileNotFoundInArchiveError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=e.message) from e
    except DatasetArchiveDownloadError as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=e.message) from e
    except DatabaseError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=e.message) from e


@router.get(
    "/status/{report_id}",
    response_model=GenerateReportResponseModel,
    status_code=status.HTTP_200_OK,
    summary="Получить статус отчета",
    description="Требуется Bearer JWT",
)
async def get_report_status(
    report_id: Annotated[int, Path(..., ge=1, description="Идентификатор отчета")],
    report_service: Annotated[ReportService, Depends(get_report_service)],
    user_id: Annotated[int, Depends(get_current_user_id)],
) -> GenerateReportResponseModel:
    """Возвращает текущий статус отчета по report_id"""
    try:
        result = await report_service.get_report_status(
            report_id=report_id,
            user_id=user_id,
        )
        logger.info(
            "GET /reports/status/%s: status=%s",
            report_id,
            result.status,
        )
        return GenerateReportResponseModel.model_validate(result)
    except ReportNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message) from e
    except ReportDeletingError as e:
        raise HTTPException(status_code=status.HTTP_410_GONE, detail=e.message) from e
    except FileNotFoundInArchiveError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=e.message) from e
    except DatasetArchiveDownloadError as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=e.message) from e
    except DatabaseError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=e.message) from e