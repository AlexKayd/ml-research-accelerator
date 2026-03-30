import logging
import sys
from pathlib import Path
from typing import Optional
from app.core.config import settings


def _force_utf8_stdio() -> None:
    """Корректная кириллица в логах"""
    for stream in (sys.stdout, sys.stderr):
        try:
            if hasattr(stream, "reconfigure"):
                stream.reconfigure(encoding="utf-8", errors="replace")
        except (OSError, ValueError, AttributeError):
            pass


def setup_logging(log_file: Optional[str] = None, log_level: Optional[str] = None) -> None:
    """Настраивает логирование приложения"""
    level = (log_level or settings.LOG_LEVEL).upper()
    _force_utf8_stdio()

    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.setLevel(level)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(logging.Formatter(settings.LOG_FORMAT))
    root_logger.addHandler(console_handler)

    if log_file:
        try:
            log_path = Path(log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)
            file_handler = logging.FileHandler(log_file, encoding="utf-8", mode="a")
            file_handler.setLevel(level)
            file_handler.setFormatter(logging.Formatter(settings.LOG_FORMAT))
            root_logger.addHandler(file_handler)
            logging.info("Логи записываются в файл: %s", log_file)
        except Exception as e:
            logging.warning("Не удалось создать файловый обработчик логов: %s", e)

    app_level = getattr(logging, level, logging.INFO)
    logging.getLogger("asyncpg").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(
        logging.WARNING if not settings.DEBUG else logging.INFO
    )
    logging.getLogger("sqlalchemy.pool").setLevel(logging.WARNING)
    logging.getLogger("celery").setLevel(app_level)
    logging.getLogger("celery.worker").setLevel(app_level)
    logging.getLogger("kombu").setLevel(
        logging.WARNING if app_level > logging.DEBUG else app_level
    )
    logging.getLogger("aiohttp").setLevel(logging.WARNING)
    logging.getLogger("minio").setLevel(logging.WARNING)

    logger = logging.getLogger(__name__)
    logger.info("Логирование настроено: уровень=%s, DEBUG=%s", level, settings.DEBUG)