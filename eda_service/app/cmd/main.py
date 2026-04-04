import asyncio
import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import close_db, init_db
from app.core.exceptions import register_exception_handlers
from app.core.logging import setup_logging
from app.core.minio import get_minio_client
from app.handler.system_handler import router as system_router
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

    if settings.MINIO_REPORTS_BUCKET_ANONYMOUS_READ:
        try:
            await asyncio.to_thread(
                get_minio_client().ensure_reports_bucket_and_policy_sync,
            )
        except Exception as e:
            logger.warning(
                "MinIO при старте: бакет/политика не применены %s",
                e,
            )

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

app.include_router(system_router, tags=["System"])
app.include_router(api_router, prefix="/api")
register_exception_handlers(app)

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