from pydantic import ConfigDict
from app.schemas.auth_schemas import UserResponse


class UserProfile(UserResponse):
    model_config = ConfigDict(from_attributes=True)