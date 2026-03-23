from typing import Optional, Any


class DomainException(Exception):
    
    def __init__(
        self,
        message: str,
        code: str,
        details: Optional[dict[str, Any]] = None,
        status_code: int = 400
    ) -> None:
        super().__init__(message)
        self.message = message
        self.code = code
        self.details = details or {}
        self.status_code = status_code
    
    def to_dict(self) -> dict[str, Any]:
        return {
            "status": "error",
            "code": self.code,
            "message": self.message,
            "details": self.details
        }
    
    def __str__(self) -> str:
        return f"[{self.code}] {self.message}"


class UserAlreadyExistsError(DomainException):
    """Исключение при попытке регистрации с занятым логином"""
    
    def __init__(self, login: str) -> None:
        super().__init__(
            message=f"Пользователь с логином '{login}' уже существует",
            code="USER_ALREADY_EXISTS",
            details={"login": login},
            status_code=409
        )


class UserNotFoundError(DomainException):
    """Исключение при отсутствии пользователя"""
    
    def __init__(self, user_id: Optional[int] = None, login: Optional[str] = None) -> None:
        details: dict[str, Any] = {}
        if user_id is not None:
            details["user_id"] = user_id
        if login is not None:
            details["login"] = login
        
        super().__init__(
            message="Пользователь не найден",
            code="USER_NOT_FOUND",
            details=details,
            status_code=404
        )


class InvalidCredentialsError(DomainException):
    """Исключение при неверных данных"""
    
    def __init__(self) -> None:
        super().__init__(
            message="Неверный логин или пароль",
            code="INVALID_CREDENTIALS",
            details={},
            status_code=401
        )


class TokenExpiredError(DomainException):
    """Исключение при истёкшем токене"""
    
    def __init__(self, token_type: str = "access") -> None:
        super().__init__(
            message=f"Срок действия {token_type} токена истёк",
            code="TOKEN_EXPIRED",
            details={"token_type": token_type},
            status_code=401
        )


class InvalidTokenError(DomainException):
    """Исключение при невалидном токене"""
    
    def __init__(self, reason: Optional[str] = None) -> None:
        details: dict[str, Any] = {}
        if reason:
            details["reason"] = reason
        
        super().__init__(
            message="Невалидный токен",
            code="INVALID_TOKEN",
            details=details,
            status_code=401
        )


class DatasetNotFoundError(DomainException):
    """Исключение при отсутствии датасета"""
    
    def __init__(self, dataset_id: int) -> None:
        super().__init__(
            message="Датасет не найден",
            code="DATASET_NOT_FOUND",
            details={"dataset_id": dataset_id},
            status_code=404
        )


class FavoriteAlreadyExistsError(DomainException):
    """Исключение при повторном добавлении датасета в избранное"""
    
    def __init__(self, user_id: int, dataset_id: int) -> None:
        super().__init__(
            message="Датасет уже находится в избранном",
            code="FAVORITE_ALREADY_EXISTS",
            details={
                "user_id": user_id,
                "dataset_id": dataset_id
            },
            status_code=409
        )


class FavoriteNotFoundError(DomainException):
    """Исключение при отсутствии связи в избранном"""
    
    def __init__(self, user_id: int, dataset_id: int) -> None:
        super().__init__(
            message="Датасет не найден в избранном",
            code="FAVORITE_NOT_FOUND",
            details={
                "user_id": user_id,
                "dataset_id": dataset_id
            },
            status_code=404
        )


class ReportAlreadyExistsError(DomainException):
    """Исключение при повторном сохранении отчёта в историю"""

    def __init__(self, user_id: int, report_id: int) -> None:
        super().__init__(
            message="Отчёт уже находится в истории",
            code="REPORT_ALREADY_EXISTS",
            details={
                "user_id": user_id,
                "report_id": report_id,
            },
            status_code=409,
        )


class ReportNotFoundError(DomainException):
    """Исключение при отсутствии отчёта"""
    
    def __init__(self, report_id: int) -> None:
        super().__init__(
            message="Отчёт не найден",
            code="REPORT_NOT_FOUND",
            details={"report_id": report_id},
            status_code=404
        )


class ReportNotInHistoryError(DomainException):
    """Исключение при отсутствии отчёта в истории пользователя"""
    
    def __init__(self, user_id: int, report_id: int) -> None:
        super().__init__(
            message="Отчёт не найден в истории",
            code="REPORT_NOT_IN_HISTORY",
            details={
                "user_id": user_id,
                "report_id": report_id
            },
            status_code=404
        )