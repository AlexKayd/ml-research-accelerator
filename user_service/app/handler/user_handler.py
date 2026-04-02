import logging
from typing import Annotated
from fastapi import APIRouter, Depends, status
from app.core.security import get_current_user
from app.domain.user import User as DomainUser
from app.schemas.user_schemas import UserProfile

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Профиль"])

@router.get(
    "/me",
    response_model=UserProfile,
    status_code=status.HTTP_200_OK,
    summary="Получить свой профиль",
    description="Получить данные профиля текущего авторизованного пользователя"
)
async def get_my_profile(
    current_user: Annotated[DomainUser, Depends(get_current_user)],
) -> UserProfile:
    """Получить профиль текущего пользователя."""
    logger.info(f"Получение профиля: user_id={current_user.user_id}")
    assert current_user.user_id is not None and current_user.created_at is not None
    return UserProfile(
        user_id=current_user.user_id,
        login=current_user.login,
        created_at=current_user.created_at,
    )