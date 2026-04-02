import logging
from typing import Optional
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from app.domain.user import User
from app.domain.interfaces import IUserRepository
from app.domain.exceptions import UserAlreadyExistsError
from app.repository.models import UserORM

logger = logging.getLogger(__name__)


class UserRepository(IUserRepository):
    
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
    
    async def create(self, user: User) -> User:
        """Создаёт нового пользователя в бд"""
        logger.info(f"Попытка создания пользователя с логином: {user.login}")

        exists = await self.exists_by_login(user.login)
        if exists:
            logger.warning(f"Попытка создания уже существующего пользователя: {user.login}")
            raise UserAlreadyExistsError(login=user.login)
        
        user_orm = UserORM(
            login=user.login,
            hashed_password=user.hashed_password,
        )
        
        self.session.add(user_orm)
        try:
            await self.session.flush()
        except IntegrityError as e:

            logger.warning("Пользователь уже существует (IntegrityError): login=%s", user.login)
            raise UserAlreadyExistsError(login=user.login) from e
        
        logger.info(f"Пользователь успешно создан: user_id={user_orm.user_id}, login={user_orm.login}")
        return User(
            user_id=user_orm.user_id,
            login=user_orm.login,
            hashed_password=user_orm.hashed_password,
            created_at=user_orm.created_at
        )
    
    async def get_by_id(self, user_id: int) -> Optional[User]:
        """Получает пользователя по айди"""
        logger.debug(f"Поиск пользователя по user_id: {user_id}")
        
        query = select(UserORM).where(UserORM.user_id == user_id)
        result = await self.session.execute(query)
        user_orm = result.scalar_one_or_none()
        
        if user_orm is None:
            logger.debug(f"Пользователь не найден: user_id={user_id}")
            return None
        
        logger.debug(f"Пользователь найден: user_id={user_orm.user_id}, login={user_orm.login}")
        
        return User(
            user_id=user_orm.user_id,
            login=user_orm.login,
            hashed_password=user_orm.hashed_password,
            created_at=user_orm.created_at
        )
    
    async def get_by_login(self, login: str) -> Optional[User]:
        """Получает пользователя по логину"""
        logger.debug(f"Поиск пользователя по логину: {login}")
        
        query = select(UserORM).where(UserORM.login == login)
        result = await self.session.execute(query)
        user_orm = result.scalar_one_or_none()
        
        if user_orm is None:
            logger.debug(f"Пользователь не найден: login={login}")
            return None
        
        logger.debug(f"Пользователь найден: user_id={user_orm.user_id}, login={user_orm.login}")
        return User(
            user_id=user_orm.user_id,
            login=user_orm.login,
            hashed_password=user_orm.hashed_password,
            created_at=user_orm.created_at
        )
    
    async def exists_by_login(self, login: str) -> bool:
        """Проверяет существование пользователя с данным логином"""
        logger.debug(f"Проверка существования логина: {login}")
        
        query = select(UserORM.user_id).where(UserORM.login == login)
        result = await self.session.execute(query)
        user_id = result.scalar_one_or_none()
        
        exists = user_id is not None
        logger.debug(f"Логин {'существует' if exists else 'не существует'}: {login}")
        return exists