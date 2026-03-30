import json
import logging
from typing import Any, Dict

logger = logging.getLogger(__name__)


def sse_channel_for_user(user_id: int) -> str:
    return f"eda:sse:user:{int(user_id)}"


def publish_report_ready_sync(user_id: int, report_id: int, report_url: str) -> None:
    """Синхронная публикация из Celery worker"""
    from app.core.config import get_settings

    try:
        import redis as redis_sync
    except ImportError:
        logger.warning("redis не установлен - SSE publish пропущен")
        return

    settings = get_settings()
    payload: Dict[str, Any] = {
        "event": "report_ready",
        "report_id": int(report_id),
        "report_url": report_url,
    }
    raw = json.dumps(payload, ensure_ascii=False)
    client = redis_sync.from_url(settings.REDIS_URL, decode_responses=True)

    try:
        n = client.publish(sse_channel_for_user(user_id), raw)
        logger.debug("SSE publish: user_id=%s subscribers=%s", user_id, n)
    except Exception as e:
        logger.warning("SSE publish не удался: user_id=%s %s", user_id, e, exc_info=True)
    finally:
        try:
            client.close()
        except Exception:
            pass


def publish_report_failed_sync(user_id: int, report_id: int, error_message: str) -> None:
    """Синхронная публикация из Celery worker / API через to_thread"""
    from app.core.config import get_settings

    try:
        import redis as redis_sync
    except ImportError:
        logger.warning("redis не установлен - SSE publish пропущен")
        return

    settings = get_settings()
    payload: Dict[str, Any] = {
        "event": "report_failed",
        "report_id": int(report_id),
        "error_message": (error_message or "").strip() or "неизвестная ошибка",
    }
    raw = json.dumps(payload, ensure_ascii=False)
    client = redis_sync.from_url(settings.REDIS_URL, decode_responses=True)

    try:
        n = client.publish(sse_channel_for_user(user_id), raw)
        logger.debug("SSE publish failed: user_id=%s subscribers=%s", user_id, n)
    except Exception as e:
        logger.warning("SSE publish (failed) не удался: user_id=%s %s", user_id, e, exc_info=True)
    finally:
        try:
            client.close()
        except Exception:
            pass


def publish_report_deleting_sync(user_id: int, report_id: int) -> None:
    """Событие: отчёт переведён в deleting"""
    from app.core.config import get_settings

    try:
        import redis as redis_sync
    except ImportError:
        logger.warning("redis не установлен - SSE publish пропущен")
        return

    settings = get_settings()
    payload: Dict[str, Any] = {
        "event": "report_deleting",
        "report_id": int(report_id),
    }
    raw = json.dumps(payload, ensure_ascii=False)
    client = redis_sync.from_url(settings.REDIS_URL, decode_responses=True)

    try:
        n = client.publish(sse_channel_for_user(user_id), raw)
        logger.debug("SSE publish deleting: user_id=%s subscribers=%s", user_id, n)
    except Exception as e:
        logger.warning("SSE publish (deleting) не удался: user_id=%s %s", user_id, e, exc_info=True)
    finally:
        try:
            client.close()
        except Exception:
            pass


def publish_report_deleted_sync(user_id: int, report_id: int) -> None:
    """Событие: отчёт удалён"""
    from app.core.config import get_settings

    try:
        import redis as redis_sync
    except ImportError:
        logger.warning("redis не установлен - SSE publish пропущен")
        return

    settings = get_settings()
    payload: Dict[str, Any] = {
        "event": "report_deleted",
        "report_id": int(report_id),
    }
    raw = json.dumps(payload, ensure_ascii=False)
    client = redis_sync.from_url(settings.REDIS_URL, decode_responses=True)

    try:
        n = client.publish(sse_channel_for_user(user_id), raw)
        logger.debug("SSE publish deleted: user_id=%s subscribers=%s", user_id, n)
    except Exception as e:
        logger.warning("SSE publish (deleted) не удался: user_id=%s %s", user_id, e, exc_info=True)
    finally:
        try:
            client.close()
        except Exception:
            pass