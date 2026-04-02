import logging
import uvicorn
from contextlib import asynccontextmanager
from typing import AsyncGenerator
from sqlalchemy import text
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.exceptions import register_exception_handlers
from app.core.config import settings
from app.core.database import init_db, close_db
from app.router.api import api_router
from app.core.database import engine


logging.basicConfig(
    level=logging.DEBUG if settings.DEBUG else logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)



@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
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


register_exception_handlers(app)


app.include_router(api_router, prefix="/api")

logger.info("API роутеры подключены (/api)")


@app.get(
    "/health",
    tags=["Health"],
    summary="Проверка работоспособности",
    description="Проверка работоспособности сервиса и подключения к БД"
)
async def health_check() -> dict:
    health_status = {
        "status": "healthy",
        "service": "user_service",
        "version": settings.VERSION,
        "database": "connected",
    }
    
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
            logger.debug("Проверка подключения к бд успешна")
    except Exception as e:
        logger.error(f"Ошибка подключения к бд: {str(e)}")
        health_status["status"] = "unhealthy"
        health_status["database"] = "disconnected"
        health_status["error"] = "Не удалось подключиться к бд"
    return health_status


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