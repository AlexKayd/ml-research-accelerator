import logging
from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from sqlalchemy import text
from app.core.config import settings
from app.core.database import engine

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/health", status_code=status.HTTP_200_OK)
async def health_check() -> JSONResponse:
    health_status = {
        "status": "healthy",
        "service": "user_service",
        "version": settings.VERSION,
        "database": "connected",
    }

    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
    except Exception as e:
        logger.error("Ошибка подключения к БД: %s", e, exc_info=True)
        health_status["status"] = "unhealthy"
        health_status["database"] = "disconnected"
        health_status["error"] = "Не удалось подключиться к бд"

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
            "service": "user_service",
            "version": settings.VERSION,
            "description": "User Service для ML Research Accelerator",
            "endpoints": {
                "health": "/health",
                "docs": "/docs",
                "redoc": "/redoc",
                "openapi": "/openapi.json",
                "api": "/api",
            },
            "status": "running",
        }
    )


@router.get("/ready", status_code=status.HTTP_200_OK)
async def readiness_check() -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"ready": True, "service": "user_service", "message": "Сервис готов к работе"},
    )