import logging
from typing import Annotated, List
from fastapi import APIRouter, Depends, status, Path
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.security import get_current_user
from app.domain.user import User as DomainUser
from app.service.user_report_service import UserReportService
from app.schemas.user_report_schemas import UserReportListItemResponse
from app.repository.user_report_repository import UserReportRepository
from app.repository.report_repository import ReportRepository

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/reports", tags=["История отчётов"])


def get_report_service(session: AsyncSession = Depends(get_db)) -> UserReportService: 
    user_report_repo = UserReportRepository(session)
    report_repo = ReportRepository(session)

    return UserReportService(
        user_report_repository=user_report_repo,
        report_repository=report_repo,
    )


@router.get(
    "",
    response_model=List[UserReportListItemResponse],
    status_code=status.HTTP_200_OK,
    summary="Получить историю отчётов",
    description="Получить все отчёты в истории пользователя"
)
async def get_all_reports(
    current_user: Annotated[DomainUser, Depends(get_current_user)],
    report_service: Annotated[UserReportService, Depends(get_report_service)],
) -> List[dict]:
    """Получить историю отчётов"""
    logger.info(f"Получение истории отчётов: user_id={current_user.user_id}")
    
    reports = await report_service.get_all_reports_with_details(
        user_id=current_user.user_id
    )
    
    logger.info(f"Найдено отчётов: {len(reports)}")
    return reports


@router.delete(
    "/{report_id}",
    status_code=status.HTTP_200_OK,
    summary="Удалить отчёт",
    description="Удалить отчёт из истории пользователя"
)
async def remove_report(
    report_id: Annotated[int, Path(..., description="Идентификатор отчёта")],
    current_user: Annotated[DomainUser, Depends(get_current_user)],
    report_service: Annotated[UserReportService, Depends(get_report_service)],
) -> dict:
    """Удалить отчёт из истории"""
    
    await report_service.remove_from_history(
        user_id=current_user.user_id,
        report_id=report_id,
    )
    
    logger.info(f"Отчёт удалён из истории: report_id={report_id}")
    return {"message": "Отчёт успешно удалён из истории"}