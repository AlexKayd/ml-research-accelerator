import logging
from fastapi import APIRouter
from app.handler.auth_handler import router as auth_router
from app.handler.user_handler import router as user_router
from app.handler.favorite_handler import router as favorite_router
from app.handler.dataset_handler import router as dataset_router
from app.handler.report_handler import router as report_router

logger = logging.getLogger(__name__)

api_router = APIRouter()

api_router.include_router(
    auth_router,
    prefix="/auth",
    tags=["Аутентификация"],
)

api_router.include_router(
    user_router,
    prefix="/users",
    tags=["Профиль"],
)

api_router.include_router(
    favorite_router,
    prefix="/users",
    tags=["Избранное"],
)

api_router.include_router(
    report_router,
    prefix="/users",
    tags=["История отчётов"],
)

api_router.include_router(
    dataset_router,
    prefix="/datasets",
    tags=["Датасеты"],
)

logger.info("API роутеры успешно зарегистрированы")