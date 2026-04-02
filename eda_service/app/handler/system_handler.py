import logging
from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from app.core.config import settings
from app.core.health import get_health_status

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/health", status_code=status.HTTP_200_OK)
async def health_check() -> JSONResponse:
    health_status = await get_health_status()
    status_code = (
        status.HTTP_200_OK
        if health_status.get("status") == "ok"
        else status.HTTP_503_SERVICE_UNAVAILABLE
    )
    return JSONResponse(status_code=status_code, content=health_status)


@router.get("/", status_code=status.HTTP_200_OK)
async def root() -> JSONResponse:
    return JSONResponse(
        content={
            "service": "eda_service",
            "version": settings.VERSION,
            "description": "Сервис генерации EDA-отчётов",
            "endpoints": {
                "health": "/health",
                "docs": "/docs",
                "redoc": "/redoc",
                "openapi": "/openapi.json",
                "api": "/api",
                "reports_sse": "/api/reports/events",
            },
            "status": "running",
        }
    )


@router.get("/ready", status_code=status.HTTP_200_OK)
async def readiness_check() -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"ready": True, "service": "eda_service", "message": "Сервис готов к работе"},
    )