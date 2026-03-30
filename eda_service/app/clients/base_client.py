import logging
from typing import Optional
import aiohttp
from aiohttp import ClientTimeout, TCPConnector
from app.core.config import get_settings

logger = logging.getLogger(__name__)


class BaseHttpClient:

    def __init__(
        self,
        client_name: str,
        timeout: Optional[float] = None,
    ) -> None:
        s = get_settings()
        self._client_name = client_name
        self._timeout = (
            float(timeout)
            if timeout is not None
            else float(getattr(s, "HTTP_CLIENT_TIMEOUT_SECONDS", 30.0))
        )
        self._session: Optional[aiohttp.ClientSession] = None
        logger.debug("Инициализирован HTTP-клиент '%s'", client_name)

    async def _get_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            timeout = ClientTimeout(total=self._timeout)
            connector = TCPConnector(limit=10, ttl_dns_cache=300)
            self._session = aiohttp.ClientSession(
                timeout=timeout,
                connector=connector,
                headers={"User-Agent": "ml-research-accelerator-eda/1.0"},
            )
            logger.debug("Создана aiohttp-сессия для '%s'", self._client_name)
        return self._session

    async def close(self) -> None:
        if self._session and not self._session.closed:
            await self._session.close()
            logger.debug("Сессия '%s' закрыта", self._client_name)
            self._session = None

    async def __aenter__(self) -> "BaseHttpClient":
        return self

    async def __aexit__(
        self,
        exc_type,
        exc_val,
        exc_tb,
    ) -> None:
        await self.close()