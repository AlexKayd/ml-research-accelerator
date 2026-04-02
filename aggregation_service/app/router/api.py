import logging
from fastapi import APIRouter
from app.handler.system_handler import router as system_router

logger = logging.getLogger(__name__)

api_router = APIRouter()

api_router.include_router(
    system_router,
    tags=["System"],
)

logger.info("API роутеры успешно зарегистрированы")