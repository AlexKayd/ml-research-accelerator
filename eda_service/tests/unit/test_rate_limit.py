import pytest
from fastapi import HTTPException
from app.core import jwt_auth


@pytest.mark.asyncio
async def test_generate_rate_limit_429_after_limit(monkeypatch):
    """Проверяет rate limit: после лимита запросов будет HTTP 429"""

    class FakeRedis:
        def __init__(self):
            self.n = 0

        async def incr(self, _key):
            self.n += 1
            return self.n

        async def expire(self, _key, _ttl):
            return True

        async def aclose(self):
            return None

    fake_client = FakeRedis()

    class FakeRedisModule:
        @staticmethod
        def from_url(*_a, **_kw):
            return fake_client

    monkeypatch.setattr(jwt_auth, "redis_async", FakeRedisModule)

    class S:
        GENERATE_RATE_LIMIT_PER_MINUTE = 2
        REDIS_URL = "redis://fake/1"

    monkeypatch.setattr(jwt_auth, "get_settings", lambda: S())

    await jwt_auth.verify_generate_rate_limit(user_id=1)
    await jwt_auth.verify_generate_rate_limit(user_id=1)
    with pytest.raises(HTTPException) as e:
        await jwt_auth.verify_generate_rate_limit(user_id=1)
    assert e.value.status_code == 429