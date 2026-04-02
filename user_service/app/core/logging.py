import logging
import sys
from typing import Optional
from app.core.config import settings


def setup_logging(log_level: Optional[str] = None) -> None:
    level = (log_level or settings.LOG_LEVEL).upper()
    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.setLevel(level)

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level)
    handler.setFormatter(logging.Formatter(settings.LOG_FORMAT))
    root_logger.addHandler(handler)

    logging.getLogger('asyncpg').setLevel('WARNING')
    logging.getLogger('sqlalchemy.engine').setLevel('WARNING' if not settings.DEBUG else 'INFO')
    logging.getLogger('sqlalchemy.pool').setLevel('WARNING')

    logging.getLogger(__name__).info("Логирование настроено: уровень=%s, DEBUG=%s", level, settings.DEBUG)