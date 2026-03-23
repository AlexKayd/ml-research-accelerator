import logging
from typing import Optional, Dict, Any
from datetime import datetime
from celery import shared_task
import asyncio
from app.core.config import get_settings
from app.core.database import get_db_session
from app.repository.dataset_repository import DatasetRepository
from app.clients.kaggle_client import KaggleClient
from app.clients.uci_client import UCIClient
from app.service.aggregation_service import AggregationService
from app.service.update_service import UpdateService
from app.service.file_processor import FileProcessor
from app.service.eda_notifier import EDANotifier
from app.service.log_labels import format_source_log
from app.domain.entities import AggregationResult
from celery import current_app

logger = logging.getLogger(__name__)


def run_async_with_engine_cleanup(async_fn):
    """Запускает асинхронную функцию Celery-задачи"""
    async def _runner():
        try:
            return await async_fn()
        finally:
            from app.core.database import dispose_engine_pool_after_asyncio_run

            await dispose_engine_pool_after_asyncio_run()

    return asyncio.run(_runner())


async def _run_kaggle_update_async() -> Dict[str, Any]:
    """Асинхронная реализация проверки обновлений Kaggle"""
    await asyncio.sleep(0)
    client: Optional[KaggleClient] = None
    file_processor: Optional[FileProcessor] = None
    
    try:
        async with get_db_session() as session:
            repo = DatasetRepository(session)
            client = KaggleClient()
            file_processor = FileProcessor()
            eda_notifier = EDANotifier(celery_app=current_app)
            
            update_service = UpdateService(
                session=session,
                dataset_repository=repo,
                source_client=client,
                file_processor=file_processor,
                eda_notifier=eda_notifier,
                source='kaggle',
            )
            
            started_at = datetime.now()
            logger.info(
                "%sСтарт проверки обновлений (worker), started_at=%s",
                format_source_log("kaggle"),
                started_at.isoformat(),
            )
            
            result: AggregationResult = await update_service.run_updates()
            
            completed_at = datetime.now()
            duration = (completed_at - started_at).total_seconds()
            
            logger.info(
                "%sПроверка обновлений (worker) завершена за %.2f сек",
                format_source_log("kaggle"),
                duration,
            )
            
            return {
                'source': 'kaggle',
                'operation': 'update',
                'success': result.success,
                'datasets_processed': result.datasets_processed,
                'datasets_updated': result.datasets_updated,
                'datasets_skipped': result.datasets_skipped,
                'datasets_failed': result.datasets_failed,
                'files_processed': result.files_processed,
                'errors': result.errors,
                'started_at': started_at.isoformat(),
                'completed_at': completed_at.isoformat(),
                'duration_seconds': duration
            }
            
    except Exception as e:
        logger.error(
            "%sКритическая ошибка при обновлении: %s",
            format_source_log("kaggle"),
            e,
        )
        raise
        
    finally:
        if client:
            await client.close()
        
        if file_processor:
            await file_processor.cleanup_all_temp_directories()
        
        logger.debug("%sРесурсы проверки обновлений закрыты", format_source_log("kaggle"))


async def _run_kaggle_aggregation_async() -> Dict[str, Any]:
    """Асинхронная реализация первичной агрегации Kaggle"""
    await asyncio.sleep(0)
    client: Optional[KaggleClient] = None
    file_processor: Optional[FileProcessor] = None
    
    try:
        async with get_db_session() as session:
            repo = DatasetRepository(session)
            client = KaggleClient()
            file_processor = FileProcessor()
            
            aggregation_service = AggregationService(
                session=session,
                dataset_repository=repo,
                source_client=client,
                file_processor=file_processor,
                source='kaggle',
            )
            
            started_at = datetime.now()
            logger.info(
                "%sСтарт первичной агрегации (worker), started_at=%s",
                format_source_log("kaggle"),
                started_at.isoformat(),
            )
            
            result: AggregationResult = await aggregation_service.run_aggregation()
            
            completed_at = datetime.now()
            duration = (completed_at - started_at).total_seconds()
            
            logger.info(
                "%sПервичная агрегация (worker) завершена за %.2f сек",
                format_source_log("kaggle"),
                duration,
            )
            
            return {
                'source': 'kaggle',
                'operation': 'aggregation',
                'success': result.success,
                'datasets_processed': result.datasets_processed,
                'datasets_added': result.datasets_added,
                'datasets_updated': result.datasets_updated,
                'datasets_skipped': result.datasets_skipped,
                'datasets_failed': result.datasets_failed,
                'files_processed': result.files_processed,
                'errors': result.errors,
                'started_at': started_at.isoformat(),
                'completed_at': completed_at.isoformat(),
                'duration_seconds': duration
            }
            
    except Exception as e:
        logger.error(
            "%sКритическая ошибка при первичной агрегации: %s",
            format_source_log("kaggle"),
            e,
        )
        raise
        
    finally:
        if client:
            await client.close()
        
        if file_processor:
            await file_processor.cleanup_all_temp_directories()
        
        logger.debug("%sРесурсы первичной агрегации закрыты", format_source_log("kaggle"))


