import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator
from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.core.config import settings
from app.core.database import close_db, init_db
from app.core.health import get_health_status
from app.core.exceptions import register_exception_handlers
from app.core.logging import setup_logging
from app.router import api_router
import uvicorn

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:

    setup_logging()

    logger.info("=" * 60)
    logger.info("ЗАПУСК eda_service...")
    logger.info("=" * 60)

    if settings.DEBUG:
        try:
            await init_db()
            logger.info("База данных инициализирована (DEBUG)")
        except Exception as e:
            logger.error("Ошибка инициализации БД: %s", e, exc_info=True)
            raise

    logger.info("EDA Service готов к работе")
    logger.debug("  Health Check: http://localhost:%s/health", settings.API_PORT)
    logger.debug("  Celery Broker: %s", settings.CELERY_BROKER_URL)
    logger.debug(
        "  Database: %s:%s/%s",
        settings.POSTGRES_HOST,
        settings.POSTGRES_PORT,
        settings.POSTGRES_DB,
    )

    yield

    logger.info("=" * 60)
    logger.info("ОСТАНОВКА eda_service...")
    logger.info("=" * 60)
    try:
        await close_db()
        logger.info("Подключение к базе данных закрыто")
    except Exception as e:
        logger.error("Ошибка при закрытии БД: %s", e, exc_info=True)
    logger.info("=" * 80)

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Сервис генерации EDA-отчётов по файлам датасетов",
    version=settings.VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS_LIST,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api")
register_exception_handlers(app)


@app.get("/health", status_code=status.HTTP_200_OK)
async def health_check() -> JSONResponse:
    health_status = await get_health_status()
    status_code = (
        status.HTTP_200_OK
        if health_status.get("status") == "ok"
        else status.HTTP_503_SERVICE_UNAVAILABLE
    )
    return JSONResponse(status_code=status_code, content=health_status)


@app.get("/", status_code=status.HTTP_200_OK)
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


@app.get("/ready", status_code=status.HTTP_200_OK)
async def readiness_check() -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"ready": True, "service": "eda_service", "message": "Сервис готов к работе"},
    )


 


if __name__ == "__main__":
    logger.info("Запуск сервера uvicorn...")
    uvicorn.run(
        "app.cmd.main:app",
        host=settings.API_HOST,
        port=int(settings.API_PORT),
        reload=bool(settings.DEBUG),
        log_level="debug" if settings.DEBUG else "info",
        workers=1,
    )