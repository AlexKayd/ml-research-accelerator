import asyncio
import importlib
import os
import sys
from dataclasses import dataclass
from datetime import datetime
from typing import AsyncIterator, Iterator
from uuid import uuid4
import pytest
import httpx
from testcontainers.postgres import PostgresContainer


def _user_service_dir() -> str:
    return os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def _ensure_sys_path() -> None:
    user_service_dir = _user_service_dir()
    if user_service_dir not in sys.path:
        sys.path.insert(0, user_service_dir)


def _ensure_base_env() -> None:
    os.environ.setdefault("CI", "1")
    os.environ.setdefault("DEBUG", "1")

    os.environ.setdefault("POSTGRES_USER", "postgres")
    os.environ.setdefault("POSTGRES_PASSWORD", "postgres")
    os.environ.setdefault("POSTGRES_HOST", "localhost")
    os.environ.setdefault("POSTGRES_PORT", "5432")
    os.environ.setdefault("POSTGRES_DB", "ml_platform_test")

    os.environ.setdefault("SECRET_KEY", "test-secret-key")
    os.environ.setdefault("ALGORITHM", "HS256")
    os.environ.setdefault("ACCESS_TOKEN_EXPIRE_MINUTES", "30")
    os.environ.setdefault("REFRESH_TOKEN_EXPIRE_DAYS", "7")

    os.environ.setdefault("CORS_ORIGINS", "http://localhost:5173")
    os.environ.setdefault("EDA_SERVICE_INTERNAL_TOKEN", "test-internal-token")
    os.environ.setdefault("MINIO_PUBLIC_BASE_URL", "http://minio.test")

_ensure_sys_path()
_ensure_base_env()


def _repo_root() -> str:
    here = os.path.abspath(os.path.dirname(__file__))
    return os.path.abspath(os.path.join(here, "..", ".."))


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
        _reload_user_service_modules()
        yield TestDbConfig(url=url, host=host, port=port, user=user, password=password, db=db)


def _reload_user_service_modules() -> None:
    for name in ("app.core.config", "app.core.database", "app.cmd.main"):
        if name in sys.modules:
            importlib.reload(sys.modules[name])


@pytest.fixture(scope="session")
async def app(test_db: TestDbConfig) -> "object":
    mod = importlib.import_module("app.cmd.main")
    return mod.app


@pytest.fixture(scope="session")
async def db_init(test_db: TestDbConfig) -> None:
    db = importlib.import_module("app.core.database")
    await db.init_db()


@pytest.fixture
async def db_session(db_init) -> AsyncIterator["object"]:
    db = importlib.import_module("app.core.database")
    maker = db.async_session_maker
    session = maker()
    try:
        yield session
        await session.commit()
    finally:
        await session.rollback()
        await session.close()


@pytest.fixture(autouse=True)
async def _clean_db(db_init) -> None:
    db = importlib.import_module("app.core.database")
    maker = db.async_session_maker
    async with maker() as s:
        from sqlalchemy import text
        await s.execute(
            text(
            """
            TRUNCATE TABLE
              users_reports,
              favorite_datasets,
              reports,
              files,
              datasets,
              users
            RESTART IDENTITY CASCADE;
            """
            )
        )
        await s.commit()


@pytest.fixture
async def http(app, db_init) -> AsyncIterator["object"]:
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


@pytest.fixture
async def user_repo(db_session):
    repo_mod = importlib.import_module("app.repository.user_repository")
    return repo_mod.UserRepository(db_session)


@pytest.fixture
async def auth_tokens(user_repo):
    from app.service.auth_service import AuthService
    from app.domain.user import UserCreate, UserLogin
    from app.core.config import settings

    svc = AuthService(
        user_repository=user_repo,
        secret_key=settings.SECRET_KEY,
        access_token_expire_minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES,
        refresh_token_expire_days=settings.REFRESH_TOKEN_EXPIRE_DAYS,
        algorithm=settings.ALGORITHM,
    )
    login = f"test_user_{uuid4().hex[:8]}"
    await svc.register(UserCreate(login=login, password="passw0rd1"))
    access, refresh, profile = await svc.login(UserLogin(login=login, password="passw0rd1"))
    return access, refresh, int(profile.user_id), profile.login


@pytest.fixture
def bearer(auth_tokens) -> dict:
    access, _refresh, _uid, _login = auth_tokens
    return {"Authorization": f"Bearer {access}"}


@pytest.fixture
async def seed_catalog(db_session, auth_tokens) -> dict:
    from sqlalchemy import func
    from app.repository.models import DatasetORM, FileORM, ReportORM

    _access, _refresh, user_id, _login = auth_tokens

    ds1 = DatasetORM(
        source="kaggle",
        external_id="k/seed-1",
        title="Seed dataset one",
        description="Health dataset",
        tags=["health", "tabular"],
        dataset_format="csv",
        dataset_size_kb=900.0,
        status="active",
        search_vector=func.to_tsvector("english", "Seed dataset one Health dataset"),
        source_updated_at=datetime.utcnow(),
    )
    db_session.add(ds1)
    await db_session.flush()

    ds1_data = FileORM(
        dataset_id=ds1.dataset_id,
        file_name="data.csv",
        file_size_kb=12.34,
        file_hash="h1",
        is_data=True,
    )
    ds1_readme = FileORM(
        dataset_id=ds1.dataset_id,
        file_name="README.md",
        file_size_kb=1.0,
        file_hash=None,
        is_data=False,
    )
    db_session.add_all([ds1_data, ds1_readme])
    await db_session.flush()

    ds2 = DatasetORM(
        source="uci",
        external_id="u/seed-2",
        title="Seed dataset two",
        description="Vehicles dataset",
        tags=["cars"],
        dataset_format="json",
        dataset_size_kb=1500.0,
        status="active",
        search_vector=func.to_tsvector("english", "Seed dataset two Vehicles dataset"),
        source_updated_at=datetime.utcnow(),
    )
    db_session.add(ds2)
    await db_session.flush()

    ds2_data = FileORM(
        dataset_id=ds2.dataset_id,
        file_name="cars.json",
        file_size_kb=12.34,
        file_hash="h2",
        is_data=True,
    )
    db_session.add(ds2_data)
    await db_session.flush()

    report = ReportORM(
        file_id=ds2_data.file_id,
        bucket_name="reports",
        object_key="u/1/r/1.html",
        input_file_hash="h2",
        status="completed",
        updated_at=datetime.utcnow(),
    )
    db_session.add(report)
    await db_session.flush()

    await db_session.commit()

    return {
        "user_id": int(user_id),
        "datasets": {"ds1": ds1, "ds2": ds2},
        "files": {"ds1_data": ds1_data, "ds1_readme": ds1_readme, "ds2_data": ds2_data},
        "reports": {"r1": report},
    }