import logging
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession,async_sessionmaker,create_async_engine
from app.core.config import settings
from app.repository.models import Base

logger = logging.getLogger(__name__)

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    pool_pre_ping=True,
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
)


async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    session = async_session_maker()
    try:
        logger.debug("Создана новая сессия бд")
        yield session
        await session.commit()
        logger.debug("Транзакция зафиксирована")
    except Exception as e:
        logger.error(f"Ошибка в сессии бд: {str(e)}")
        await session.rollback()
        raise
    finally:
        logger.debug("Сессия бд закрыта")
        await session.close()


async def init_db() -> None:
    logger.info("Инициализация бд...")

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    logger.info("Бд инициализирована")


async def close_db() -> None:
    logger.info("Закрытие подключения к бд...")
    await engine.dispose()
    logger.info("Подключение к бд закрыто")