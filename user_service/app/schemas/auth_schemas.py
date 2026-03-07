from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict, field_validator
from app.domain.user import validate_login, validate_password


class UserCreate(BaseModel):
    """Схема для регистрации нового пользователя"""
    model_config = ConfigDict(from_attributes=True)
    
    login: str = Field(
        ...,
        min_length=3,
        max_length=50,
        description="Имя пользователя для входа (3-50 символов)",
    )
    password: str = Field(
        ...,
        min_length=8,
        description="Пароль (минимум 8 символов)"
    )
    
    @field_validator('login')
    @classmethod
    def validate_login_format(cls, value: str) -> str:
        """Проверяет формат логина через функцию из domain слоя"""
        validate_login(value)
        return value
    
    @field_validator('password')
    @classmethod
    def validate_password_complexity(cls, value: str) -> str:
        """Проверяет сложность пароля через функцию из domain слоя"""
        validate_password(value)
        return value


class UserLogin(BaseModel):
    """Схема для входа пользователя в систему"""
    model_config = ConfigDict(from_attributes=True)
    
    login: str = Field(
        ...,
        description="Имя пользователя"
    )
    password: str = Field(
        ...,
        description="Пароль"
    )


class TokenRefresh(BaseModel):
    """Схема для обновления токенов"""
    model_config = ConfigDict(from_attributes=True)
    
    refresh_token: str = Field(
        ...,
        description="Refresh JWT токен"
    )


class UserResponse(BaseModel):
    """Ответ API с данными пользователя"""
    model_config = ConfigDict(from_attributes=True)
    
    user_id: int = Field(
        ...,
        description="Уникальный идентификатор пользователя"
    )
    login: str = Field(
        ...,
        description="Имя пользователя"
    )
    created_at: datetime = Field(
        ...,
        description="Дата регистрации"
    )


class TokenResponse(BaseModel):
    """Ответ API с токенами"""
    model_config = ConfigDict(from_attributes=True)
    
    access_token: str = Field(
        ...,
        description="Access JWT токен"
    )
    refresh_token: str = Field(
        ...,
        description="Refresh JWT токен"
    )
    token_type: str = Field(
        default="bearer",
        description="Тип токена"
    )
    user: UserResponse = Field(
        ...,
        description="Данные пользователя"
    )