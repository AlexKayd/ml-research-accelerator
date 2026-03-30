import asyncio
import logging
from typing import Any, Dict, Optional
import aiohttp
from app.clients.base_client import BaseHttpClient
from app.core.config import get_settings
from app.domain.exceptions import UserServiceReportAttachFailedError, UserServiceUnavailableError
from app.domain.interfaces import IUserServiceClient

logger = logging.getLogger(__name__)


class UserServiceClient(BaseHttpClient, IUserServiceClient):

    def __init__(self, timeout: Optional[float] = None) -> None:
        s = get_settings()
        t = timeout if timeout is not None else float(s.USER_SERVICE_HTTP_TIMEOUT_SECONDS)
        super().__init__(client_name="user_service", timeout=t)
        self._base_url = (s.USER_SERVICE_URL or "").rstrip("/")

    def _attach_url(self, user_id: int) -> str:
        """Формирует URL для привязки отчёта к пользователю"""
        return f"{self._base_url}/api/users/{user_id}/reports"

    def _request_headers(self) -> Dict[str, str]:
        """Формирует заголовки для запроса"""
        s = get_settings()
        headers: Dict[str, str] = {"Content-Type": "application/json"}
        token = s.EDA_SERVICE_INTERNAL_TOKEN or ""
        if token.strip():
            headers["X-EDA-Internal-Token"] = token.strip()
        return headers

    async def attach_report_to_user(self, user_id: int, report_id: int) -> None:
        """Вызывает эндпойнт привязки отчёта к пользователю"""
        if not self._base_url:
            raise UserServiceUnavailableError(
                user_id=user_id,
                report_id=report_id,
                reason="USER_SERVICE_URL не задан",
            )

        url = self._attach_url(user_id)
        payload: Dict[str, Any] = {"report_id": report_id}
        session = await self._get_session()

        try:
            async with session.post(
                url,
                json=payload,
                headers=self._request_headers(),
            ) as resp:
                body_preview = (await resp.text())[:500]
                if resp.status in (200, 201, 204):
                    logger.info(
                        "user_service: привязка отчёта ok user_id=%s report_id=%s status=%s",
                        user_id,
                        report_id,
                        resp.status,
                    )
                    return

                if resp.status == 409:
                    logger.info(
                        "user_service: конфликт user_id=%s report_id=%s",
                        user_id,
                        report_id,
                    )
                    return

                if 400 <= resp.status < 500:
                    if resp.status in (408, 429):
                        raise UserServiceUnavailableError(
                            user_id=user_id,
                            report_id=report_id,
                            reason=f"HTTP {resp.status}: {body_preview}",
                        )
                    raise UserServiceReportAttachFailedError(
                        user_id=user_id,
                        report_id=report_id,
                        reason=f"HTTP {resp.status}: {body_preview}",
                    )

                raise UserServiceUnavailableError(
                    user_id=user_id,
                    report_id=report_id,
                    reason=f"HTTP {resp.status}: {body_preview}",
                )
        except aiohttp.ClientError as e:
            logger.warning(
                "user_service: сетевая ошибка user_id=%s report_id=%s: %s",
                user_id,
                report_id,
                e,
            )
            raise UserServiceUnavailableError(
                user_id=user_id,
                report_id=report_id,
                reason=f"сеть: {e}",
            ) from e

    def attach_report_to_user_sync(self, user_id: int, report_id: int) -> None:

        async def _run() -> None:
            try:
                await self.attach_report_to_user(user_id, report_id)
            finally:
                await self.close()

        asyncio.run(_run())