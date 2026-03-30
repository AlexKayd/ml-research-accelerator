import logging
from fastapi import APIRouter
from app.handler.report_handler import router as report_router
from app.handler.sse_handler import router as sse_router

logger = logging.getLogger(__name__)

api_router = APIRouter()

api_router.include_router(
    report_router,
    prefix="/reports",
    tags=["EDA-отчеты"],
)
api_router.include_router(
    sse_router,
    prefix="/reports",
    tags=["EDA-SSE"],
)

logger.info("API роутеры успешно зарегистрированы")