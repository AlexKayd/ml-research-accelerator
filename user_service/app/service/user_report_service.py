import logging

from app.domain.user import UserReport
from app.domain.interfaces import IUserReportRepository, IReportRepository
from app.domain.exceptions import (
    ReportAlreadyExistsError,
    ReportNotInHistoryError,
    ReportNotFoundError,
)

logger = logging.getLogger(__name__)


class UserReportService:

    def __init__(
        self,
        user_report_repository: IUserReportRepository,
        report_repository: IReportRepository,
    ) -> None:
        self.user_report_repository = user_report_repository
        self.report_repository = report_repository

    async def save_report(self, user_id: int, report_id: int) -> UserReport:
        """
        Сохраняет отчёт в историю: в БД пишется (user_id, report_id).
        """
        logger.info(
            "Сохранение отчёта в историю: user_id=%s, report_id=%s",
            user_id,
            report_id,
        )

        if not await self.report_repository.exists(report_id):
            raise ReportNotFoundError(report_id=report_id)

        link = await self.user_report_repository.add(user_id, report_id)
        logger.info(
            "В истории: user_id=%s, report_id=%s",
            user_id,
            report_id,
        )
        return link

    async def save_report_idempotent(self, user_id: int, report_id: int) -> UserReport:
        """
        Сохраняет отчёт в историю; при уже существующей связи возвращает успех (идемпотентность для EDA).
        """
        try:
            return await self.save_report(user_id, report_id)
        except ReportAlreadyExistsError:
            logger.info(
                "Связь уже есть (идемпотентность): user_id=%s report_id=%s",
                user_id,
                report_id,
            )
            return UserReport(user_id=user_id, report_id=report_id)

    async def remove_from_history(self, user_id: int, report_id: int) -> None:
        logger.info(
            "Удаление из истории по report_id: user_id=%s, report_id=%s",
            user_id,
            report_id,
        )

        if not await self.report_repository.exists(report_id):
            raise ReportNotFoundError(report_id=report_id)

        removed = await self.user_report_repository.remove(user_id, report_id)
        if not removed:
            raise ReportNotInHistoryError(user_id=user_id, report_id=report_id)

    async def get_all_reports_with_details(self, user_id: int) -> list[dict]:
        logger.debug("История отчётов с метаданными: user_id=%s", user_id)
        return await self.report_repository.get_metadata_for_user_history(user_id)

    async def is_in_history(self, user_id: int, report_id: int) -> bool:
        if not await self.report_repository.exists(report_id):
            return False
        return await self.user_report_repository.exists(user_id, report_id)

    async def get_report_full_details(self, user_id: int, report_id: int) -> dict:
        logger.debug(
            "Полная информация об отчёте: user_id=%s, report_id=%s",
            user_id,
            report_id,
        )

        if not await self.is_in_history(user_id, report_id):
            raise ReportNotInHistoryError(user_id=user_id, report_id=report_id)

        metadata = await self.report_repository.get_full_metadata(report_id)
        if metadata is None:
            raise ReportNotFoundError(report_id=report_id)

        return metadata
