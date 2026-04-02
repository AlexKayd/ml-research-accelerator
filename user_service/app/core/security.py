import logging
from datetime import datetime, timedelta, timezone
from typing import Annotated, Optional
from jose import JWTError, ExpiredSignatureError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from app.domain.user import User as DomainUser
from app.domain.user import TokenData
from app.core.config import settings
from app.core.database import get_db
from app.repository.user_repository import UserRepository

logger = logging.getLogger(__name__)


pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=12,
)

security = HTTPBearer(auto_error=False)


def hash_password(password: str) -> str:
    """Хеширует пароль с использованием bcrypt"""
    logger.debug("Хеширование пароля")
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Проверяет соответствие пароля хешу"""
    logger.debug("Проверка пароля")
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(
    user_id: int,
    secret_key: str = settings.SECRET_KEY,
    expire_minutes: int = settings.ACCESS_TOKEN_EXPIRE_MINUTES,
    algorithm: str = settings.ALGORITHM
) -> str:
    """Создаёт access токен"""
    logger.debug(f"Создание access токена для user_id={user_id}")
    
    now = datetime.now(timezone.utc)
    expire = now + timedelta(minutes=expire_minutes)
    
    payload = {
        "sub": f"user:{user_id}",
        "user_id": user_id,
        "type": "access",
        "exp": expire,
        "iat": now,
    }
    
    token = jwt.encode(payload, secret_key, algorithm=algorithm)
    
    logger.debug(f"Access токен создан: exp={expire}")
    return token


def create_refresh_token(
    user_id: int,
    secret_key: str = settings.SECRET_KEY,
    expire_days: int = settings.REFRESH_TOKEN_EXPIRE_DAYS,
    algorithm: str = settings.ALGORITHM
) -> str:
    """Создаёт refresh токен"""
    logger.debug(f"Создание refresh токена для user_id={user_id}")
    
    now = datetime.now(timezone.utc)
    expire = now + timedelta(days=expire_days)
    
    payload = {
        "sub": f"user:{user_id}",
        "user_id": user_id,
        "type": "refresh",
        "exp": expire,
        "iat": now,
    }
    
    token = jwt.encode(payload, secret_key, algorithm=algorithm)
    
    logger.debug(f"Refresh токен создан: exp={expire}")
    return token


def decode_token(
    token: str,
    secret_key: str = settings.SECRET_KEY,
    algorithm: str = settings.ALGORITHM
) -> TokenData:
    """Декодирует токен и извлекает данные"""
    logger.debug("Декодирование токена")
    
    payload = jwt.decode(token, secret_key, algorithms=[algorithm])
    
    user_id: int = payload.get("user_id")
    token_type: str = payload.get("type")
    exp: int = payload.get("exp")
    
    if user_id is None or token_type is None:
        logger.warning("Невалидный payload токена")
        raise JWTError("Невалидный payload токена")
    
    token_data = TokenData(
        user_id=user_id,
        token_type=token_type,
        exp=exp,
    )
    
    logger.debug(f"Токен декодирован: user_id={user_id}, type={token_type}")
    
    return token_data


async def get_current_user(
    credentials: Annotated[
        Optional[HTTPAuthorizationCredentials],
        Depends(security)
    ] = None,
    session: AsyncSession = Depends(get_db),
) -> DomainUser:
    """Получение текущего авторизованного пользователя"""
    if credentials is None:
        logger.warning("Отсутствует токен в запросе")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Требуется авторизация",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = credentials.credentials
    
    try:
        token_data = decode_token(
            token=token,
            secret_key=settings.SECRET_KEY,
            algorithm=settings.ALGORITHM,
        )
    except ExpiredSignatureError:
        logger.warning("Токен истёк")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Срок действия токена истёк",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except JWTError as e:
        logger.warning(f"Невалидный токен: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Невалидный токен",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if token_data.token_type != "access":
        logger.warning(f"Неверный тип токена: {token_data.token_type}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Требуется access токен",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_repo = UserRepository(session)
    user = await user_repo.get_by_id(token_data.user_id)
    
    if user is None:
        logger.warning(f"Пользователь не найден: user_id={token_data.user_id}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Невалидный токен",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    logger.debug(f"Текущий пользователь загружен: user_id={user.user_id}")
    return user