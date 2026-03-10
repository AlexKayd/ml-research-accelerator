from typing import Optional, Any, List
from pydantic import BaseModel, Field, ConfigDict


class MessageResponse(BaseModel):
    """Стандартный ответ с сообщением об успехе"""
    model_config = ConfigDict(from_attributes=True)
    
    message: str = Field(
        ...,
        description="Сообщение об успехе"
    )


class ErrorResponse(BaseModel):
    """Стандартизированный ответ с ошибкой"""
    model_config = ConfigDict(from_attributes=True)
    
    status: str = Field(
        default="error",
        description="Статус ответа"
    )
    code: str = Field(
        ...,
        description="Код ошибки"
    )
    message: str = Field(
        ...,
        description="Сообщение об ошибке"
    )
    details: Optional[dict[str, Any]] = Field(
        None,
        description="Детали ошибки"
    )


class PaginatedResponse(BaseModel):
    """Ответ API с пагинацией"""
    model_config = ConfigDict(from_attributes=True)
    
    items: List[Any] = Field(
        ...,
        description="Список результатов"
    )
    total: int = Field(
        ...,
        description="Общее количество элементов"
    )
    limit: int = Field(
        ...,
        description="Количество элементов на странице"
    )
    offset: int = Field(
        ...,
        description="Смещение"
    )
    has_more: bool = Field(
        ...,
        description="Есть ли ещё результаты"
    )