from pydantic import ConfigDict
from app.schemas.auth_schemas import UserResponse


class UserProfile(UserResponse):
    """Расширенный профиль пользователя, может включать дополнительные поля в будущем"""
    model_config = ConfigDict(from_attributes=True)