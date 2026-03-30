import asyncio
import logging
from typing import Set
import redis as redis_sync
import redis.asyncio as redis_async
from app.core.celery_config import celery_app
from app.core.config import get_settings

logger = logging.getLogger(__name__)


def _subscribers_key(report_id: int) -> str:
    """Формирует ключ подписчиков отчёта"""
    return f"eda:report_subscribers:{int(report_id)}"


def _attach_enqueued_key(report_id: int, user_id: int) -> str:
    """Формирует ключ постановки notify в user_service"""
    return f"eda:attach_enqueued:{int(report_id)}:{int(user_id)}"


def touch_user_report_attach_cooldown_sync(report_id: int, user_id: int) -> None:
    """Выставляет тот же ключ, что и schedule_user_report_attach_once, без постановки задачи"""
    settings = get_settings()
    key = _attach_enqueued_key(report_id, user_id)
    client = redis_sync.from_url(settings.REDIS_URL, decode_responses=True)

    try:
        client.set(key, "1", ex=int(settings.REPORT_ATTACH_ENQUEUE_COOLDOWN_SECONDS))
    finally:
        try:
            client.close()
        except Exception:
            pass


async def register_report_subscriber(report_id: int, user_id: int) -> None:
    """Добавляет user_id в множество ожидающих отчёт report_id"""
    settings = get_settings()
    ttl = int(settings.REPORT_SUBSCRIBERS_REDIS_TTL_SECONDS)
    key = _subscribers_key(report_id)
    client = redis_async.from_url(settings.REDIS_URL, encoding="utf-8", decode_responses=True)

    try:
        await client.sadd(key, str(int(user_id)))
        await client.expire(key, ttl)
    finally:
        try:
            await client.aclose()
        except Exception:
            pass


def clear_report_subscribers_sync(report_id: int) -> None:
    """Удаляет ключ подписчиков отчёта из Redis (без чтения множества)."""
    settings = get_settings()
    key = _subscribers_key(report_id)
    client = redis_sync.from_url(settings.REDIS_URL, decode_responses=True)
    try:
        client.delete(key)
    finally:
        try:
            client.close()
        except Exception:
            pass


def pop_report_subscribers_sync(report_id: int) -> Set[int]:
    """Читает множество подписчиков и удаляет ключ"""
    settings = get_settings()
    key = _subscribers_key(report_id)
    client = redis_sync.from_url(settings.REDIS_URL, decode_responses=True)

    try:
        pipe = client.pipeline()
        pipe.smembers(key)
        pipe.delete(key)
        members, _ = pipe.execute()
        if not members:
            return set()
        out: Set[int] = set()
        for m in members:
            try:
                out.add(int(m))
            except (TypeError, ValueError):
                continue
        return out

    finally:
        try:
            client.close()
        except Exception:
            pass


def get_report_subscribers_sync(report_id: int) -> Set[int]:
    """Читает множество подписчиков без удаления ключа"""
    settings = get_settings()
    key = _subscribers_key(report_id)
    client = redis_sync.from_url(settings.REDIS_URL, decode_responses=True)

    try:
        members = client.smembers(key) or set()
        out: Set[int] = set()
        for m in members:
            try:
                out.add(int(m))
            except (TypeError, ValueError):
                continue
        return out

    finally:
        try:
            client.close()
        except Exception:
            pass


async def schedule_user_report_attach_once(report_id: int, user_id: int) -> None:
    """Ставит notify_user_service_report_ready_task не чаще одного раза на пару (report, user)"""
    settings = get_settings()
    cooldown = int(settings.REPORT_ATTACH_ENQUEUE_COOLDOWN_SECONDS)
    key = _attach_enqueued_key(report_id, user_id)
    client = redis_async.from_url(settings.REDIS_URL, encoding="utf-8", decode_responses=True)

    try:
        ok = await client.set(name=key, value="1", nx=True, ex=cooldown)
        if not ok:
            return

    finally:
        try:
            await client.aclose()
        except Exception:
            pass

    await asyncio.to_thread(
        celery_app.send_task,
        "app.celery.tasks.notify_user_service_report_ready_task",
        kwargs={"user_id": int(user_id), "report_id": int(report_id)},
        queue=settings.CELERY_EDA_QUEUE,
    )

    logger.debug(
        "Поставлена notify: report_id=%s user_id=%s",
        report_id,
        user_id,
    )