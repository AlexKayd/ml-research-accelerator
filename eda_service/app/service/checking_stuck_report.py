from datetime import datetime, timedelta
from typing import List, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import get_settings
from app.repository.report_repository import ReportRepository


class CheckingStuckReport:

    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._settings = get_settings()
        self._reports = ReportRepository(session)

    async def detect_and_mark_stuck(self) -> Tuple[int, List[int]]:
        """Находит долго висящие processing отчёты и переводит их в failed"""
        stuck_after = int(self._settings.REPORT_STUCK_AFTER_MINUTES)
        threshold = datetime.now() - timedelta(minutes=stuck_after)
        count, ids = await self._reports.mark_stuck_processing_reports_failed(
            stuck_before=threshold,
            error_message="отчёт завис",
        )
        await self._session.commit()
        return count, ids