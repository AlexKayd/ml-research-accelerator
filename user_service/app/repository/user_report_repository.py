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
    
    async def add(
        self,
        user_id: int,
        report_id: int
    ) -> UserReport:
        """Сохраняет отчёт в историю пользователя"""
        logger.info(f"Сохранение отчёта в историю: user_id={user_id}, report_id={report_id}")
        
        exists = await self.exists(user_id, report_id)
        if exists:
            logger.warning(f"Отчёт уже в истории: user_id={user_id}, report_id={report_id}")
            raise ReportAlreadyExistsError(user_id=user_id, report_id=report_id)
        
        user_report_orm = UserReportORM(
            user_id=user_id,
            report_id=report_id
        )
        
        self.session.add(user_report_orm)
        await self.session.flush()
        
        logger.info(f"Отчёт сохранён в историю: user_id={user_id}, report_id={report_id}")
        return UserReport(
            user_id=user_id,
            report_id=report_id
        )
    
    async def remove(self, user_id: int, report_id: int) -> bool:
        """Удаляет отчёт из истории пользователя"""
        logger.info(f"Удаление отчёта из истории: user_id={user_id}, report_id={report_id}")
        
        exists = await self.exists(user_id, report_id)
        if not exists:
            logger.warning(f"Связь не найдена для удаления: user_id={user_id}, report_id={report_id}")
            return False
        
        query = delete(UserReportORM).where(
            UserReportORM.user_id == user_id,
            UserReportORM.report_id == report_id
        )
        
        await self.session.execute(query)
        await self.session.flush()
        
        logger.info(f"Отчёт удалён из истории: user_id={user_id}, report_id={report_id}")
        return True
    
    async def get_all_by_user(self, user_id: int) -> List[UserReport]:
        """Получает все отчёты в истории пользователя"""
        logger.debug(f"Получение списка отчётов пользователя: user_id={user_id}")
        
        query = select(UserReportORM).where(UserReportORM.user_id == user_id)
        result = await self.session.execute(query)
        rows: List[UserReportORM] = result.scalars().all()
        
        links: List[UserReport] = [
            UserReport(user_id=row.user_id, report_id=row.report_id)
            for row in rows
        ]
        
        logger.debug(f"Найдено связей пользователь-отчёт: {len(links)}")
        return links
    
    async def exists(self, user_id: int, report_id: int) -> bool:
        """Проверяет наличие отчёта в истории пользователя"""
        logger.debug(f"Проверка наличия отчёта report_id={report_id} в истории пользователя user_id={user_id}")
        
        query = select(UserReportORM).where(
            UserReportORM.user_id == user_id,
            UserReportORM.report_id == report_id
        )
        result = await self.session.execute(query)
        user_report_orm = result.scalar_one_or_none()
        
        exists = user_report_orm is not None
        logger.debug(f"Отчет report_id={report_id} {'существует' if exists else 'не существует'} в истории пользователя user_id={user_id}")
        return exists