import logging
from typing import Tuple
from jose import JWTError, ExpiredSignatureError
from app.domain.user import User, UserCreate, UserLogin, UserProfile
from app.domain.interfaces import IUserRepository
from app.domain.exceptions import (
    UserAlreadyExistsError,
    UserNotFoundError,
    InvalidCredentialsError,
    TokenExpiredError,
    InvalidTokenError
)
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token
)

logger = logging.getLogger(__name__)


class AuthService:

    def __init__(
        self,
        user_repository: IUserRepository,
        secret_key: str,
        access_token_expire_minutes: int = 30,
        refresh_token_expire_days: int = 7,
        algorithm: str = "HS256"
    ) -> None:
        self.user_repository = user_repository
        self.secret_key = secret_key
        self.access_token_expire_minutes = access_token_expire_minutes
        self.refresh_token_expire_days = refresh_token_expire_days
        self.algorithm = algorithm

    async def register(self, user_create: UserCreate) -> User:
        """Регистрирует нового пользователя в системе"""
        logger.info(f"Регистрация нового пользователя: login={user_create.login}")
        
        exists = await self.user_repository.exists_by_login(user_create.login)
        if exists:
            logger.warning(f"Попытка регистрации занятого логина: {user_create.login}")
            raise UserAlreadyExistsError(login=user_create.login)
        
        hashed_password = hash_password(user_create.password)
        logger.debug(f"Пароль успешно хеширован для пользователя: {user_create.login}")
        
        user = User(
            user_id=None,
            login=user_create.login,
            hashed_password=hashed_password,
        )
        
        created_user = await self.user_repository.create(user)
        
        logger.info(f"Пользователь успешно зарегистрирован: user_id={created_user.user_id}")
        return created_user

    async def login(self, user_login: UserLogin) -> Tuple[str, str, UserProfile]:
        """Аутентифицирует пользователя и генерирует токены"""
        logger.info(f"Попытка входа пользователя: login={user_login.login}")
        
        user = await self.user_repository.get_by_login(user_login.login)
        if user is None:
            logger.warning(f"Пользователь не найден при входе: {user_login.login}")
            raise UserNotFoundError(login=user_login.login)
        
        password_valid = verify_password(user_login.password, user.hashed_password)
        if not password_valid:
            logger.warning(f"Неверный пароль для пользователя: {user_login.login}")
            raise InvalidCredentialsError()
        
        logger.debug(f"Пароль успешно проверен для пользователя: user_id={user.user_id}")
        
        access_token = create_access_token(
            user_id=user.user_id,
            secret_key=self.secret_key,
            expire_minutes=self.access_token_expire_minutes,
            algorithm=self.algorithm
        )
        
        refresh_token = create_refresh_token(
            user_id=user.user_id,
            secret_key=self.secret_key,
            expire_days=self.refresh_token_expire_days,
            algorithm=self.algorithm
        )
        
        logger.info(f"Пользователь успешно вошёл в систему: user_id={user.user_id}")
        
        user_profile = UserProfile(
            user_id=user.user_id,
            login=user.login,
            created_at=user.created_at
        )
        return access_token, refresh_token, user_profile

    async def refresh_tokens(
        self, 
        refresh_token: str
    ) -> Tuple[str, str, UserProfile]:
        """Обновляет access-токен по refresh-токену. Refresh-токен остаётся неизменным"""
        logger.info("Попытка обновления токенов")
        
        try:
            token_data = decode_token(
                token=refresh_token,
                secret_key=self.secret_key,
                algorithm=self.algorithm
            )
        except ExpiredSignatureError:
            logger.warning(f"Refresh токен истёк")
            raise TokenExpiredError(token_type="refresh")
        except JWTError as e:
            logger.warning(f"Невалидный refresh токен: {str(e)}")
            raise InvalidTokenError(reason="Некорректный формат токена")
        
        if token_data.token_type != "refresh":
            logger.warning(f"Неверный тип токена: {token_data.token_type}")
            raise InvalidTokenError(reason="Требуется refresh токен")
        
        if token_data.is_expired():
            logger.warning(f"Refresh токен истёк (domain check): user_id={token_data.user_id}")
            raise TokenExpiredError(token_type="refresh")

        user = await self.user_repository.get_by_id(token_data.user_id)
        if user is None:
            logger.warning(f"Пользователь не найден при обновлении токена: user_id={token_data.user_id}")
            raise UserNotFoundError(user_id=token_data.user_id)
        
        new_access_token = create_access_token(
            user_id=user.user_id,
            secret_key=self.secret_key,
            expire_minutes=self.access_token_expire_minutes,
            algorithm=self.algorithm
        )
        
        user_profile = UserProfile(
            user_id=user.user_id,
            login=user.login,
            created_at=user.created_at
        )
        logger.info(f"Токены успешно обновлены: user_id={user.user_id}")
        return new_access_token, refresh_token, user_profile

    async def get_current_user(self, access_token: str) -> UserProfile:
        """Получает профиль текущего пользователя из access токена"""
        logger.debug("Получение данных текущего пользователя из access токена")
        
        try:
            token_data = decode_token(
                token=access_token,
                secret_key=self.secret_key,
                algorithm=self.algorithm
            )
        except ExpiredSignatureError:
            logger.warning(f"Access токен истёк")
            raise TokenExpiredError(token_type="access")
        except JWTError as e:
            logger.warning(f"Невалидный access токен: {str(e)}")
            raise InvalidTokenError(reason="Некорректный формат токена")
        
        if token_data.token_type != "access":
            logger.warning(f"Неверный тип токена: {token_data.token_type}")
            raise InvalidTokenError(reason="Требуется access токен")
        
        if token_data.is_expired():
            logger.warning(f"Access токен истёк (domain check): user_id={token_data.user_id}")
            raise TokenExpiredError(token_type="access")
        
        user = await self.user_repository.get_by_id(token_data.user_id)
        if user is None:
            logger.warning(f"Пользователь не найден: user_id={token_data.user_id}")
            raise UserNotFoundError(user_id=token_data.user_id)
        
        logger.debug(f"Пользователь успешно загружен: user_id={user.user_id}")
        return UserProfile(
            user_id=user.user_id,
            login=user.login,
            created_at=user.created_at
        )