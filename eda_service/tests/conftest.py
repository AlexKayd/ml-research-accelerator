import importlib
import os
import sys
from dataclasses import dataclass
from typing import AsyncIterator, Iterator
from uuid import uuid4


def _eda_service_dir() -> str:
    return os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def _ensure_sys_path() -> None:
    d = _eda_service_dir()
    if d not in sys.path:
        sys.path.insert(0, d)


def _ensure_tests_dir_on_path() -> None:
    t = os.path.dirname(os.path.abspath(__file__))
    if t not in sys.path:
        sys.path.append(t)


def _ensure_base_env() -> None:
    os.environ.setdefault("CI", "1")
    os.environ.setdefault("DEBUG", "0")
    os.environ.setdefault("LOG_LEVEL", "WARNING")

    os.environ.setdefault("POSTGRES_USER", "postgres")
    os.environ.setdefault("POSTGRES_PASSWORD", "postgres")
    os.environ.setdefault("POSTGRES_HOST", "localhost")
    os.environ.setdefault("POSTGRES_PORT", "5432")
    os.environ.setdefault("POSTGRES_DB", "ml_platform_eda_test")

    os.environ.setdefault("REDIS_URL", "redis://localhost:6379/1")

    os.environ.setdefault("SECRET_KEY", "test-secret-key")
    os.environ.setdefault("ALGORITHM", "HS256")

    os.environ.setdefault("GENERATE_RATE_LIMIT_PER_MINUTE", "5")

    os.environ.setdefault("MINIO_ENDPOINT", "localhost:9000")
    os.environ.setdefault("MINIO_ACCESS_KEY", "minioadmin")
    os.environ.setdefault("MINIO_SECRET_KEY", "minioadmin")
    os.environ.setdefault("MINIO_SECURE", "0")
    os.environ.setdefault("MINIO_REPORTS_BUCKET", "eda-reports")
    os.environ.setdefault("MINIO_PUBLIC_BASE_URL", "http://minio.test")
    os.environ.setdefault("MINIO_REPORTS_BUCKET_ANONYMOUS_READ", "0")

    os.environ.setdefault("EDA_SERVICE_INTERNAL_TOKEN", "test-internal-token")
    os.environ.setdefault("USER_SERVICE_URL", "http://user-service.test")

    os.environ.setdefault("CORS_ORIGINS", "http://localhost:5173")


_ensure_sys_path()
_ensure_tests_dir_on_path()
_ensure_base_env()

import httpx
import pytest
import redis.asyncio as redis_async
from datetime import datetime, timedelta, timezone
from jose import jwt
from sqlalchemy import func, text
from testcontainers.core.container import DockerContainer
from testcontainers.postgres import PostgresContainer
from app.repository.models import DatasetORM, FileORM
from streaming_asgi_transport import StreamingBodyASGITransport
from app.core.config import get_settings


def _reload_eda_modules() -> None:
    order = (
        "app.core.config",
        "app.core.minio",
        "app.core.jwt_auth",
        "app.handler.sse_handler",
        "app.service.report_subscribers_redis",
        "app.service.report_generator",
        "app.service.aggregation_service",
        "app.celery.tasks",
        "app.service.report_service",
        "app.handler.report_handler",
        "app.router.api",
        "app.router",
        "app.core.database",
        "app.core.celery_config",
        "app.cmd.main",
    )
    for name in order:
        mod = sys.modules.get(name)
        if mod is not None:
            importlib.reload(mod)


@dataclass
class TestDbConfig:
    host: str
    port: int
    user: str
    password: str
    db: str


@dataclass
class TestRedisConfig:
    host: str
    port: int
    url: str


@pytest.fixture(scope="session")
def test_db() -> Iterator[TestDbConfig]:
    with PostgresContainer("postgres:17-alpine") as pg:
        host = pg.get_container_host_ip()
        port = int(pg.get_exposed_port(5432))
        user = pg.username
        password = pg.password
        db = pg.dbname

        os.environ["POSTGRES_HOST"] = host
        os.environ["POSTGRES_PORT"] = str(port)
        os.environ["POSTGRES_USER"] = user
        os.environ["POSTGRES_PASSWORD"] = password
        os.environ["POSTGRES_DB"] = db

        _reload_eda_modules()
        yield TestDbConfig(host=host, port=port, user=user, password=password, db=db)


@pytest.fixture(scope="session")
def test_redis() -> Iterator[TestRedisConfig]:
    c = DockerContainer("redis:7-alpine").with_exposed_ports(6379)
    c.start()
    try:
        host = c.get_container_host_ip()
        port = int(c.get_exposed_port(6379))
        url = f"redis://{host}:{port}/1"
        os.environ["REDIS_URL"] = url
        os.environ["CELERY_BROKER_URL"] = url
        os.environ["CELERY_RESULT_BACKEND"] = url
        _reload_eda_modules()
        yield TestRedisConfig(host=host, port=port, url=url)
    finally:
        try:
            c.stop()
        except Exception:
            pass


