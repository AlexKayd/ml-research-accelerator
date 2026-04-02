import logging
from sqlalchemy import delete, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from app.domain.user import UserReport
from app.domain.interfaces import IUserReportRepository
from app.domain.exceptions import ReportAlreadyExistsError
from app.repository.models import UserReportORM

logger = logging.getLogger(__name__)


class UserReportRepository(IUserReportRepository):

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def add(self, user_id: int, report_id: int) -> UserReport:
        logger.info(
            "Сохранение отчёта в историю: user_id=%s, report_id=%s",
            user_id,
            report_id,
        )

        if await self.exists(user_id, report_id):
            logger.warning(
                "Отчёт уже в истории: user_id=%s, report_id=%s",
                user_id,
                report_id,
            )
            raise ReportAlreadyExistsError(user_id=user_id, report_id=report_id)

        row = UserReportORM(user_id=user_id, report_id=report_id)
        self.session.add(row)
        try:
            await self.session.flush()
        except IntegrityError as e:

            logger.warning(
                "Отчёт уже в истории (IntegrityError): user_id=%s report_id=%s",
                user_id,
                report_id,
            )
            raise ReportAlreadyExistsError(user_id=user_id, report_id=report_id) from e

        return UserReport(user_id=user_id, report_id=report_id)

    async def remove(self, user_id: int, report_id: int) -> bool:
        logger.info(
            "Удаление отчёта из истории: user_id=%s, report_id=%s",
            user_id,
            report_id,
        )

        if not await self.exists(user_id, report_id):
            return False

        await self.session.execute(
            delete(UserReportORM).where(
                UserReportORM.user_id == user_id,
                UserReportORM.report_id == report_id,
            )
        )
        await self.session.flush()
        return True

    async def exists(self, user_id: int, report_id: int) -> bool:
        """Проверяет существование отчёта в истории пользователя"""
        query = select(UserReportORM).where(
            UserReportORM.user_id == user_id,
            UserReportORM.report_id == report_id,
        )
        result = await self.session.execute(query)
        return result.scalars().first() is not None