async def _run_uci_update_async() -> Dict[str, Any]:
    """Асинхронная реализация проверки обновлений UCI"""
    await asyncio.sleep(0)
    client: Optional[UCIClient] = None
    file_processor: Optional[FileProcessor] = None
    
    try:
        async with get_db_session() as session:
            settings = get_settings()
            repo = DatasetRepository(session)
            client = UCIClient(
                catalog_filter_python=settings.UCI_CATALOG_FILTER_PYTHON,
            )
            file_processor = FileProcessor()
            eda_notifier = EDANotifier(celery_app=current_app)
            
            update_service = UpdateService(
                session=session,
                dataset_repository=repo,
                source_client=client,
                file_processor=file_processor,
                eda_notifier=eda_notifier,
                source='uci',
                uci_skip_date_optimization=settings.UCI_SKIP_DATE_OPTIMIZATION,
            )
            
            started_at = datetime.now()
            logger.info(
                "%sСтарт проверки обновлений (worker), started_at=%s",
                format_source_log("uci"),
                started_at.isoformat(),
            )
            
            result: AggregationResult = await update_service.run_updates()
            
            completed_at = datetime.now()
            duration = (completed_at - started_at).total_seconds()
            
            logger.info(
                "%sПроверка обновлений (worker) завершена за %.2f сек",
                format_source_log("uci"),
                duration,
            )
            
            return {
                'source': 'uci',
                'operation': 'update',
                'success': result.success,
                'datasets_processed': result.datasets_processed,
                'datasets_updated': result.datasets_updated,
                'datasets_skipped': result.datasets_skipped,
                'datasets_failed': result.datasets_failed,
                'files_processed': result.files_processed,
                'errors': result.errors,
                'started_at': started_at.isoformat(),
                'completed_at': completed_at.isoformat(),
                'duration_seconds': duration
            }
            
    except Exception as e:
        logger.error(
            "%sКритическая ошибка при обновлении: %s",
            format_source_log("uci"),
            e,
        )
        raise
        
    finally:
        if client:
            await client.close()
        
        if file_processor:
            await file_processor.cleanup_all_temp_directories()
        
        logger.debug("%sРесурсы проверки обновлений закрыты", format_source_log("uci"))


async def _run_uci_aggregation_async() -> Dict[str, Any]:
    """Асинхронная реализация первичной агрегации UCI"""
    await asyncio.sleep(0)
    client: Optional[UCIClient] = None
    file_processor: Optional[FileProcessor] = None
    
    try:
        async with get_db_session() as session:
            settings = get_settings()
            repo = DatasetRepository(session)
            client = UCIClient(
                catalog_filter_python=settings.UCI_CATALOG_FILTER_PYTHON,
            )
            file_processor = FileProcessor()
            
            aggregation_service = AggregationService(
                session=session,
                dataset_repository=repo,
                source_client=client,
                file_processor=file_processor,
                source='uci',
            )
            
            started_at = datetime.now()
            logger.info(
                "%sСтарт первичной агрегации (worker), started_at=%s",
                format_source_log("uci"),
                started_at.isoformat(),
            )
            
            result: AggregationResult = await aggregation_service.run_aggregation()
            
            completed_at = datetime.now()
            duration = (completed_at - started_at).total_seconds()
            
            logger.info(
                "%sПервичная агрегация (worker) завершена за %.2f сек",
                format_source_log("uci"),
                duration,
            )
            
            return {
                'source': 'uci',
                'operation': 'aggregation',
                'success': result.success,
                'datasets_processed': result.datasets_processed,
                'datasets_added': result.datasets_added,
                'datasets_updated': result.datasets_updated,
                'datasets_skipped': result.datasets_skipped,
                'datasets_failed': result.datasets_failed,
                'files_processed': result.files_processed,
                'errors': result.errors,
                'started_at': started_at.isoformat(),
                'completed_at': completed_at.isoformat(),
                'duration_seconds': duration
            }
            
    except Exception as e:
        logger.error(
            "%sКритическая ошибка при первичной агрегации: %s",
            format_source_log("uci"),
            e,
        )
        raise
        
    finally:
        if client:
            await client.close()
        
        if file_processor:
            await file_processor.cleanup_all_temp_directories()
        
        logger.debug("%sРесурсы первичной агрегации закрыты", format_source_log("uci"))


@shared_task(bind=True, max_retries=3, acks_late=True)
def run_kaggle_update(self) -> Dict[str, Any]:
    """Запускает проверку обновлений для датасетов Kaggle"""
    
    logger.info(
        "%sCelery: начало задачи «проверка обновлений»",
        format_source_log("kaggle"),
    )
    
    try:
        result = run_async_with_engine_cleanup(_run_kaggle_update_async)
        return result

    except Exception as e:
        logger.error(
            "%sCelery: критическая ошибка задачи «проверка обновлений»: %s",
            format_source_log("kaggle"),
            e,
        )
        
        retry_delay = 60 * (2 ** self.request.retries)
        raise self.retry(exc=e, countdown=retry_delay)
        
    finally:
        logger.info(
            "%sCelery: конец задачи «проверка обновлений»",
            format_source_log("kaggle"),
        )