@pytest.fixture(scope="session")
def test_minio() -> Iterator[dict]:

    access = "minioadmin"
    secret = "minioadmin"
    bucket = "eda-reports"

    c = (
        DockerContainer("minio/minio:RELEASE.2024-01-16T16-07-38Z")
        .with_env("MINIO_ROOT_USER", access)
        .with_env("MINIO_ROOT_PASSWORD", secret)
        .with_command("server /data --console-address :9001")
        .with_exposed_ports(9000, 9001)
    )
    c.start()
    try:
        host = c.get_container_host_ip()
        port = int(c.get_exposed_port(9000))

        os.environ["MINIO_ENDPOINT"] = f"{host}:{port}"
        os.environ["MINIO_ACCESS_KEY"] = access
        os.environ["MINIO_SECRET_KEY"] = secret
        os.environ["MINIO_SECURE"] = "0"
        os.environ["MINIO_REPORTS_BUCKET"] = bucket
        os.environ["MINIO_PUBLIC_BASE_URL"] = f"http://{host}:{port}"
        os.environ["MINIO_REPORTS_BUCKET_ANONYMOUS_READ"] = "0"

        _reload_eda_modules()
        yield {"host": host, "port": port, "access": access, "secret": secret, "bucket": bucket}
    finally:
        try:
            c.stop()
        except Exception:
            pass


@pytest.fixture(scope="session")
async def db_init(test_db: TestDbConfig) -> None:
    db = importlib.import_module("app.core.database")
    await db.init_db()


@pytest.fixture(autouse=True)
async def _clean_db(db_init) -> None:
    db = importlib.import_module("app.core.database")
    maker = db.async_session_factory
    async with maker() as s:

        await s.execute(
            text(
                """
                TRUNCATE TABLE
                  reports,
                  files,
                  datasets
                RESTART IDENTITY CASCADE;
                """
            )
        )
        await s.commit()


@pytest.fixture(autouse=True)
async def _clean_redis(test_redis: TestRedisConfig) -> None:
    client = redis_async.from_url(test_redis.url, decode_responses=True)
    try:
        await client.flushdb()
    finally:
        try:
            await client.aclose()
        except Exception:
            pass


@pytest.fixture
async def db_session(db_init) -> AsyncIterator["object"]:
    db = importlib.import_module("app.core.database")
    maker = db.async_session_factory
    session = maker()
    try:
        yield session
        await session.commit()
    finally:
        await session.rollback()
        await session.close()


@pytest.fixture(scope="session")
async def app(test_db: TestDbConfig, test_redis: TestRedisConfig) -> "object":
    mod = importlib.import_module("app.cmd.main")
    return mod.app


@pytest.fixture(scope="session")
async def app_minio(test_db: TestDbConfig, test_redis: TestRedisConfig, test_minio) -> "object":
    mod = importlib.import_module("app.cmd.main")
    return mod.app


@pytest.fixture
async def http(app, db_init) -> AsyncIterator["object"]:
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


@pytest.fixture
async def http_streaming(app, db_init) -> AsyncIterator["object"]:
    transport = StreamingBodyASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


@pytest.fixture
async def http_minio(app_minio, db_init) -> AsyncIterator["object"]:
    transport = httpx.ASGITransport(app=app_minio)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


def _make_access_token(user_id: int) -> str:
    s = get_settings()
    now = datetime.now(timezone.utc)
    exp = now + timedelta(minutes=30)
    payload = {
        "sub": f"user:{user_id}",
        "user_id": int(user_id),
        "type": "access",
        "exp": exp,
        "iat": now,
    }
    return jwt.encode(payload, s.SECRET_KEY, algorithm=s.ALGORITHM)


@pytest.fixture
def auth_header() -> dict:
    token = _make_access_token(user_id=1)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def user_id() -> int:
    return 1


@pytest.fixture
async def seed_file_and_dataset(db_session) -> dict:
    ds = DatasetORM(
        source="kaggle",
        external_id=f"k/{uuid4().hex[:8]}",
        title="Seed dataset",
        description="Test dataset",
        tags=["tabular"],
        dataset_format="csv",
        dataset_size_kb=100.0,
        status="active",
        download_url="http://example.com/dataset.zip",
        repository_url="http://example.com",
        source_updated_at=datetime.utcnow(),
        search_vector=func.to_tsvector("english", "Seed dataset Test dataset"),
    )
    db_session.add(ds)
    await db_session.flush()

    f = FileORM(
        dataset_id=ds.dataset_id,
        file_name="data.csv",
        file_size_kb=1.0,
        file_hash="abc",
        is_data=True,
    )
    db_session.add(f)
    await db_session.flush()
    await db_session.commit()

    return {"dataset": ds, "file": f}