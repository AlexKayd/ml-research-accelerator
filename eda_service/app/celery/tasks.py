import asyncio
import logging
import random
from datetime import datetime
from typing import Any, Dict
from celery import shared_task
from app.clients.user_service_client import UserServiceClient
from app.core.celery_config import celery_app
from app.core.config import get_settings
from app.core.database import dispose_engine_pool_after_asyncio_run, get_db_session
from app.domain.entities import DatasetChangeEvent
from app.domain.value_objects import ReportStatus
from app.domain.exceptions import (
    DatabaseError,
    FileNotFoundInArchiveError,
    ReportGenerationError,
    StorageError,
    UserServiceReportAttachFailedError,
    UserServiceUnavailableError,
)
from app.core.minio import get_minio_client
from app.repository.files_repository import FilesRepository
from app.repository.report_repository import ReportRepository
from app.service.aggregation_service import (
    AggregationEventService,
    DeleteReportService,
    RegenWaiterService,
)
from app.service.checking_stuck_report import CheckingStuckReport
from app.service.report_generator import ReportGenerator
from app.service.report_subscribers_redis import (
    pop_report_subscribers_sync,
    touch_user_report_attach_cooldown_sync,
)
from app.sse.sse_broker import publish_report_ready_sync
from app.sse.sse_broker import publish_report_failed_sync

logger = logging.getLogger(__name__)


def run_async_with_engine_cleanup(async_fn):

    async def _runner():
        try:
            return await async_fn()
        finally:
            await dispose_engine_pool_after_asyncio_run()

    return asyncio.run(_runner())


