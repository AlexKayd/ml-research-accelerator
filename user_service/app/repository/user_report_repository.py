import logging
from typing import List

from sqlalchemy import delete, select
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
        await self.session.flush()

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

    async def get_all_by_user(self, user_id: int) -> List[UserReport]:
        logger.debug("Список истории отчётов: user_id=%s", user_id)
        query = select(UserReportORM).where(UserReportORM.user_id == user_id)
        result = await self.session.execute(query)
        rows: List[UserReportORM] = result.scalars().all()
        return [
            UserReport(user_id=row.user_id, report_id=row.report_id) for row in rows
        ]

    async def exists(self, user_id: int, report_id: int) -> bool:
        query = select(UserReportORM).where(
            UserReportORM.user_id == user_id,
            UserReportORM.report_id == report_id,
        )
        result = await self.session.execute(query)
        return result.scalars().first() is not None
