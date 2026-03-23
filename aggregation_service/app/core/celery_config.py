import logging
from celery import Celery
from app.core.config import settings
from app.core.logging import setup_logging
from app.celery.beat_schedule import get_beat_schedule

setup_logging()


logger = logging.getLogger(__name__)


def create_celery_app() -> Celery:
    beat_schedule = get_beat_schedule()
    
    celery_app = Celery(
        'aggregation_service',
        broker=settings.CELERY_BROKER_URL,
        backend=settings.CELERY_RESULT_BACKEND,
        include=['app.celery.tasks']
    )
    
    celery_app.conf.update(
        task_serializer='json',
        result_serializer='json',
        accept_content=['json'],
        
        timezone='UTC',
        enable_utc=True,
        
        task_track_started=True,
        task_send_sent_event=True,
        worker_send_task_events=True,
        
        task_time_limit=settings.CELERY_TASK_TIME_LIMIT,
        task_soft_time_limit=settings.CELERY_TASK_SOFT_TIME_LIMIT,
        
        task_acks_late=True,
        task_reject_on_worker_lost=True,
        
        worker_prefetch_multiplier=1,
        worker_max_tasks_per_child=1000,
        
        beat_schedule=beat_schedule,
        
        worker_hijack_root_logger=False,
        worker_redirect_stdouts=False,
    )
    
    logger.info("Celery приложение настроено")
    logger.info(f"  Broker: {settings.CELERY_BROKER_URL}")
    logger.info(f"  Backend: {settings.CELERY_RESULT_BACKEND}")
    logger.info(f"  Timezone: UTC")
    logger.info(f"  Периодических задач: {len(beat_schedule)}")
    
    for task_name, task_config in beat_schedule.items():
        schedule = task_config.get('schedule')
        if hasattr(schedule, 'days'):
            logger.info(f"    - {task_name}: каждые {schedule.days} дней")
    
    return celery_app


celery_app = create_celery_app()