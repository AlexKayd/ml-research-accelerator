import logging
from datetime import timedelta
from typing import Any, Dict
from app.core.config import settings

logger = logging.getLogger(__name__)


def get_beat_schedule() -> Dict[str, Dict[str, Any]]:
    """Периодическая проверка зависших отчётов в статусе processing"""
    interval = timedelta(hours=int(settings.STUCK_REPORTS_BEAT_INTERVAL_HOURS))
    schedule = {
        "eda-detect-stuck-reports": {
            "task": "app.celery.tasks.detect_stuck_reports_task",
            "schedule": interval,
            "options": {"expires": 3600},
            "args": (),
            "kwargs": {},
        }
    }
    logger.debug(
        "Beat EDA: detect_stuck_reports_task каждые %s ч",
        settings.STUCK_REPORTS_BEAT_INTERVAL_HOURS,
    )
    return schedule