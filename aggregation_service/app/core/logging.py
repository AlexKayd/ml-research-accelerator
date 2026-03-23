import logging
import sys
from pathlib import Path
from typing import Optional
from app.core.config import settings


def _force_utf8_stdio() -> None:
    """кириллица в логах"""
    for stream in (sys.stdout, sys.stderr):
        try:
            if hasattr(stream, "reconfigure"):
                stream.reconfigure(encoding="utf-8", errors="replace")
        except (OSError, ValueError, AttributeError):
            pass


def setup_logging(
    log_file: Optional[str] = None,
    log_level: Optional[str] = None
) -> None:
    """Настраивает логирование приложения"""
    level = (log_level or settings.LOG_LEVEL).upper()

    _force_utf8_stdio()
    
    base_format = settings.LOG_FORMAT
    
    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    
    root_logger.setLevel(level)
    
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    
    console_formatter = logging.Formatter(base_format)
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)
    
    if log_file:
        try:
            log_path = Path(log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)
            
            file_handler = logging.FileHandler(log_file, encoding='utf-8', mode='a')
            file_handler.setLevel(level)
            file_formatter = logging.Formatter(base_format)
            file_handler.setFormatter(file_formatter)
            
            root_logger.addHandler(file_handler)
            logging.info(f"Логи записываются в файл: {log_file}")
            
        except Exception as e:
            logging.warning(f"Не удалось создать файловый обработчик логов: {e}")
    
    _app_level = getattr(logging, level, logging.INFO)
    logging.getLogger('asyncpg').setLevel('WARNING')
    logging.getLogger('sqlalchemy.engine').setLevel('WARNING' if not settings.DEBUG else 'INFO')
    logging.getLogger('sqlalchemy.pool').setLevel('WARNING')
    logging.getLogger('celery').setLevel(_app_level)
    logging.getLogger('celery.worker').setLevel(_app_level)
    logging.getLogger('kombu').setLevel(logging.WARNING if _app_level > logging.DEBUG else _app_level)
    logging.getLogger('aiohttp').setLevel('WARNING')
    logging.getLogger('kaggle').setLevel(_app_level)
    logging.getLogger('ucimlrepo').setLevel(_app_level)
    
    logger = logging.getLogger(__name__)
    logger.info(f"Логирование настроено: уровень={level}, DEBUG={settings.DEBUG}")
    
    if settings.DEBUG:
        logger.debug("Режим отладки включён: включено подробное логирование")


setup_logging()