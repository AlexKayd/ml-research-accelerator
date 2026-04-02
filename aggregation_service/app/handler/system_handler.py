import asyncio
import logging
from typing import Any, Dict
from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from sqlalchemy import func, select
from app.core.celery_config import celery_app
from app.core.config import settings
from app.core.database import get_db_session, health_check_db
from app.repository.models import DatasetORM

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/health", status_code=status.HTTP_200_OK)
async def health_check() -> JSONResponse:
    health_status: Dict[str, Any] = {
        "status": "healthy",
        "service": "aggregation_service",
        "version": settings.VERSION,
        "database": {"status": "unknown", "total_count": 0},
        "celery": {"status": "unknown", "broker": settings.CELERY_BROKER_URL},
        "sources": {
            "kaggle": {"enabled": True, "interval_days": settings.KAGGLE_UPDATE_INTERVAL_DAYS},
            "uci": {"enabled": True, "interval_days": settings.UCI_UPDATE_INTERVAL_DAYS},
        },
    }

    try:
        db_healthy = await health_check_db()

        async with get_db_session() as session:
            result = await session.execute(select(func.count(DatasetORM.dataset_id)))
            total_count = result.scalar() or 0

        health_status["database"] = {
            "status": "connected" if db_healthy else "disconnected",
            "total_count": total_count,
        }

        if not db_healthy:
            health_status["status"] = "unhealthy"

    except Exception as e:
        logger.error("Ошибка проверки БД: %s", e)
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
        logger.error("Ошибка проверки Celery: %s", e)
        health_status["celery"]["status"] = "error"
        health_status["celery"]["error"] = str(e)

    if health_status["database"]["status"] == "error":
        health_status["status"] = "unhealthy"

    status_code = (
        status.HTTP_200_OK
        if health_status["status"] == "healthy"
        else status.HTTP_503_SERVICE_UNAVAILABLE
    )

    return JSONResponse(status_code=status_code, content=health_status)


@router.get("/", status_code=status.HTTP_200_OK)
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
                "openapi": "/openapi.json",
            },
            "schedule": {
                "kaggle_update_interval_days": settings.KAGGLE_UPDATE_INTERVAL_DAYS,
                "uci_update_interval_days": settings.UCI_UPDATE_INTERVAL_DAYS,
                "startup_delay_minutes": settings.AGGREGATION_STARTUP_DELAY_MINUTES,
            },
            "status": "running",
        }
    )


@router.get("/ready", status_code=status.HTTP_200_OK)
async def readiness_check() -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "ready": True,
            "service": "aggregation_service",
            "message": "Сервис готов к работе",
        },
    )