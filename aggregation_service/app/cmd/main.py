import asyncio
import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator
from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.core.config import settings
from app.core.database import get_db_session, init_db, close_db, health_check_db
from app.core.celery_config import celery_app
from app.core.logging import setup_logging
from app.celery.beat_schedule import get_startup_tasks
from app.repository.models import DatasetORM

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
    
    logger.info("=" * 60)
    logger.info("ЗАПУСК aggregation_service...")
    logger.info("=" * 60)
    
    try:
        setup_logging()
        logger.debug("Логирование настроено")
        
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


@app.get("/health", status_code=status.HTTP_200_OK)
async def health_check() -> JSONResponse:
    health_status = {
        "status": "healthy",
        "service": "aggregation_service",
        "version": settings.VERSION,
        "database": {
            "status": "unknown",
            "total_count": 0
        },
        "celery": {
            "status": "unknown",
            "broker": settings.CELERY_BROKER_URL
        },
        "sources": {
            "kaggle": {
                "enabled": True,
                "interval_days": settings.KAGGLE_UPDATE_INTERVAL_DAYS
            },
            "uci": {
                "enabled": True,
                "interval_days": settings.UCI_UPDATE_INTERVAL_DAYS
            }
        }
    }
    
    try:
        db_healthy = await health_check_db()
        
        async with get_db_session() as session:
            from sqlalchemy import select, func
            query = select(func.count(DatasetORM.dataset_id))
            result = await session.execute(query)
            total_count = result.scalar() or 0
        
        health_status["database"] = {
            "status": "connected" if db_healthy else "disconnected",
            "total_count": total_count
        }
        
        if not db_healthy:
            health_status["status"] = "unhealthy"
            
    except Exception as e:
        logger.error(f"Ошибка проверки БД: {e}")
        health_status["database"]["status"] = "error"
        health_status["database"]["error"] = str(e)
        health_status["status"] = "unhealthy"
    
    try:
        await asyncio.sleep(2)
        inspect = celery_app.control.inspect()
        ping_response = inspect.ping()
        
        if ping_response:
            health_status["celery"]["status"] = "connected"
            health_status["celery"]["workers"] = len(ping_response)
        else:
            health_status["celery"]["status"] = "no_workers"
            logger.warning("Celery воркеры не отвечают")
            
    except Exception as e:
        logger.error(f"Ошибка проверки Celery: {e}")
        health_status["celery"]["status"] = "error"
        health_status["celery"]["error"] = str(e)

    if health_status["database"]["status"] == "error":
        health_status["status"] = "unhealthy"
    
    status_code = (
        status.HTTP_200_OK if health_status["status"] == "healthy"
        else status.HTTP_503_SERVICE_UNAVAILABLE
    )
    
    return JSONResponse(status_code=status_code, content=health_status)


@app.get("/", status_code=status.HTTP_200_OK)
async def root() -> JSONResponse:
    return JSONResponse(
        content={
            "service": "aggregation_service",
            "version": settings.VERSION,
            "description": "Фоновый сервис для агрегации метаданных датасетов",
            "sources": ["Kaggle", "UCI ML Repository"],
            "endpoints": {
                "health": "/health",
                "docs": "/docs",
                "redoc": "/redoc",
                "openapi": "/openapi.json"
            },
            "schedule": {
                "kaggle_update_interval_days": settings.KAGGLE_UPDATE_INTERVAL_DAYS,
                "uci_update_interval_days": settings.UCI_UPDATE_INTERVAL_DAYS,
                "startup_delay_minutes": settings.AGGREGATION_STARTUP_DELAY_MINUTES
            },
            "status": "running"
        }
    )


@app.get("/ready", status_code=status.HTTP_200_OK)
async def readiness_check() -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "ready": True,
            "service": "aggregation_service",
            "message": "Сервис готов к работе"
        }
    )


@app.exception_handler(Exception)
async def global_exception_handler(request, exc: Exception) -> JSONResponse:
    logger.error(
        f"Непредвиденная ошибка: {exc}",
        exc_info=True,
        extra={"path": request.url.path, "method": request.method}
    )
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "status": "error",
            "code": "INTERNAL_ERROR",
            "message": "Внутренняя ошибка сервиса",
            "details": str(exc) if settings.DEBUG else None
        }
    )