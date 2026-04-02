from pydantic import BaseModel, Field, ConfigDict


class MessageResponse(BaseModel):
    """Стандартный ответ с сообщением об успехе"""
    model_config = ConfigDict(from_attributes=True)
    
    message: str = Field(
        ...,
        description="Сообщение об успехе"
    )