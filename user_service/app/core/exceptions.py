import logging
from typing import Any, Dict, List
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from app.domain.exceptions import DomainException


logger = logging.getLogger(__name__)


def _clean_validation_errors(errors: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    cleaned = []
    for err in errors:
        err_copy = err.copy()
        ctx = err_copy.get('ctx')
        if ctx:
            new_ctx = {}
            for k, v in ctx.items():
                if not isinstance(v, (str, int, float, bool, type(None))):
                    new_ctx[k] = str(v)
                else:
                    new_ctx[k] = v
            err_copy['ctx'] = new_ctx
        cleaned.append(err_copy)
    return cleaned


def register_exception_handlers(app: FastAPI) -> None:
    
    @app.exception_handler(DomainException)
    async def domain_exception_handler(
        request: Request,
        exc: DomainException
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
        exc: RequestValidationError
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
        exc: Exception
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