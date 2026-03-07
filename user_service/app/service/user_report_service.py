import logging
from app.domain.user import UserReport
from app.domain.interfaces import IUserReportRepository, IReportRepository
from app.domain.exceptions import ReportNotInHistoryError, ReportNotFoundError

logger = logging.getLogger(__name__)


class UserReportService:

    def __init__(
        self,
        user_report_repository: IUserReportRepository,
        report_repository: IReportRepository
    ) -> None:
        self.user_report_repository = user_report_repository
        self.report_repository = report_repository

    async def save_report(
        self,
        user_id: int,
        report_id: int
    ) -> UserReport:
        """Сохраняет отчёт в историю пользователя"""
        logger.info(f"Сохранение отчёта в историю: user_id={user_id}, report_id={report_id}")
        
        report_exists = await self.report_repository.exists(report_id)
        if not report_exists:
            logger.warning(f"Отчёт не найден для сохранения в историю: report_id={report_id}")
            raise ReportNotFoundError(report_id=report_id)
        
        user_report = await self.user_report_repository.add(user_id, report_id)
        
        logger.info(f"Отчёт сохранён в историю: user_id={user_id}, report_id={report_id}")
        return user_report

    async def remove_from_history(
        self,
        user_id: int,
        report_id: int
    ) -> None:
        """Удаляет отчёт из истории пользователя"""
        logger.info(f"Удаление отчёта из истории: user_id={user_id}, report_id={report_id}")
        
        removed = await self.user_report_repository.remove(user_id, report_id)
        
        if not removed:
            logger.warning(f"Связь для удаления не найдена: user_id={user_id}, report_id={report_id}")
            raise ReportNotInHistoryError(user_id=user_id, report_id=report_id)
        
        logger.info(f"Отчёт удалён из истории: user_id={user_id}, report_id={report_id}")

    async def get_all_reports_with_details(
        self,
        user_id: int
    ) -> list[dict]:
        """Получает все отчёты в истории пользователя с информацией (с preview)"""
        logger.debug(f"Получение истории отчётов с метаданными: user_id={user_id}")
        
        user_reports = await self.user_report_repository.get_all_by_user(user_id)
        
        if not user_reports:
            return []
        
        report_ids = [link.report_id for link in user_reports]
        reports_metadata = await self.report_repository.get_metadata_batch(report_ids)
        
        logger.debug(f"Найдено отчётов с метаданными: {len(reports_metadata)}")
        return reports_metadata

    async def is_in_history(
        self,
        user_id: int,
        report_id: int
    ) -> bool:
        """Проверяет, находится ли отчёт в истории пользователя"""
        logger.debug(f"Проверка истории отчётов: user_id={user_id}, report_id={report_id}")
        
        exists = await self.user_report_repository.exists(user_id, report_id)
        
        logger.debug(f"Отчёт {'в истории' if exists else 'не в истории'}: report_id={report_id}")
        return exists

    async def get_report_full_details(
        self,
        user_id: int,
        report_id: int
    ) -> dict:
        """Получает полную метаинформацию об одном отчёте пользователя."""
        logger.debug(
            f"Получение полной информации об отчёте: user_id={user_id}, report_id={report_id}"
        )
        
        in_history = await self.user_report_repository.exists(user_id, report_id)
        if not in_history:
            logger.warning(
                f"Попытка получить отчёт вне истории пользователя: "
                f"user_id={user_id}, report_id={report_id}"
            )
            raise ReportNotInHistoryError(user_id=user_id, report_id=report_id)
        
        metadata = await self.report_repository.get_full_metadata(report_id)
        if metadata is None:
            logger.warning(f"Отчёт не найден при запросе полной информации: report_id={report_id}")
            raise ReportNotFoundError(report_id=report_id)

        return metadata