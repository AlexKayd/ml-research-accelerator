import os
import logging
from functools import lru_cache
from typing import List
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    
    PROJECT_NAME: str = Field(default="ML Research Aggregation Service")
    VERSION: str = Field(default="1.0.0")
    DEBUG: bool = Field(default=False)
    
    API_PORT: int = Field(default=8000, ge=1, le=65535)
    API_HOST: str = Field(default="0.0.0.0")
    
    POSTGRES_USER: str = Field(default="postgres")
    POSTGRES_PASSWORD: str = Field(default="", exclude=True)
    POSTGRES_HOST: str = Field(default="localhost")
    POSTGRES_PORT: int = Field(default=5432)
    POSTGRES_DB: str = Field(default="ml_platform")
    
    DB_POOL_SIZE: int = Field(default=10, ge=1, le=100)
    DB_MAX_OVERFLOW: int = Field(default=20, ge=0, le=100)
    
    @property
    def DATABASE_URL(self) -> str:
        return (
            f"postgresql+asyncpg://"
            f"{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@"
            f"{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/"
            f"{self.POSTGRES_DB}"
        )

    
    @field_validator('POSTGRES_PASSWORD')
    @classmethod
    def validate_password(cls, v: str) -> str:
        if not v and not os.getenv('CI'):
            logger.warning("POSTGRES_PASSWORD не установлен")
        return v
    
    HTTP_CLIENT_TIMEOUT_SECONDS: float = Field(
        default=120.0,
    )
    HTTP_CLIENT_MAX_RETRIES: int = Field(
        default=3,
    )
    HTTP_CLIENT_RETRY_DELAY_SECONDS: float = Field(
        default=1.0,
    )
    HTTP_CLIENT_RATE_LIMIT_DELAY_SECONDS: float = Field(
        default=0.5,
    )
    KAGGLE_HTTP_RATE_LIMIT_DELAY_SECONDS: float = Field(
        default=1.0,
    )
    KAGGLE_LIST_429_MAX_RETRIES: int = Field(
        default=10,
    )
    KAGGLE_CALL_429_MAX_RETRIES: int = Field(
        default=10,
    )
    CELERY_BROKER_URL: str = Field(
        default="redis://localhost:6379/1",
    )
    CELERY_RESULT_BACKEND: str = Field(
        default="redis://localhost:6379/1",
    )
    CELERY_TASK_TIME_LIMIT: int = Field(
        default=86400,
    )
    CELERY_TASK_SOFT_TIME_LIMIT: int = Field(
        default=84600,
    )
    CELERY_EDA_QUEUE: str = Field(
        default="eda",
    )
    AGGREGATION_STARTUP_DELAY_MINUTES: int = Field(
        default=5,
    )
    KAGGLE_UPDATE_INTERVAL_DAYS: int = Field(
        default=7,
    )
    UCI_UPDATE_INTERVAL_DAYS: int = Field(
        default=28,
    )
    UCI_CATALOG_FILTER_PYTHON: bool = Field(
        default=True,
    )
    UCI_SKIP_DATE_OPTIMIZATION: bool = Field(
        default=False,
    )
    KAGGLE_SKIP_DATE_OPTIMIZATION: bool = Field(
        default=False,
    )
    UCI_FORCE_HASH_RECALC_ON_SAME_SIZE: bool = Field(
        default=False,
    )
    KAGGLE_FORCE_HASH_RECALC_ON_SAME_SIZE: bool = Field(
        default=False,
    )
    AGGREGATION_BATCH_SIZE: int = Field(
        default=100,
    )
    UPDATE_BATCH_SIZE: int = Field(
        default=100,
    )
    MAX_FILE_SIZE_KB: int = Field(
        default=102400,
    )
    
    CORS_ORIGINS: str = Field(
        default="http://localhost:3000,http://localhost:5173",
    )
    
    @property
    def CORS_ORIGINS_LIST(self) -> List[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]
    
    LOG_LEVEL: str = Field(
        default="INFO",
    )
    LOG_FORMAT: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    @field_validator('LOG_LEVEL')
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in valid_levels:
            logger.warning(f"Неверный LOG_LEVEL '{v}', используется 'INFO'")
            return "INFO"
        return v.upper()
    
    def log_config_summary(self) -> None:
        logger.info("=" * 60)
        logger.info(f"Конфигурация {self.PROJECT_NAME} v{self.VERSION}")
        logger.info("=" * 60)
        logger.info(f"  DEBUG: {self.DEBUG}")
        logger.info(f"  API: {self.API_HOST}:{self.API_PORT}")
        logger.info(f"  DATABASE: {self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}")
        logger.info(f"  DB_POOL_SIZE: {self.DB_POOL_SIZE}")
        logger.info(f"  CELERY_BROKER: {self.CELERY_BROKER_URL}")
        logger.info(
            "  HTTP_CLIENT: timeout=%ss retries=%s retry_delay=%ss rate_limit=%ss "
            "(Kaggle aiohttp rate_limit=%ss, list_429_retries=%s, call_429_retries=%s)",
            self.HTTP_CLIENT_TIMEOUT_SECONDS,
            self.HTTP_CLIENT_MAX_RETRIES,
            self.HTTP_CLIENT_RETRY_DELAY_SECONDS,
            self.HTTP_CLIENT_RATE_LIMIT_DELAY_SECONDS,
            self.KAGGLE_HTTP_RATE_LIMIT_DELAY_SECONDS,
            self.KAGGLE_LIST_429_MAX_RETRIES,
            self.KAGGLE_CALL_429_MAX_RETRIES,
        )
        logger.info(f"  CELERY_EDA_QUEUE: {self.CELERY_EDA_QUEUE}")
        logger.info(f"  KAGGLE_INTERVAL: {self.KAGGLE_UPDATE_INTERVAL_DAYS} дней")
        logger.info(f"  UCI_INTERVAL: {self.UCI_UPDATE_INTERVAL_DAYS} дней")
        logger.info(f"  UCI_CATALOG_FILTER_PYTHON: {self.UCI_CATALOG_FILTER_PYTHON}")
        logger.info(f"  UCI_SKIP_DATE_OPTIMIZATION: {self.UCI_SKIP_DATE_OPTIMIZATION}")
        logger.info(f"  KAGGLE_SKIP_DATE_OPTIMIZATION: {self.KAGGLE_SKIP_DATE_OPTIMIZATION}")
        logger.info(f"  UCI_FORCE_HASH_RECALC_ON_SAME_SIZE: {self.UCI_FORCE_HASH_RECALC_ON_SAME_SIZE}")
        logger.info(f"  KAGGLE_FORCE_HASH_RECALC_ON_SAME_SIZE: {self.KAGGLE_FORCE_HASH_RECALC_ON_SAME_SIZE}")
        logger.info(f"  STARTUP_DELAY: {self.AGGREGATION_STARTUP_DELAY_MINUTES} мин")
        logger.info(f"  AGGREGATION_BATCH_SIZE: {self.AGGREGATION_BATCH_SIZE}")
        logger.info(f"  UPDATE_BATCH_SIZE: {self.UPDATE_BATCH_SIZE}")
        logger.info(f"  MAX_FILE_SIZE: {self.MAX_FILE_SIZE_KB} КБ")
        logger.info(f"  LOG_LEVEL: {self.LOG_LEVEL}")
        logger.info("=" * 60)


@lru_cache()
def get_settings() -> Settings:
    settings = Settings()
    settings.log_config_summary()
    return settings


settings = get_settings()