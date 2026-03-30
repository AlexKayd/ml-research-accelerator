import asyncio
import logging
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.celery_config import celery_app
from app.core.config import get_settings
from app.repository.report_repository import ReportRepository

logger = logging.getLogger(__name__)


async def enqueue_generate_task_only(report_id: int) -> None:
    """Постановка задачи генерации отчёта в Celery"""
    settings = get_settings()
    await asyncio.to_thread(
        celery_app.send_task,
        "app.celery.tasks.generate_report_task",
        kwargs={"report_id": report_id},
        queue=settings.CELERY_GEN_QUEUE,
    )
    logger.info(
        "Поставлена generate_report_task (без повторного mark_processing): report_id=%s",
        report_id,
    )


async def mark_processing_and_enqueue_generate(
    session: AsyncSession,
    report_id: int,
) -> None:
    """Переводит отчёт в processing, коммитит, ставит generate_report_task в CELERY_GEN_QUEUE"""
    settings = get_settings()
    reports = ReportRepository(session)
    started_at = datetime.now()
    await reports.mark_processing(report_id=report_id, started_at=started_at)
    await session.commit()

    await asyncio.to_thread(
        celery_app.send_task,
        "app.celery.tasks.generate_report_task",
        kwargs={"report_id": report_id},
        queue=settings.CELERY_GEN_QUEUE,
    )
    logger.info("Поставлена generate_report_task: report_id=%s", report_id)