async def _process_dataset_change_async(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Обработка события от aggregation_service"""
    event = DatasetChangeEvent.from_kwargs(payload)
    async with get_db_session() as session:
        service = AggregationEventService(session)
        await service.process_event(event)
    return {
        "status": "ok",
        "event_type": event.event_type.value,
        "dataset_id": event.dataset_id,
        "file_name": event.file_name,
        "file_id": event.file_id,
        "received_at": datetime.now().isoformat(),
    }


async def _generate_report_async(report_id: int) -> Dict[str, Any]:
    """Генерация EDA-отчёта"""
    async with get_db_session() as session:
        reports = ReportRepository(session)
        files = FilesRepository(session)
        generator = ReportGenerator()
        settings = get_settings()

        report = await reports.lock_for_update(report_id)
        if str(report.status.value) == "completed":
            await session.commit()
            logger.info("generate_report_task: report_id=%s уже completed", report_id)
            return {"status": "skipped_completed", "report_id": report_id}
        if str(report.status.value) != "processing":
            await session.commit()
            logger.info(
                "generate_report_task: report_id=%s статус=%s, генерация не требуется",
                report_id,
                report.status.value,
            )
            return {"status": "skipped_status", "report_id": report_id, "report_status": report.status.value}

        processing_started_at = report.processing_started_at
        await session.commit()

        try:
            info = await files.get_file_and_dataset_info(report.file_id)
            if info is None:
                raise DatabaseError(
                    f"Не найден file/dataset для report_id={report_id} file_id={report.file_id}",
                    operation="get_file_and_dataset_info",
                )
            file_info, dataset_info = info

            artifact = await generator.generate(
                report=report,
                file_info=file_info,
                dataset_info=dataset_info,
            )

            completed_at = datetime.now()
            updated = await reports.mark_completed_if_processing_started_at_matches(
                report_id=report_id,
                processing_started_at=processing_started_at,
                bucket_name=artifact.bucket_name,
                object_key=artifact.object_key,
                input_file_hash=artifact.input_file_hash,
                completed_at=completed_at,
            )
            await session.commit()

            if not updated:
                logger.warning(
                    "generate_report_task: CAS completed не сработал, report_id=%s",
                    report_id,
                )
                return {"status": "stale_runner", "report_id": report_id}

            report_url = get_minio_client().build_report_url(artifact.object_key)

            subscribers = await asyncio.to_thread(pop_report_subscribers_sync, int(report_id))
            for uid in sorted(subscribers):
                await asyncio.to_thread(
                    touch_user_report_attach_cooldown_sync,
                    int(report_id),
                    int(uid),
                )
                await asyncio.to_thread(
                    publish_report_ready_sync,
                    int(uid),
                    int(report_id),
                    report_url,
                )
                await asyncio.to_thread(
                    celery_app.send_task,
                    "app.celery.tasks.notify_user_service_report_ready_task",
                    kwargs={"user_id": int(uid), "report_id": int(report_id)},
                    queue=settings.CELERY_NOTIFY_QUEUE,
                )
            if subscribers:
                logger.info(
                    "report_ready: report_id=%s user_ids=%s",
                    report_id,
                    sorted(subscribers),
                )

            return {
                "status": "completed",
                "report_id": report_id,
                "bucket_name": artifact.bucket_name,
                "object_key": artifact.object_key,
            }
        except (
            FileNotFoundInArchiveError,
            ReportGenerationError,
            DatabaseError,
            StorageError,
            Exception,
        ) as e:
            err_msg = str(e)
            updated = await reports.mark_failed_if_processing_started_at_matches(
                report_id=report_id,
                processing_started_at=processing_started_at,
                error_message=err_msg,
            )
            await session.commit()
            if not updated:
                logger.warning(
                    "generate_report_task: CAS failed не сработал, report_id=%s",
                    report_id,
                )
                return {"status": "stale_runner", "report_id": report_id}

            row = await reports.get_by_id(report_id)
            if (
                row is not None
                and row.status == ReportStatus.FAILED
                and row.processing_started_at == processing_started_at
            ):
                subscribers = await asyncio.to_thread(pop_report_subscribers_sync, int(report_id))
                for uid in sorted(subscribers):
                    await asyncio.to_thread(
                        publish_report_failed_sync,
                        int(uid),
                        int(report_id),
                        err_msg,
                    )
            else:
                logger.debug(
                    "Очистка подписчиков пропущена (состояние изменилось или новый processing): report_id=%s",
                    report_id,
                )
            if isinstance(e, ReportGenerationError):
                logger.error(
                    "generate_report_task: report_id=%s завершён failed: %s (reason=%s)",
                    report_id,
                    e.message,
                    e.details.get("reason"),
                )
            else:
                logger.error("generate_report_task: report_id=%s завершён failed: %s", report_id, e)
            return {"status": "failed", "report_id": report_id, "error": str(e)}


async def _regen_waiter_async(report_id: int) -> Dict[str, Any]:
    """Задача-ожидалка для отложенной перегенерации"""
    async with get_db_session() as session:
        service = RegenWaiterService(
            session,
            report_repository=ReportRepository(session),
        )
        await service.wait_and_regenerate(report_id)
    return {"status": "ok", "report_id": report_id}


async def _delete_report_async(report_id: int) -> Dict[str, Any]:
    """Удаление отчёта"""
    async with get_db_session() as session:
        service = DeleteReportService(session)
        await service.delete_report(report_id)
    return {"status": "ok", "report_id": report_id}


async def _detect_stuck_reports_async() -> Dict[str, Any]:
    async with get_db_session() as session:
        service = CheckingStuckReport(session)
        count, ids = await service.detect_and_mark_stuck()
        if ids:
            for rid in ids:
                subscribers = await asyncio.to_thread(pop_report_subscribers_sync, int(rid))
                for uid in sorted(subscribers):
                    await asyncio.to_thread(
                        publish_report_failed_sync,
                        int(uid),
                        int(rid),
                        "отчёт завис",
                    )
    return {"status": "ok", "count": count, "report_ids": ids, "checked_at": datetime.now().isoformat()}


@shared_task(
    bind=True,
    name="eda_service.tasks.process_dataset_change",
    max_retries=0,
    acks_late=True,
)
def process_dataset_change(self, **kwargs: Any) -> Dict[str, Any]:
    """Входная точка для событий от aggregation_service"""
    payload = dict(kwargs or {})
    logger.info("Получено событие от агрегации: %s", payload)
    return run_async_with_engine_cleanup(lambda: _process_dataset_change_async(payload))


@shared_task(
    bind=True,
    name="app.celery.tasks.generate_report_task",
    max_retries=0,
    acks_late=True,
)
def generate_report_task(self, report_id: int, **_kwargs: Any) -> Dict[str, Any]:
    """Генерация EDA-отчёта"""
    logger.info("Celery: старт generate_report_task report_id=%s", report_id)
    result = run_async_with_engine_cleanup(lambda: _generate_report_async(report_id))
    logger.info("Celery: конец generate_report_task report_id=%s status=%s", report_id, result.get("status"))
    return result


@shared_task(
    bind=True,
    name="app.celery.tasks.regen_waiter_task",
    max_retries=0,
    acks_late=True,
)
def regen_waiter_task(self, report_id: int) -> Dict[str, Any]:
    """Задача-ожидалка для отложенной перегенерации"""
    logger.info("Celery: старт regen_waiter_task report_id=%s", report_id)
    return run_async_with_engine_cleanup(lambda: _regen_waiter_async(report_id))


@shared_task(
    bind=True,
    name="app.celery.tasks.delete_report_task",
    max_retries=0,
    acks_late=True,
)
def delete_report_task(self, report_id: int) -> Dict[str, Any]:
    """Удаляет отчёт по сценарию file_deleted"""
    logger.info("Celery: старт delete_report_task report_id=%s", report_id)
    return run_async_with_engine_cleanup(lambda: _delete_report_async(report_id))


@shared_task(
    bind=True,
    name="app.celery.tasks.detect_stuck_reports_task",
    max_retries=0,
    acks_late=True,
)
def detect_stuck_reports_task(self) -> Dict[str, Any]:
    """Периодическая задача поиска зависших processing отчётов"""
    logger.info("Celery: старт detect_stuck_reports_task")
    return run_async_with_engine_cleanup(_detect_stuck_reports_async)


@shared_task(
    bind=True,
    name="app.celery.tasks.notify_user_service_report_ready_task",
    max_retries=10000,
    acks_late=True,
)
def notify_user_service_report_ready_task(self, user_id: int, report_id: int) -> Dict[str, Any]:
    """Привязка отчёта к пользователю в user_service"""
    s = get_settings()
    max_retries = int(s.USER_SERVICE_NOTIFY_MAX_RETRIES)

    try:
        client = UserServiceClient()
        client.attach_report_to_user_sync(user_id=user_id, report_id=report_id)
    except UserServiceReportAttachFailedError as e:
        logger.error(
            "Привязка отчёта к user_service без повторов: user_id=%s report_id=%s: %s",
            user_id,
            report_id,
            e,
        )
        raise
    except UserServiceUnavailableError as e:
        if self.request.retries >= max_retries:
            logger.error(
                "Уведомление user_service исчерпало попытки: user_id=%s report_id=%s retries=%s: %s",
                user_id,
                report_id,
                self.request.retries,
                e,
            )
            raise
        base = float(s.USER_SERVICE_NOTIFY_RETRY_BASE_DELAY_SECONDS)
        cap = float(s.USER_SERVICE_NOTIFY_RETRY_MAX_DELAY_SECONDS)
        delay = min(base * (2**self.request.retries), cap)
        delay = delay + random.uniform(0, min(delay * 0.1, 5.0))
        logger.warning(
            "user_service недоступен, retry через %.2fs: user_id=%s report_id=%s (%s)",
            delay,
            user_id,
            report_id,
            e,
        )
        raise self.retry(exc=e, countdown=delay)

    logger.info("user_service уведомлён: user_id=%s report_id=%s", user_id, report_id)
    return {"status": "ok", "user_id": user_id, "report_id": report_id}