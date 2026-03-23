import logging
from typing import Dict, Any
from datetime import timedelta
from app.core.config import settings

logger = logging.getLogger(__name__)


def get_beat_schedule() -> Dict[str, Dict[str, Any]]:
    """Формирует расписание задач Celery Beat"""
    logger.debug("Формирование расписания Celery Beat")
    logger.debug(f"  Kaggle интервал: {settings.KAGGLE_UPDATE_INTERVAL_DAYS} дней")
    logger.debug(f"  UCI интервал: {settings.UCI_UPDATE_INTERVAL_DAYS} дней")
    
    beat_schedule = {
        'kaggle-weekly-cycle': {
            'task': 'app.celery.tasks.run_kaggle_cycle',
            'schedule': timedelta(days=settings.KAGGLE_UPDATE_INTERVAL_DAYS),
            'options': {
                'expires': 3600 * 24,
            },
            'args': (),
            'kwargs': {}
        },
        
        'uci-monthly-cycle': {
            'task': 'app.celery.tasks.run_uci_cycle',
            'schedule': timedelta(days=settings.UCI_UPDATE_INTERVAL_DAYS),
            'options': {
                'expires': 3600 * 24 * 7,
            },
            'args': (),
            'kwargs': {}
        },
    }
    
    logger.info("Расписание Celery Beat сформировано")
    logger.info(f"  Задачи: {len(beat_schedule)}")
    
    for task_name, task_config in beat_schedule.items():
        schedule = task_config.get('schedule')
        if isinstance(schedule, timedelta):
            logger.info(f"  - {task_name}: каждые {schedule.days} дней")
    
    return beat_schedule


def get_startup_tasks() -> list:
    """Возвращает список задач для запуска при старте приложения"""
    countdown = settings.AGGREGATION_STARTUP_DELAY_MINUTES * 60
    
    tasks = [
        ('app.celery.tasks.run_kaggle_cycle', countdown),
        ('app.celery.tasks.run_uci_cycle', countdown),
    ]
    
    logger.debug(f"Задачи старта: {len(tasks)} задач через {countdown} сек")
    
    return tasks