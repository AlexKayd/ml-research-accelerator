import logging
from typing import Any, Dict, List
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from app.core.config import settings
from app.domain.exceptions import (
    DomainException,
    InvalidEventError,
    InvalidReportError,
    ReportNotFoundError,
    ReportDeletingError,
    FileNotFoundInArchiveError,
    UserServiceUnavailableError,
    UserServiceReportAttachFailedError,
    DatabaseError,
    StorageError,
    ReportGenerationError,
)

logger = logging.getLogger(__name__)


def _error_payload(
    *,
    code: str,
    message: str,
    details: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    return {
        "status": "error",
        "code": code,
        "message": message,
        "details": details or {},
    }


def _localize_pydantic_error(err: Dict[str, Any]) -> str:
    err_type = err.get("type") or ""
    msg = err.get("msg") or ""
    ctx = err.get("ctx") or {}

    if isinstance(msg, str) and msg.startswith("Value error, "):
        return msg[len("Value error, ") :]

    if err_type.startswith("missing"):
        return "Обязательное поле"

    if err_type.startswith("string_type"):
        return "Значение должно быть строкой"
    if err_type == "string_too_short":
        min_length = ctx.get("min_length")
        return (
            f"Строка должна содержать минимум {min_length} символов"
            if min_length is not None
            else "Слишком короткая строка"
        )
    if err_type == "string_too_long":
        max_length = ctx.get("max_length")
        return (
            f"Строка не должна превышать {max_length} символов"
            if max_length is not None
            else "Слишком длинная строка"
        )

    if err_type in ("int_type", "int_parsing"):
        return "Значение должно быть целым числом"
    if err_type in ("float_type", "float_parsing", "number_type"):
        return "Значение должно быть числом"
    if err_type == "greater_than_equal":
        ge = ctx.get("ge")
        return f"Значение должно быть больше либо равно {ge}" if ge is not None else "Значение слишком маленькое"
    if err_type == "less_than_equal":
        le = ctx.get("le")
        return f"Значение должно быть меньше либо равно {le}" if le is not None else "Значение слишком большое"

    if err_type in ("list_type", "list_parsing"):
        return "Значение должно быть списком"

    return msg


def _clean_validation_errors(errors: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    cleaned: List[Dict[str, Any]] = []
    for err in errors:
        err_copy = err.copy()
        err_copy["msg"] = _localize_pydantic_error(err_copy)

        ctx = err_copy.get("ctx")
        if ctx:
            new_ctx: Dict[str, Any] = {}
            for k, v in ctx.items():
                new_ctx[k] = v if isinstance(v, (str, int, float, bool, type(None))) else str(v)
            err_copy["ctx"] = new_ctx

        cleaned.append(err_copy)
    return cleaned


def _domain_to_http(exc: DomainException) -> tuple[int, str]:
    if isinstance(exc, ReportNotFoundError):
        return status.HTTP_404_NOT_FOUND, "REPORT_NOT_FOUND"
    if isinstance(exc, ReportDeletingError):
        return status.HTTP_410_GONE, "REPORT_DELETING"
    if isinstance(exc, (InvalidReportError, InvalidEventError)):
        return status.HTTP_422_UNPROCESSABLE_ENTITY, "VALIDATION_ERROR"
    if isinstance(exc, FileNotFoundInArchiveError):
        return status.HTTP_404_NOT_FOUND, "FILE_NOT_FOUND_IN_ARCHIVE"
    if isinstance(exc, UserServiceUnavailableError):
        return status.HTTP_503_SERVICE_UNAVAILABLE, "USER_SERVICE_UNAVAILABLE"
    if isinstance(exc, UserServiceReportAttachFailedError):
        return status.HTTP_502_BAD_GATEWAY, "USER_SERVICE_ATTACH_FAILED"
    if isinstance(exc, (DatabaseError, StorageError, ReportGenerationError)):
        return status.HTTP_500_INTERNAL_SERVER_ERROR, exc.__class__.__name__.upper()
    return status.HTTP_400_BAD_REQUEST, exc.__class__.__name__.upper()


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(DomainException)
    async def domain_exception_handler(
        request: Request,
        exc: DomainException,
    ) -> JSONResponse:
        http_status, code = _domain_to_http(exc)
        logger.warning(
            "Доменное исключение: %s (code=%s url=%s method=%s)",
            exc.__class__.__name__,
            code,
            request.url,
            request.method,
        )
        return JSONResponse(
            status_code=http_status,
            content=_error_payload(code=code, message=exc.message, details=exc.details),
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request,
        exc: RequestValidationError,
    ) -> JSONResponse:
        clean_errors = _clean_validation_errors(exc.errors())
        logger.warning(
            "Ошибка валидации запроса: %s (url=%s method=%s)",
            clean_errors,
            request.url,
            request.method,
        )
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=_error_payload(
                code="VALIDATION_ERROR",
                message="Ошибка валидации входных данных",
                details={"errors": clean_errors},
            ),
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(
        request: Request,
        exc: Exception,
    ) -> JSONResponse:
        logger.error(
            f"Необработанное исключение: {str(exc)} "
            f"(url={request.url}, method={request.method})",
            exc_info=True,
        )
        details = {"error": str(exc)} if settings.DEBUG else {}
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=_error_payload(
                code="INTERNAL_ERROR",
                message="Внутренняя ошибка сервера",
                details=details,
            ),
        )

    logger.info("Глобальные обработчики исключений зарегистрированы")