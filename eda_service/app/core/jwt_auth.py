import logging
from typing import Annotated, Optional
import redis.asyncio as redis_async
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import ExpiredSignatureError, JWTError, jwt
from app.core.config import get_settings

logger = logging.getLogger(__name__)

security = HTTPBearer(auto_error=False)


def decode_access_token_user_id(token: str) -> int:
    """Извлекает user_id из access JWT"""
    s = get_settings()
    if not (s.SECRET_KEY or "").strip():
        logger.error("SECRET_KEY не задан")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Сервис не настроен для проверки токенов",
        )

    payload = jwt.decode(token, s.SECRET_KEY, algorithms=[s.ALGORITHM])
    if payload.get("type") != "access":
        raise JWTError("Ожидается access-токен")
    uid = payload.get("user_id")
    if uid is None:
        raise JWTError("В токене нет user_id")
    return int(uid)


async def get_current_user_id(
    credentials: Annotated[
        Optional[HTTPAuthorizationCredentials],
        Depends(security),
    ] = None,
) -> int:
    """user_id из Bearer JWT"""
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Требуется авторизация",
            headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        return decode_access_token_user_id(credentials.credentials)
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Срок действия токена истёк",
            headers={"WWW-Authenticate": "Bearer"},
        ) from None

    except JWTError as e:
        logger.warning("Невалидный JWT: %s", e)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Невалидный токен",
            headers={"WWW-Authenticate": "Bearer"},
        ) from e


async def verify_generate_rate_limit(
    user_id: Annotated[int, Depends(get_current_user_id)],
) -> None:
    """Не более GENERATE_RATE_LIMIT_PER_MINUTE запросов на генерацию в минуту на пользователя"""
    settings = get_settings()
    limit = int(settings.GENERATE_RATE_LIMIT_PER_MINUTE)
    key = f"eda:rate:generate:{user_id}"
    client = redis_async.from_url(settings.REDIS_URL, encoding="utf-8", decode_responses=True)

    try:
        n = await client.incr(key)
        if n == 1:
            await client.expire(key, 60)
        if n > limit:
            logger.info("Rate limit: user_id=%s count=%s limit=%s", user_id, n, limit)
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Слишком много запросов на генерацию отчёта. Попробуйте позже.",
            )
    finally:
        try:
            await client.aclose()
        except Exception:
            pass