from __future__ import annotations
import pytest
from datetime import datetime
from sqlalchemy import func, select
from app.handler import eda_internal_handler
from app.repository.models import UserReportORM, DatasetORM, FileORM


@pytest.mark.asyncio(loop_scope="session")
async def test_api_datasets_non_data_files_public_endpoint(http, seed_catalog):
    """Проверяет публичный endpoint: возвращает только non-data файлы датасета"""
    ds1 = seed_catalog["datasets"]["ds1"]
    r = await http.get(f"/api/datasets/{ds1.dataset_id}")
    assert r.status_code == 200
    body = r.json()
    assert body["dataset_id"] == ds1.dataset_id
    names = [x["file_name"] for x in body["files"]]
    assert "README.md" in names
    assert "data.csv" not in names


@pytest.mark.asyncio(loop_scope="session")
async def test_api_datasets_search_and_filters(http, db_session, bearer, seed_catalog):
    """Проверяет поиск и фильтры каталога и что deleted не попадает"""
    ds1 = seed_catalog["datasets"]["ds1"]
    ds2 = seed_catalog["datasets"]["ds2"]

    deleted = DatasetORM(
        source="kaggle",
        external_id="k/deleted",
        title="Deleted one",
        description="Should not be visible",
        tags=["x"],
        dataset_format="csv",
        dataset_size_kb=10.0,
        status="deleted",
        search_vector=func.to_tsvector("english", "Deleted one Should not be visible"),
        source_updated_at=datetime.utcnow(),
    )
    db_session.add(deleted)
    await db_session.flush()
    db_session.add(
        FileORM(
            dataset_id=deleted.dataset_id,
            file_name="x.csv",
            file_size_kb=1.0,
            file_hash="h3",
            is_data=True,
        )
    )
    await db_session.commit()

    r = await http.get("/api/datasets", headers=bearer, params={"query": "seed"})
    assert r.status_code == 200
    ids = [row["dataset_id"] for row in r.json()]
    assert ds1.dataset_id in ids
    assert ds2.dataset_id in ids
    assert deleted.dataset_id not in ids

    r = await http.get("/api/datasets", headers=bearer, params={"sources": ["uci"]})
    assert r.status_code == 200
    ids = [row["dataset_id"] for row in r.json()]
    assert ds2.dataset_id in ids
    assert ds1.dataset_id not in ids

    r = await http.get("/api/datasets", headers=bearer, params={"file_formats": ["csv"]})
    assert r.status_code == 200
    ids = [row["dataset_id"] for row in r.json()]
    assert ds1.dataset_id in ids
    assert ds2.dataset_id not in ids

    r = await http.get("/api/datasets", headers=bearer, params={"max_size_mb": 1.0})
    assert r.status_code == 200
    ids = [row["dataset_id"] for row in r.json()]
    assert ds1.dataset_id in ids
    assert ds2.dataset_id not in ids

    r = await http.get("/api/datasets", headers=bearer, params={"tags": ["health"]})
    assert r.status_code == 200
    ids = [row["dataset_id"] for row in r.json()]
    assert ds1.dataset_id in ids
    assert ds2.dataset_id not in ids

    r = await http.get(
        "/api/datasets",
        headers=bearer,
        params={"query": "health", "sources": ["kaggle"], "file_formats": ["csv"], "tags": ["tabular"], "max_size_mb": 1.0},
    )
    assert r.status_code == 200
    ids = [row["dataset_id"] for row in r.json()]
    assert ids == [ds1.dataset_id]


@pytest.mark.asyncio(loop_scope="session")
async def test_api_favorites_crud(http, bearer, seed_catalog):
    """Проверяет избранное через API"""
    ds1 = seed_catalog["datasets"]["ds1"]

    r = await http.post(f"/api/users/favorites/{ds1.dataset_id}", headers=bearer)
    assert r.status_code == 201

    r = await http.post(f"/api/users/favorites/{ds1.dataset_id}", headers=bearer)
    assert r.status_code == 409

    r = await http.get("/api/users/favorites", headers=bearer)
    assert r.status_code == 200
    items = r.json()
    assert any(x["dataset_id"] == ds1.dataset_id for x in items)

    r = await http.delete(f"/api/users/favorites/{ds1.dataset_id}", headers=bearer)
    assert r.status_code == 200

    r = await http.delete(f"/api/users/favorites/{ds1.dataset_id}", headers=bearer)
    assert r.status_code == 404


@pytest.mark.asyncio(loop_scope="session")
async def test_api_reports_history_list_and_delete(http, db_session, bearer, seed_catalog):
    """Проверяет историю отчётов: list содержит report_url, затем delete удаляет связь"""
    user_id = seed_catalog["user_id"]
    rep = seed_catalog["reports"]["r1"]

    db_session.add(UserReportORM(user_id=user_id, report_id=rep.report_id))
    await db_session.commit()

    r = await http.get("/api/users/reports", headers=bearer)
    assert r.status_code == 200
    rows = r.json()
    assert any(x["report_id"] == rep.report_id and x["report_url"] for x in rows)

    r = await http.delete(f"/api/users/reports/{rep.report_id}", headers=bearer)
    assert r.status_code == 200

    r = await http.delete(f"/api/users/reports/{rep.report_id}", headers=bearer)
    assert r.status_code == 404


@pytest.mark.asyncio(loop_scope="session")
async def test_api_eda_internal_attach_report_token_guard(http, db_session, seed_catalog, monkeypatch):
    """Проверяет внутренний EDA endpoint: 403/503 по токену и 200 без дублей"""
    user_id = seed_catalog["user_id"]
    rep = seed_catalog["reports"]["r1"]

    r = await http.post(f"/api/users/{user_id}/reports", json={"report_id": rep.report_id})
    assert r.status_code == 403

    r = await http.post(
        f"/api/users/{user_id}/reports",
        json={"report_id": rep.report_id},
        headers={"X-EDA-Internal-Token": "wrong"},
    )
    assert r.status_code == 403

    class S:
        EDA_SERVICE_INTERNAL_TOKEN = "   "

    monkeypatch.setattr(eda_internal_handler, "get_settings", lambda: S())
    r = await http.post(
        f"/api/users/{user_id}/reports",
        json={"report_id": rep.report_id},
        headers={"X-EDA-Internal-Token": "whatever"},
    )
    assert r.status_code == 503

    class S2:
        EDA_SERVICE_INTERNAL_TOKEN = "test-internal-token"

    monkeypatch.setattr(eda_internal_handler, "get_settings", lambda: S2())

    r = await http.post(
        f"/api/users/{user_id}/reports",
        json={"report_id": rep.report_id},
        headers={"X-EDA-Internal-Token": "test-internal-token"},
    )
    assert r.status_code == 200
    assert r.json()["message"] == "ok"

    r = await http.post(
        f"/api/users/{user_id}/reports",
        json={"report_id": rep.report_id},
        headers={"X-EDA-Internal-Token": "test-internal-token"},
    )
    assert r.status_code == 200

    q = select(func.count()).select_from(UserReportORM).where(
        UserReportORM.user_id == user_id, UserReportORM.report_id == rep.report_id
    )
    cnt = (await db_session.execute(q)).scalar_one()
    assert cnt == 1