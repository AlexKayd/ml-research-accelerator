import logging
from typing import AsyncGenerator
from contextlib import asynccontextmanager
from sqlalchemy import pool, text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from app.core.config import settings
from app.repository.models import Base

logger = logging.getLogger(__name__)


engine = create_async_engine(
    settings.DATABASE_URL,
    poolclass=pool.AsyncAdaptedQueuePool,
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
    pool_pre_ping=True,
    pool_recycle=3600,
    echo=settings.DEBUG,
    future=True,
)

async_session_factory = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)


@asynccontextmanager
async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    session = async_session_factory()
    
    try:
        logger.debug("Открыта новая сессия бд")
        yield session
        logger.debug("Сессия бд успешно завершена")
        
    except Exception:
        await session.rollback()
        logger.error("Ошибка в сессии бд, выполнен rollback", exc_info=True)
        raise
        
    finally:
        await session.close()
        logger.debug("Сессия бд закрыта")


async def init_db() -> None:
    logger.debug("Инициализация базы данных...")
    
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        logger.info("База данных инициализирована успешно")
        
    except Exception as e:
        logger.error(f"Ошибка инициализации базы данных: {e}", exc_info=True)
        raise


async def dispose_engine_pool_after_asyncio_run() -> None:
    try:
        await engine.dispose()
        logger.debug("Пул async engine сброшен после asyncio.run()")
    except Exception as e:
        logger.warning(
            "Не удалось сбросить пул async engine после задачи: %s",
            e,
            exc_info=True,
        )


async def close_db() -> None:
    logger.debug("Закрытие подключения к базе данных...")
    
    try:
        await engine.dispose()
        logger.info("Подключение к базе данных закрыто")
        
    except Exception as e:
        logger.error(f"Ошибка при закрытии подключения к бд: {e}", exc_info=True)
        raise


async def health_check_db() -> bool:
    try:
        async with get_db_session() as session:
            await session.execute(text("SELECT 1"))
        return True
        
    except Exception as e:
        logger.error(f"Health check бд не прошёл: {e}")
        return False