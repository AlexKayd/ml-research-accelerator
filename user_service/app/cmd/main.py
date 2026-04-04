import logging
import uvicorn
from contextlib import asynccontextmanager
from typing import AsyncGenerator
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.exceptions import register_exception_handlers
from app.core.config import settings
from app.core.database import init_db, close_db
from app.router.api import api_router
from app.core.logging import setup_logging
from app.handler.system_handler import router as system_router

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    setup_logging()

    logger.info("=" * 60)
    logger.info("Запуск приложения user_service...")
    logger.info(f"Название проекта: {settings.PROJECT_NAME}")
    logger.info(f"Версия: {settings.VERSION}")
    logger.info(f"Режим отладки: {settings.DEBUG}")
    logger.info("=" * 60)
    
    if settings.DEBUG:
        try:
            await init_db()
            logger.info("Бд  инициализирована")
        except Exception as e:
            logger.error(f"Ошибка инициализации бд: {str(e)}")
            raise
    
    logger.info("user_service готов")
    logger.info("=" * 60)
    
    yield
    
    logger.info("Остановка user_service...")
    await close_db()
    logger.info("Подключение к базе данных закрыто")
    logger.info("user_service  остановлено")
    logger.info("=" * 60)


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="""
## User Service для ML Research Accelerator""",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS_LIST,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "Accept"],
    expose_headers=["X-Request-ID"],
    max_age=600,
)

logger.info(f"CORS настроен для origins: {settings.CORS_ORIGINS_LIST}")


app.include_router(system_router, tags=["System"])
app.include_router(api_router, prefix="/api")
register_exception_handlers(app)

if __name__ == "__main__":
    logger.info("Запуск сервера uvicorn...")
    
    uvicorn.run(
        "app.cmd.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG,
        log_level="debug" if settings.DEBUG else "info",
        workers=1,
    )