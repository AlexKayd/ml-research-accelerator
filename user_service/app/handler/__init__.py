from app.handler.auth_handler import router as auth_router
from app.handler.user_handler import router as user_router
from app.handler.favorite_handler import router as favorite_router
from app.handler.dataset_handler import router as dataset_router
from app.handler.report_handler import router as report_router

__all__ = [
    "auth_router",
    "user_router",
    "favorite_router",
    "dataset_router",
    "report_router",
]