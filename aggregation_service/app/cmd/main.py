import asyncio
import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import init_db, close_db, health_check_db
from app.core.celery_config import celery_app
from app.core.exceptions import register_exception_handlers
from app.core.logging import setup_logging
from app.celery.beat_schedule import get_startup_tasks
from app.router.api import api_router

logger = logging.getLogger(__name__)


async def schedule_startup_tasks() -> None:
    """Планирует задачи для запуска при старте приложения"""
    
    startup_delay_seconds = settings.AGGREGATION_STARTUP_DELAY_MINUTES * 60
    
    logger.info(f"Запуск задач через {startup_delay_seconds} сек ({startup_delay_seconds // 60} мин)")
    
    startup_tasks = get_startup_tasks()
    
    for task_name, countdown in startup_tasks:
        celery_app.send_task(
            task_name,
            countdown=startup_delay_seconds
        )
        
        logger.debug(f"Задача {task_name} запланирована через {startup_delay_seconds} сек")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Управление жизненным циклом приложения"""
    
    try:
        setup_logging()
        logger.debug("Логирование настроено")
    except Exception as e:
        logger.error(f"Ошибка настройки логирования: {e}", exc_info=True)
        raise
    
    logger.info("=" * 60)
    logger.info("ЗАПУСК aggregation_service...")
    logger.info("=" * 60)
    
    try:
        logger.debug("Инициализация базы данных...")
        await init_db()
        logger.info("База данных инициализирована")
        
        db_healthy = await health_check_db()
        if db_healthy:
            logger.info("Подключение к БД успешно проверено")
        else:
            logger.warning("Подключение к БД работает с ошибками")
        
        asyncio.create_task(schedule_startup_tasks())
        
        logger.debug("=" * 60)
        logger.debug("Aggregation Service готов к работе")
        logger.debug(f"  Health Check: http://localhost:{settings.API_PORT}/health")
        logger.debug(f"  Celery Broker: {settings.CELERY_BROKER_URL}")
        logger.debug(f"  Database: {settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}")
        logger.debug("=" * 60)
        
    except Exception as e:
        logger.error(f"Ошибка при старте приложения: {e}", exc_info=True)
        raise
    
    yield
    
    logger.info("=" * 60)
    logger.info("ОСТАНОВКА aggregation_service...")
    logger.info("=" * 60)
    
    try:
        await close_db()
        logger.info("Подключение к БД закрыто")
        
        logger.debug("Сервис остановлен корректно")
        
    except Exception as e:
        logger.error(f"Ошибка при остановке сервиса: {e}", exc_info=True)
    
    logger.info("=" * 80)


app = FastAPI(
    title="ML Research Accelerator - Aggregation Service",
    description="""Фоновый сервис для агрегации метаданных датасетов из Kaggle и UCI ML Repository""",
    version=settings.VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS_LIST,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)
register_exception_handlers(app)