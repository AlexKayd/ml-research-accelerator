import asyncio
import json
import pytest
from app.handler import report_handler
from app.core import jwt_auth
import redis.asyncio as redis_async
from app.sse.sse_broker import sse_channel_for_user


@pytest.mark.asyncio(loop_scope="session")
async def test_api_generate_report_rate_limit_works_with_redis(http, auth_header, monkeypatch):
    """Проверяет: POST /reports/generate ограничивается Redis rate limit и возвращает 429 после лимита"""

    class FakeResp:
        report_id = 1
        status = "processing"
        report_url = None

    async def fake_get_or_create(self, file_id: int, user_id: int):
        return FakeResp()

    monkeypatch.setattr(report_handler.ReportService, "get_or_create_report", fake_get_or_create)

    base = jwt_auth.get_settings()

    class S:
        REDIS_URL = base.REDIS_URL
        GENERATE_RATE_LIMIT_PER_MINUTE = 2
        SECRET_KEY = base.SECRET_KEY
        ALGORITHM = base.ALGORITHM

    monkeypatch.setattr(jwt_auth, "get_settings", lambda: S())

    r1 = await http.post("/api/reports/generate", headers=auth_header, json={"file_id": 1})
    assert r1.status_code == 200
    r2 = await http.post("/api/reports/generate", headers=auth_header, json={"file_id": 1})
    assert r2.status_code == 200
    r3 = await http.post("/api/reports/generate", headers=auth_header, json={"file_id": 1})
    assert r3.status_code == 429


@pytest.mark.asyncio(loop_scope="session")
async def test_api_sse_stream_connect_and_receive_report_ready(
    http_streaming, auth_header, test_redis, user_id
):
    """Проверяет SSE: подключение к /reports/events и получение report_ready сообщения из Redis"""

    channel = sse_channel_for_user(user_id)
    client = redis_async.from_url(test_redis.url, decode_responses=True)
    try:
        async with http_streaming.stream("GET", "/api/reports/events", headers=auth_header) as resp:
            assert resp.status_code == 200

            lines = resp.aiter_lines()
            line1 = await asyncio.wait_for(anext(lines), timeout=5.0)
            assert line1.startswith(":")

            payload = {
                "event": "report_ready",
                "report_id": 10,
                "report_url": "http://minio/x.html",
            }
            await client.publish(channel, json.dumps(payload))

            async def _wait_data_line() -> dict:
                async for line in lines:
                    if line.startswith("data: "):
                        return json.loads(line.removeprefix("data: ").strip())
                raise AssertionError("SSE stream closed without data")

            got = await asyncio.wait_for(_wait_data_line(), timeout=5.0)
            assert got["event"] == "report_ready"
            assert got["report_id"] == 10
    finally:
        await client.aclose()