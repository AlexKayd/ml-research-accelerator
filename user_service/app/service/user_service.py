import logging
from app.domain.user import UserProfile
from app.domain.interfaces import IUserRepository
from app.domain.exceptions import UserNotFoundError

logger = logging.getLogger(__name__)


class UserService:

    def __init__(self, user_repository: IUserRepository) -> None:
        self.user_repository = user_repository

    async def get_profile(self, user_id: int) -> UserProfile:
        """Получает профиль пользователя по айди"""
        logger.debug("Получение профиля пользователя: user_id=%s", user_id)

        user = await self.user_repository.get_by_id(user_id)
        if user is None:
            logger.warning("Пользователь не найден: user_id=%s", user_id)
            raise UserNotFoundError(user_id=user_id)

        logger.debug("Профиль успешно получен: user_id=%s", user_id)
        return UserProfile(
            user_id=user.user_id,
            login=user.login,
            created_at=user.created_at,
        )