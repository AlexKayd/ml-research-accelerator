import asyncio
import hashlib
import logging
import time
from abc import ABC
from pathlib import Path
from typing import Optional
import aiohttp
from aiohttp import ClientTimeout, TCPConnector
from app.core.config import get_settings
try:
    import aiofiles
    AIOFILES_AVAILABLE = True
except ImportError:
    AIOFILES_AVAILABLE = False

logger = logging.getLogger(__name__)


class BaseClient(ABC):

    def __init__(
        self,
        source_name: str,
        timeout: Optional[float] = None,
        max_retries: Optional[int] = None,
        rate_limit_delay: Optional[float] = None
    ) -> None:
        s = get_settings()
        self._source_name = source_name
        self._timeout = (
            float(timeout) if timeout is not None else float(s.HTTP_CLIENT_TIMEOUT_SECONDS)
        )
        self._max_retries = (
            int(max_retries) if max_retries is not None else int(s.HTTP_CLIENT_MAX_RETRIES)
        )
        self._rate_limit_delay = (
            float(rate_limit_delay)
            if rate_limit_delay is not None
            else float(s.HTTP_CLIENT_RATE_LIMIT_DELAY_SECONDS)
        )
        self._retry_delay_base = float(s.HTTP_CLIENT_RETRY_DELAY_SECONDS)

        self._session: Optional[aiohttp.ClientSession] = None
        self._last_request_time: float = 0
        
        logger.debug(f"Инициализирован клиент для источника '{source_name}'")
    
    async def _get_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            timeout = ClientTimeout(total=self._timeout)
            connector = TCPConnector(limit=10, ttl_dns_cache=300)
            
            self._session = aiohttp.ClientSession(
                timeout=timeout,
                connector=connector,
                headers={"User-Agent": "ml-research-accelerator/1.0"}
            )
            logger.debug(f"Создана новая сессия для источника '{self._source_name}'")
        
        return self._session
    
    async def _wait_rate_limit(self) -> None:
        """Ждёт необходимое время для соблюдения rate limit источника"""
        now = time.time()
        elapsed = now - self._last_request_time
        
        if elapsed < self._rate_limit_delay:
            sleep_time = self._rate_limit_delay - elapsed
            await asyncio.sleep(sleep_time)
        
        self._last_request_time = time.time()
    
    
    @property
    def _retry_delay(self) -> float:
        return self._retry_delay_base
    
    async def compute_file_hash(self, file_path: Path) -> str:
        """Вычисляет SHA-256 хеш файла"""
        if not file_path.exists():
            raise FileNotFoundError(f"Файл не найден: {file_path}")
        
        logger.debug(f"Вычисление хеша для файла: {file_path.name}")
        
        sha256 = hashlib.sha256()
        
        if AIOFILES_AVAILABLE:
            async with aiofiles.open(file_path, 'rb') as f:
                while True:
                    chunk = await f.read(65536)
                    if not chunk:
                        break
                    sha256.update(chunk)
        else:
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(65536), b''):
                    sha256.update(chunk)
        
        file_hash = sha256.hexdigest().lower()
        logger.debug(f"Хеш файла {file_path.name}: {file_hash[:16]}...")
        
        return file_hash
    
    def is_data_file(self, file_name: str) -> bool:
        """Проверяет, является ли файл data-файлом"""
        if not file_name:
            return False
        
        lower_name = file_name.lower()
        return (lower_name.endswith('.csv') or 
                lower_name.endswith('.json') or 
                lower_name.endswith('.jsonl'))
    
    async def close(self) -> None:
        if self._session and not self._session.closed:
            await self._session.close()
            logger.debug(f"Сессия для источника '{self._source_name}' закрыта")
            self._session = None
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
        return False