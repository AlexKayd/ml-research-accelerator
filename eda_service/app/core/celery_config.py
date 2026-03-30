import logging
from celery import Celery
from app.celery.periodic import get_beat_schedule
from app.core.config import settings
from app.core.logging import setup_logging

setup_logging()

logger = logging.getLogger(__name__)


def create_celery_app() -> Celery:
    beat_schedule = get_beat_schedule()

    celery_app = Celery(
        "eda_service",
        broker=settings.CELERY_BROKER_URL,
        backend=settings.CELERY_RESULT_BACKEND,
        include=["app.celery.tasks"],
    )

    celery_app.conf.update(
        task_serializer="json",
        result_serializer="json",
        accept_content=["json"],
        timezone="UTC",
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
        worker_hijack_root_logger=False,
        worker_redirect_stdouts=False,
        beat_schedule=beat_schedule,
        task_default_queue=settings.CELERY_EDA_QUEUE,
        task_routes={
            "app.celery.tasks.generate_report_task": {"queue": settings.CELERY_GEN_QUEUE},
            "app.celery.tasks.regen_waiter_task": {"queue": settings.CELERY_WAITER_QUEUE},
            "eda_service.tasks.process_dataset_change": {"queue": settings.CELERY_EDA_QUEUE},
            "app.celery.tasks.delete_report_task": {"queue": settings.CELERY_EDA_QUEUE},
            "app.celery.tasks.detect_stuck_reports_task": {"queue": settings.CELERY_EDA_QUEUE},
            "app.celery.tasks.notify_user_service_report_ready_task": {
                "queue": settings.CELERY_EDA_QUEUE
            },
        },
    )

    logger.info("Celery приложение EDA настроено")
    logger.info("  Broker: %s", settings.CELERY_BROKER_URL)
    logger.info("  Backend: %s", settings.CELERY_RESULT_BACKEND)
    logger.info(
        "  Queues: eda=%s gen=%s waiter=%s",
        settings.CELERY_EDA_QUEUE,
        settings.CELERY_GEN_QUEUE,
        settings.CELERY_WAITER_QUEUE,
    )
    logger.info("  Периодических задач Beat: %s", len(beat_schedule))
    return celery_app


celery_app = create_celery_app()