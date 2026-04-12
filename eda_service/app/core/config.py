import os
import logging
from functools import lru_cache
from typing import List
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    PROJECT_NAME: str = Field(default="ML Research Accelerator EDA Service")
    VERSION: str = Field(default="1.0.0")
    DEBUG: bool = Field(default=False)

    API_PORT: int = Field(default=8003, ge=1, le=65535)
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

    @field_validator("POSTGRES_PASSWORD")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if not v and not os.getenv("CI"):
            logger.warning("POSTGRES_PASSWORD не установлен")
        return v

    REDIS_URL: str = Field(default="redis://localhost:6379/1")

    SECRET_KEY: str = Field(
        default="",
        description="Секрет для JWT access-токенов",
    )
    ALGORITHM: str = Field(default="HS256")

    CELERY_BROKER_URL: str = Field(default="redis://localhost:6379/1")
    CELERY_RESULT_BACKEND: str = Field(default="redis://localhost:6379/1")
    CELERY_TASK_TIME_LIMIT: int = Field(default=86400)
    CELERY_TASK_SOFT_TIME_LIMIT: int = Field(default=84600)
    CELERY_EDA_QUEUE: str = Field(default="eda")
    CELERY_GEN_QUEUE: str = Field(default="eda_gen")
    CELERY_WAITER_QUEUE: str = Field(default="eda_waiter")
    CELERY_NOTIFY_QUEUE: str = Field(default="eda_notify")
    CELERY_WORKER_CONCURRENCY: int = Field(default=2, ge=1, le=64)
    CELERY_GEN_WORKER_CONCURRENCY: int = Field(default=2, ge=1, le=64)

    REPORT_STALE_AFTER_HOURS: int = Field(default=24, ge=1, le=168)
    REPORT_STUCK_AFTER_MINUTES: int = Field(default=30, ge=1, le=720)
    STUCK_REPORTS_BEAT_INTERVAL_HOURS: int = Field(
        default=1,
        ge=1,
        le=24,
        description="Интервал Celery Beat для detect_stuck_reports_task (часы)",
    )
    WAITER_POLL_INTERVAL_SECONDS: int = Field(default=5, ge=1, le=300)
    WAITER_MAX_WAIT_MINUTES: int = Field(default=120, ge=1, le=1440)

    GENERATE_RATE_LIMIT_PER_MINUTE: int = Field(default=5, ge=1, le=100000)

    REPORT_SUBSCRIBERS_REDIS_TTL_SECONDS: int = Field(
        default=604800,
        ge=300,
        le=2592000,
        description="TTL множества eda:report_subscribers:{report_id} (сек)",
    )
    REPORT_ATTACH_ENQUEUE_COOLDOWN_SECONDS: int = Field(
        default=3600,
        ge=60,
        le=86400,
        description="Не ставить повторно notify для той же пары report/user чаще (сек)",
    )

    HTTP_CLIENT_TIMEOUT_SECONDS: float = Field(default=30.0, ge=1.0, le=600.0)
    HTTP_CLIENT_MAX_RETRIES: int = Field(default=3, ge=0, le=20)
    HTTP_CLIENT_RETRY_DELAY_SECONDS: float = Field(default=1.0, ge=0.1, le=60.0)

    MINIO_ENDPOINT: str = Field(default="localhost:9000")
    MINIO_ACCESS_KEY: str = Field(default="minioadmin")
    MINIO_SECRET_KEY: str = Field(default="minioadmin", exclude=True)
    MINIO_SECURE: bool = Field(default=False)
    MINIO_REPORTS_BUCKET: str = Field(default="eda-reports")
    MINIO_AUTO_CREATE_BUCKET: bool = Field(default=True)
    MINIO_PUBLIC_BASE_URL: str = Field(default="")
    MINIO_REPORTS_BUCKET_ANONYMOUS_READ: bool = Field(default=True)

    USER_SERVICE_URL: str = Field(default="http://user_service:8000")
    USER_SERVICE_HTTP_TIMEOUT_SECONDS: float = Field(default=30.0, ge=1.0, le=600.0)
    EDA_SERVICE_INTERNAL_TOKEN: str = Field(
        default="",
        description="Общий секрет с user_service (заголовок X-EDA-Internal-Token)",
    )

    USER_SERVICE_NOTIFY_MAX_RETRIES: int = Field(default=30, ge=0, le=10000)
    USER_SERVICE_NOTIFY_RETRY_BASE_DELAY_SECONDS: float = Field(
        default=2.0, ge=0.1, le=3600.0
    )
    USER_SERVICE_NOTIFY_RETRY_MAX_DELAY_SECONDS: float = Field(
        default=300.0, ge=0.1, le=86400.0
    )

    CORS_ORIGINS: str = Field(
        default="http://localhost:5173",
    )

    @property
    def CORS_ORIGINS_LIST(self) -> List[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

    LOG_LEVEL: str = Field(default="INFO")
    LOG_FORMAT: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @field_validator("LOG_LEVEL")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in valid_levels:
            logger.warning("Неверный LOG_LEVEL '%s', используется 'INFO'", v)
            return "INFO"
        return v.upper()

    def log_config_summary(self) -> None:
        logger.info("=" * 60)
        logger.info("Конфигурация %s v%s", self.PROJECT_NAME, self.VERSION)
        logger.info("=" * 60)
        logger.info("  DEBUG: %s", self.DEBUG)
        logger.info("  API: %s:%s", self.API_HOST, self.API_PORT)
        logger.info(
            "  DATABASE: %s:%s/%s",
            self.POSTGRES_HOST,
            self.POSTGRES_PORT,
            self.POSTGRES_DB,
        )
        logger.info("  CELERY_BROKER: %s", self.CELERY_BROKER_URL)
        logger.info(
            "  CELERY_QUEUES: eda=%s gen=%s waiter=%s notify=%s",
            self.CELERY_EDA_QUEUE,
            self.CELERY_GEN_QUEUE,
            self.CELERY_WAITER_QUEUE,
            self.CELERY_NOTIFY_QUEUE,
        )
        logger.info(
            "  CELERY_CONCURRENCY: default=%s gen=%s",
            self.CELERY_WORKER_CONCURRENCY,
            self.CELERY_GEN_WORKER_CONCURRENCY,
        )
        logger.info(
            "  REPORT_POLICY: stale_after=%sh stuck_after=%sm",
            self.REPORT_STALE_AFTER_HOURS,
            self.REPORT_STUCK_AFTER_MINUTES,
        )
        logger.info(
            "  REPORT_SUBSCRIBERS: ttl=%ss attach_cooldown=%ss",
            self.REPORT_SUBSCRIBERS_REDIS_TTL_SECONDS,
            self.REPORT_ATTACH_ENQUEUE_COOLDOWN_SECONDS,
        )
        logger.info("  MINIO_ENDPOINT: %s", self.MINIO_ENDPOINT)
        logger.info("  MINIO_REPORTS_BUCKET: %s", self.MINIO_REPORTS_BUCKET)
        logger.info(
            "  MINIO_REPORTS_BUCKET_ANONYMOUS_READ: %s",
            self.MINIO_REPORTS_BUCKET_ANONYMOUS_READ,
        )
        logger.info("  USER_SERVICE_URL: %s", self.USER_SERVICE_URL)
        logger.info(
            "  JWT: ALGORITHM=%s SECRET_KEY=%s",
            self.ALGORITHM,
            "задан" if (self.SECRET_KEY or "").strip() else "не задан",
        )
        logger.info(
            "  USER_SERVICE_NOTIFY_POLICY: max_retries=%s base_delay=%ss max_delay=%ss",
            self.USER_SERVICE_NOTIFY_MAX_RETRIES,
            self.USER_SERVICE_NOTIFY_RETRY_BASE_DELAY_SECONDS,
            self.USER_SERVICE_NOTIFY_RETRY_MAX_DELAY_SECONDS,
        )
        logger.info("  LOG_LEVEL: %s", self.LOG_LEVEL)
        logger.info("=" * 60)


@lru_cache()
def get_settings() -> Settings:
    settings = Settings()
    settings.log_config_summary()
    return settings


settings = get_settings()