import asyncio
import json
import logging
from typing import Annotated, AsyncIterator
import redis.asyncio as redis_async
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from app.core.config import settings
from app.core.jwt_auth import get_current_user_id
from app.sse.sse_broker import sse_channel_for_user

logger = logging.getLogger(__name__)

router = APIRouter(tags=["EDA-SSE"])


@router.get(
    "/events",
    summary="SSE: события готовности отчёта",
    description="Server-Sent Events; после генерации публикуется report_ready с report_url",
)
async def report_events_stream(
    user_id: Annotated[int, Depends(get_current_user_id)],
) -> StreamingResponse:
    """Подписка на канал Redis, совпадающий с publish_report_ready_sync в Celery"""

    async def event_stream() -> AsyncIterator[bytes]:
        channel = sse_channel_for_user(user_id)
        client = redis_async.from_url(settings.REDIS_URL, decode_responses=True)
        pubsub = client.pubsub()
        try:
            await pubsub.subscribe(channel)
            yield b": ok\n\n"
            while True:
                try:
                    message = await pubsub.get_message(
                        ignore_subscribe_messages=True,
                        timeout=25.0,
                    )
                    if message is None:
                        yield b": ping\n\n"
                        continue
                    if message.get("type") != "message":
                        continue
                    data = message.get("data")
                    if isinstance(data, bytes):
                        data = data.decode("utf-8")
                    payload = data if isinstance(data, str) else json.dumps(data)
                    yield f"data: {payload}\n\n".encode("utf-8")
                except asyncio.CancelledError:
                    break
                except Exception as e:
                    logger.warning("SSE: ошибка чтения pubsub user_id=%s: %s", user_id, e, exc_info=True)
                    break
        finally:
            try:
                await pubsub.unsubscribe(channel)
            except Exception:
                pass
            try:
                await pubsub.close()
            except Exception:
                pass
            try:
                await client.aclose()
            except Exception:
                pass

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )