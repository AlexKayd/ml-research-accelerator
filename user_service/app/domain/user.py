from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
import re
import time


def validate_password(password: str) -> None:
    """Валидирует сложность пароля
        - Минимум 8 символов
        - Хотя бы одна буква
        - Хотя бы одна цифра """

    if not password or len(password) < 8:
        raise ValueError("Пароль должен содержать минимум 8 символов")
    
    has_letter = any(c.isalpha() for c in password)
    has_digit = any(c.isdigit() for c in password)
    
    if not has_letter or not has_digit:
        raise ValueError( "Пароль должен содержать хотя бы одну букву и одну цифру")


def validate_login(login: str) -> None:
    """Валидирует формат логина
        - 3-50 символов
        - Только русский, англицский, цифры, подчёркивания"""

    if not login or len(login) < 3:
        raise ValueError("Логин должен содержать минимум 3 символа")
    
    if len(login) > 50:
        raise ValueError("Логин не должен превышать 50 символов")
    
    if not re.match(r'^[a-zA-Zа-яА-ЯёЁ0-9_]+$', login):
        raise ValueError("Логин должен содержать только английские или русские буквы, цифры и подчёркивания")


@dataclass
class User:
    login: str
    hashed_password: str
    user_id: Optional[int] = None
    created_at: Optional[datetime] = None
    
    def __post_init__(self) -> None:
        validate_login(self.login)
    
    def to_dict(self) -> dict:
        return {
            "user_id": self.user_id,
            "login": self.login,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
    
    def __str__(self) -> str:
        return f"User(user_id={self.user_id}, login={self.login})"
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, User):
            return False

        if self.user_id is None or other.user_id is None:
            return False
        return self.user_id == other.user_id
    
    def __hash__(self) -> int:
        return hash(self.user_id) if self.user_id is not None else 0


@dataclass
class UserCreate:
    login: str
    password: str
    
    def __post_init__(self) -> None:
        validate_login(self.login)
        validate_password(self.password)


@dataclass
class UserLogin:
    login: str
    password: str
    
    def __post_init__(self) -> None:
        if not self.login:
            raise ValueError("Логин не может быть пустым")
        
        if not self.password:
            raise ValueError("Пароль не может быть пустым")


@dataclass
class UserProfile:
    user_id: int
    login: str
    created_at: datetime
    
    def to_dict(self) -> dict:
        return {
            "user_id": self.user_id,
            "login": self.login,
            "created_at": self.created_at.isoformat()
        }


@dataclass
class TokenData:
    user_id: int
    token_type: str
    exp: Optional[int] = None
    
    def is_expired(self) -> bool:
        if self.exp is None:
            return False
        return time.time() > self.exp


@dataclass
class FavoriteDataset:
    user_id: int
    dataset_id: int
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, FavoriteDataset):
            return False
        return (
            self.user_id == other.user_id and 
            self.dataset_id == other.dataset_id
        )
    
    def __hash__(self) -> int:
        return hash((self.user_id, self.dataset_id))


@dataclass
class UserReport:
    """Связь пользователя с отчётом в истории (таблица users_reports)."""

    user_id: int
    report_id: int

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, UserReport):
            return False
        return (
            self.user_id == other.user_id
            and self.report_id == other.report_id
        )

    def __hash__(self) -> int:
        return hash((self.user_id, self.report_id))