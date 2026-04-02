import logging
from typing import Annotated
from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.security import get_current_token_data
from app.domain.interfaces import IUserRepository
from app.domain.user import TokenData, User as DomainUser
from app.repository.user_repository import UserRepository

logger = logging.getLogger(__name__)


def get_user_repository(session: AsyncSession = Depends(get_db)) -> IUserRepository:
    return UserRepository(session)


async def get_current_user(
    token_data: Annotated[TokenData, Depends(get_current_token_data)],
    user_repository: Annotated[IUserRepository, Depends(get_user_repository)],
) -> DomainUser:
    """Получает текущего пользователя из токена"""
    user = await user_repository.get_by_id(token_data.user_id)
    if user is None:
        logger.warning("Пользователь не найден: user_id=%s", token_data.user_id)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Невалидный токен",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user