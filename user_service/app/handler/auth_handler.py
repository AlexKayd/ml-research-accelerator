import logging
from typing import Annotated
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.config import settings
from app.service.auth_service import AuthService
from app.service.user_service import UserService
from app.repository.user_repository import UserRepository
from app.schemas.auth_schemas import (
    UserCreate,
    UserLogin,
    TokenRefresh,
    UserResponse,
    TokenResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Аутентификация"])


def get_auth_service(session: AsyncSession = Depends(get_db)) -> AuthService:
    user_repo = UserRepository(session)
    return AuthService(
        user_repository=user_repo,
        secret_key=settings.SECRET_KEY,
        access_token_expire_minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES,
        refresh_token_expire_days=settings.REFRESH_TOKEN_EXPIRE_DAYS,
        algorithm=settings.ALGORITHM,
    )


def get_user_service(session: AsyncSession = Depends(get_db)) -> UserService:
    user_repo = UserRepository(session)
    return UserService(user_repository=user_repo)


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Регистрация нового пользователя",
    description="Зарегистрировать нового пользователя в системе"
)
async def register(
    user_create: UserCreate,
    auth_service: Annotated[AuthService, Depends(get_auth_service)]
) -> dict:
    """Зарегистрировать нового пользователя"""
    
    user = await auth_service.register(user_create)

    logger.info(f"Пользователь успешно зарегистрирован: user_id={user.user_id}")
    return {
        "user_id": user.user_id,
        "login": user.login,
        "created_at": user.created_at,
    }


@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Вход в систему",
    description="Аутентифицировать пользователя и получить токены"
)
async def login(
    user_login: UserLogin,
    auth_service: Annotated[AuthService, Depends(get_auth_service)]
) -> dict:
    """Войти в систему и получить токены"""
    
    access_token, refresh_token, user_profile = await auth_service.login(user_login)
    
    logger.info(f"Пользователь успешно вошёл: user_id={user_profile.user_id}")
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": {
            "user_id": user_profile.user_id,
            "login": user_profile.login,
            "created_at": user_profile.created_at,
        },
    }


@router.post(
    "/refresh",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Обновить токены",
    description="Обновить пару токенов по refresh токену"
)
async def refresh_tokens(
    token_refresh: TokenRefresh,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> dict:
    """Обновить токены"""
    
    access_token, refresh_token, user_profile = await auth_service.refresh_tokens(
        token_refresh.refresh_token
    )
    
    logger.info(f"Токены успешно обновлены: user_id={user_profile.user_id}")
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": {
            "user_id": user_profile.user_id,
            "login": user_profile.login,
            "created_at": user_profile.created_at,
        },
    }