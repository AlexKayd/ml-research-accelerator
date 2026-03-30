import logging
from typing import Any, Dict
from app.core.config import settings
from app.core.database import health_check_db

logger = logging.getLogger(__name__)


async def health_check_redis() -> bool:
    try:
        import redis.asyncio as redis
    except Exception as e:
        logger.error("Redis клиент недоступен: %s", e)
        return False

    client = redis.from_url(
        settings.REDIS_URL,
        encoding="utf-8",
        decode_responses=True,
    )
    try:
        pong = await client.ping()
        return bool(pong)
    except Exception as e:
        logger.error("Health check Redis не прошёл: %s", e)
        return False
    finally:
        try:
            await client.aclose()
        except Exception:
            pass


async def health_check_minio() -> bool:
    try:
        from app.core.minio import get_minio_client

        return get_minio_client().health_check()
    except Exception as e:
        logger.error("Health check MinIO не прошёл: %s", e)
        return False


async def get_health_status() -> Dict[str, Any]:
    db_ok = await health_check_db()
    redis_ok = await health_check_redis()
    minio_ok = await health_check_minio()

    checks = {
        "database": db_ok,
        "redis": redis_ok,
        "minio": minio_ok,
    }
    ok = all(checks.values())

    return {
        "status": "ok" if ok else "degraded",
        "service": "eda_service",
        "checks": checks,
    }