import logging
from typing import Any, Dict, List
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.domain.exceptions import DomainException

logger = logging.getLogger(__name__)


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
        return f"Строка должна содержать минимум {min_length} символов" if min_length is not None else "Слишком короткая строка"
    if err_type == "string_too_long":
        max_length = ctx.get("max_length")
        return f"Строка не должна превышать {max_length} символов" if max_length is not None else "Слишком длинная строка"

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

    if err_type == "bool_parsing" or err_type == "bool_type":
        return "Значение должно быть булевым (true/false)"

    if err_type in ("list_type", "list_parsing"):
        return "Значение должно быть списком"
    if err_type == "list_too_short":
        min_length = ctx.get("min_length")
        return f"Список должен содержать минимум {min_length} элементов" if min_length is not None else "Слишком короткий список"
    if err_type == "list_too_long":
        max_length = ctx.get("max_length")
        return f"Список не должен содержать более {max_length} элементов" if max_length is not None else "Слишком длинный список"

    if err_type == "is_instance_of":
        expected = ctx.get("class")
        return f"Неверный тип данных, ожидается {expected}" if expected is not None else "Неверный тип данных"

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
                if not isinstance(v, (str, int, float, bool, type(None))):
                    new_ctx[k] = str(v)
                else:
                    new_ctx[k] = v
            err_copy["ctx"] = new_ctx

        cleaned.append(err_copy)
    return cleaned


def register_exception_handlers(app: FastAPI) -> None:

    @app.exception_handler(DomainException)
    async def domain_exception_handler(
        request: Request,
        exc: DomainException,
    ) -> JSONResponse:
        logger.warning(
            f"Доменное исключение: {exc.code} - {exc.message} "
            f"(url={request.url}, method={request.method})"
        )

        return JSONResponse(
            status_code=exc.status_code,
            content={
                "status": "error",
                "code": exc.code,
                "message": exc.message,
                "details": exc.details,
            },
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request,
        exc: RequestValidationError,
    ) -> JSONResponse:
        raw_errors = exc.errors()
        clean_errors = _clean_validation_errors(raw_errors)

        logger.warning(
            f"Ошибка валидации запроса: {clean_errors} "
            f"(url={request.url}, method={request.method})"
        )

        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "status": "error",
                "code": "VALIDATION_ERROR",
                "message": "Ошибка валидации входных данных",
                "details": {"errors": clean_errors},
            },
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

        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "status": "error",
                "code": "INTERNAL_ERROR",
                "message": "Внутренняя ошибка сервера",
                "details": {},
            },
        )

    logger.info("Глобальные обработчики исключений зарегистрированы")