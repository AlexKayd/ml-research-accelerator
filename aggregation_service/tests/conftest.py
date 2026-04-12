import asyncio
import importlib
import os
import sys
from dataclasses import dataclass
from typing import AsyncIterator, Iterator
from unittest.mock import AsyncMock
import httpx
import pytest
from sqlalchemy import text
from testcontainers.postgres import PostgresContainer


def _aggregation_service_dir() -> str:
    return os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def _ensure_sys_path() -> None:
    d = _aggregation_service_dir()
    if d not in sys.path:
        sys.path.insert(0, d)


def _ensure_base_env() -> None:
    os.environ.setdefault("CI", "1")
    os.environ.setdefault("DEBUG", "0")
    os.environ.setdefault("LOG_LEVEL", "WARNING")

    os.environ.setdefault("POSTGRES_USER", "postgres")
    os.environ.setdefault("POSTGRES_PASSWORD", "postgres")
    os.environ.setdefault("POSTGRES_HOST", "localhost")
    os.environ.setdefault("POSTGRES_PORT", "5432")
    os.environ.setdefault("POSTGRES_DB", "ml_platform_agg_test")

    os.environ.setdefault("CELERY_BROKER_URL", "redis://localhost:6379/0")
    os.environ.setdefault("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")
    os.environ.setdefault("CELERY_EDA_QUEUE", "eda")

    os.environ.setdefault("CORS_ORIGINS", "http://localhost:5173")


_ensure_sys_path()
_ensure_base_env()


@pytest.fixture(autouse=True)
def _no_async_sleep(monkeypatch) -> None:
    monkeypatch.setattr(asyncio, "sleep", AsyncMock(return_value=None))


def _reload_aggregation_modules() -> None:
    for name in (
        "app.core.config",
        "app.core.database",
        "app.core.celery_config",
        "app.cmd.main",
    ):
        mod = sys.modules.get(name)
        if mod is not None:
            importlib.reload(mod)


@dataclass
class TestDbConfig:
    url: str
    host: str
    port: int
    user: str
    password: str
    db: str


@pytest.fixture(scope="session")
def test_db() -> Iterator[TestDbConfig]:
    with PostgresContainer("postgres:17-alpine") as pg:
        host = pg.get_container_host_ip()
        port = int(pg.get_exposed_port(5432))
        user = pg.username
        password = pg.password
        db = pg.dbname
        url = f"postgresql+asyncpg://{user}:{password}@{host}:{port}/{db}"

        os.environ["POSTGRES_USER"] = user
        os.environ["POSTGRES_PASSWORD"] = password
        os.environ["POSTGRES_HOST"] = host
        os.environ["POSTGRES_PORT"] = str(port)
        os.environ["POSTGRES_DB"] = db

        _reload_aggregation_modules()
        yield TestDbConfig(url=url, host=host, port=port, user=user, password=password, db=db)


@pytest.fixture(scope="session")
async def db_init(test_db: TestDbConfig) -> None:
    db = importlib.import_module("app.core.database")
    await db.init_db()


@pytest.fixture(scope="session")
async def app(test_db: TestDbConfig):
    mod = importlib.import_module("app.cmd.main")
    return mod.app


@pytest.fixture
async def db_session(db_init) -> AsyncIterator[object]:
    db = importlib.import_module("app.core.database")
    maker = db.async_session_factory
    session = maker()
    try:
        yield session
        await session.commit()
    except Exception:
        await session.rollback()
        raise
    finally:
        await session.close()


@pytest.fixture(autouse=True)
async def _clean_db(db_init) -> None:
    db = importlib.import_module("app.core.database")
    maker = db.async_session_factory
    async with maker() as s:
        await s.execute(text("TRUNCATE TABLE files, datasets RESTART IDENTITY CASCADE;"))
        await s.commit()


@pytest.fixture
async def http(app, db_init):
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        yield client