@shared_task(bind=True, max_retries=3, acks_late=True)
def run_kaggle_aggregation(self, previous_result=None) -> Dict[str, Any]:
    """Запускает первичную агрегацию новых датасетов Kaggle"""
    logger.info(
        "%sCelery: начало задачи «первичная агрегация»",
        format_source_log("kaggle"),
    )
    
    try:
        result = run_async_with_engine_cleanup(_run_kaggle_aggregation_async)
        return result

    except Exception as e:
        logger.error(
            "%sCelery: критическая ошибка задачи «первичная агрегация»: %s",
            format_source_log("kaggle"),
            e,
        )
        
        retry_delay = 60 * (2 ** self.request.retries)
        raise self.retry(exc=e, countdown=retry_delay)
        
    finally:
        logger.info(
            "%sCelery: конец задачи «первичная агрегация»",
            format_source_log("kaggle"),
        )


@shared_task(bind=True, max_retries=3, acks_late=True)
def run_uci_update(self) -> Dict[str, Any]:
    """Запускает проверку обновлений для датасетов UCI"""
    
    logger.info(
        "%sCelery: начало задачи «проверка обновлений»",
        format_source_log("uci"),
    )
    
    try:
        result = run_async_with_engine_cleanup(_run_uci_update_async)
        return result

    except Exception as e:
        logger.error(
            "%sCelery: критическая ошибка задачи «проверка обновлений»: %s",
            format_source_log("uci"),
            e,
        )
        
        retry_delay = 60 * (2 ** self.request.retries)
        raise self.retry(exc=e, countdown=retry_delay)
        
    finally:
        logger.info(
            "%sCelery: конец задачи «проверка обновлений»",
            format_source_log("uci"),
        )


@shared_task(bind=True, max_retries=3, acks_late=True)
def run_uci_aggregation(self, previous_result=None) -> Dict[str, Any]:
    """Запускает первичную агрегацию новых датасетов UCI"""
    logger.info(
        "%sCelery: начало задачи «первичная агрегация»",
        format_source_log("uci"),
    )
    
    try:
        result = run_async_with_engine_cleanup(_run_uci_aggregation_async)
        return result

    except Exception as e:
        logger.error(
            "%sCelery: критическая ошибка задачи «первичная агрегация»: %s",
            format_source_log("uci"),
            e,
        )
        
        retry_delay = 60 * (2 ** self.request.retries)
        raise self.retry(exc=e, countdown=retry_delay)
        
    finally:
        logger.info(
            "%sCelery: конец задачи «первичная агрегация»",
            format_source_log("uci"),
        )


@shared_task(bind=True, max_retries=0)
def run_kaggle_cycle(self) -> Dict[str, Any]:
    """Полный цикл Kaggle: Update -> Aggregate в одной задаче"""
    logger.info(
        "%sПолный цикл: проверка обновлений -> первичная агрегация",
        format_source_log("kaggle"),
    )

    update_result: Dict[str, Any] = {}
    try:
        update_result = run_async_with_engine_cleanup(_run_kaggle_update_async)
        logger.info(
            "%sФаза «проверка обновлений» завершена, success=%s",
            format_source_log("kaggle"),
            update_result.get("success"),
        )
    except Exception as e:
        logger.error(
            "%sФаза «проверка обновлений» с ошибкой - всё равно запускаем агрегацию: %s",
            format_source_log("kaggle"),
            e,
            exc_info=True,
        )
        update_result = {"success": False, "operation": "update", "error": str(e)}

    agg_result = run_async_with_engine_cleanup(_run_kaggle_aggregation_async)
    logger.info(
        "%sФаза «первичная агрегация» завершена, success=%s",
        format_source_log("kaggle"),
        agg_result.get("success"),
    )

    return {
        "source": "kaggle",
        "operation": "cycle",
        "status": "completed",
        "update": update_result,
        "aggregation": agg_result,
    }


@shared_task(bind=True, max_retries=0)
def run_uci_cycle(self) -> Dict[str, Any]:
    """Полный цикл UCI: Update -> Aggregate в одной задаче"""
    logger.info(
        "%sПолный цикл: проверка обновлений -> первичная агрегация",
        format_source_log("uci"),
    )

    update_result: Dict[str, Any] = {}
    try:
        update_result = run_async_with_engine_cleanup(_run_uci_update_async)
        logger.info(
            "%sФаза «проверка обновлений» завершена, success=%s",
            format_source_log("uci"),
            update_result.get("success"),
        )
    except Exception as e:
        logger.error(
            "%sФаза «проверка обновлений» с ошибкой - всё равно запускаем агрегацию: %s",
            format_source_log("uci"),
            e,
            exc_info=True,
        )
        update_result = {"success": False, "operation": "update", "error": str(e)}

    agg_result = run_async_with_engine_cleanup(_run_uci_aggregation_async)
    logger.info(
        "%sФаза «первичная агрегация» завершена, success=%s",
        format_source_log("uci"),
        agg_result.get("success"),
    )

    return {
        "source": "uci",
        "operation": "cycle",
        "status": "completed",
        "update": update_result,
        "aggregation": agg_result,
    }