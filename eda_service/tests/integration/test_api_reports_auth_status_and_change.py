import asyncio
import json
from datetime import datetime
import pytest
from app.celery.tasks import _process_dataset_change_async
from app.domain.value_objects import ReportStatus
from app.repository.models import FileORM, ReportORM
from app.sse.sse_broker import publish_report_failed_sync


@pytest.mark.asyncio(loop_scope="session")
async def test_api_reports_generate_status_events_require_bearer_401(http):
    """Без авторизации 401 на generate, status и SSE"""
    r1 = await http.post("/api/reports/generate", json={"file_id": 1})
    assert r1.status_code == 401

    r2 = await http.get("/api/reports/status/1")
    assert r2.status_code == 401

    r3 = await http.get("/api/reports/events")
    assert r3.status_code == 401


@pytest.mark.asyncio(loop_scope="session")
async def test_api_get_status_processing_and_failed(http, db_session, seed_file_and_dataset, auth_header):
    ds = seed_file_and_dataset["dataset"]
    f = seed_file_and_dataset["file"]

    f2 = FileORM(
        dataset_id=ds.dataset_id,
        file_name="other.csv",
        file_size_kb=2.0,
        file_hash="def",
        is_data=True,
    )
    db_session.add(f2)
    await db_session.flush()

    proc = ReportORM(
        file_id=int(f.file_id),
        bucket_name=None,
        object_key=None,
        input_file_hash="x",
        status=ReportStatus.PROCESSING.value,
        updated_at=None,
        processing_started_at=datetime.utcnow(),
    )
    db_session.add(proc)
    await db_session.flush()

    fail = ReportORM(
        file_id=int(f2.file_id),
        bucket_name=None,
        object_key=None,
        input_file_hash="y",
        status=ReportStatus.FAILED.value,
        updated_at=datetime.utcnow(),
        error_message="тестовая ошибка",
    )
    db_session.add(fail)
    await db_session.flush()
    await db_session.commit()

    rp = await http.get(f"/api/reports/status/{int(proc.report_id)}", headers=auth_header)
    assert rp.status_code == 200
    jp = rp.json()
    assert jp["status"] == "processing"
    assert jp["report_url"] in (None, "")
    assert jp["report_id"] == int(proc.report_id)

    rf = await http.get(f"/api/reports/status/{int(fail.report_id)}", headers=auth_header)
    assert rf.status_code == 200
    jf = rf.json()
    assert jf["status"] == "failed"
    assert jf["error_message"] == "тестовая ошибка"
    assert jf["report_url"] in (None, "")


@pytest.mark.asyncio(loop_scope="session")
async def test_api_get_status_unknown_report_404(http, auth_header):
    r = await http.get("/api/reports/status/999999999", headers=auth_header)
    assert r.status_code == 404


@pytest.mark.asyncio(loop_scope="session")
async def test_process_dataset_change_file_deleted_enqueues_delete_task(
    db_session, seed_file_and_dataset, monkeypatch
):
    """Проверяет: completed + file_deleted то delete_report_task"""
    ds = seed_file_and_dataset["dataset"]
    f = seed_file_and_dataset["file"]

    rep = ReportORM(
        file_id=int(f.file_id),
        bucket_name="eda-reports",
        object_key="u/1/r/1.html",
        input_file_hash="abc",
        status=ReportStatus.COMPLETED.value,
        updated_at=datetime.utcnow(),
    )
    db_session.add(rep)
    await db_session.flush()
    await db_session.commit()

    sent: list[tuple[str, dict | None]] = []

    def fake_send_task(name, kwargs=None, **_kw):
        sent.append((str(name), dict(kwargs) if kwargs else None))

    monkeypatch.setattr("app.service.aggregation_service.celery_app.send_task", fake_send_task)

    out = await _process_dataset_change_async(
        {
            "event_type": "file_deleted",
            "dataset_id": int(ds.dataset_id),
            "file_name": f.file_name,
            "file_id": int(f.file_id),
            "source": "kaggle",
            "external_id": "x",
        }
    )
    assert out["status"] == "ok"
    assert out["event_type"] == "file_deleted"

    names = [n for n, _ in sent]
    assert "app.celery.tasks.delete_report_task" in names
    assert any(kw == {"report_id": int(rep.report_id)} for n, kw in sent if n == "app.celery.tasks.delete_report_task")


@pytest.mark.asyncio(loop_scope="session")
async def test_sse_receives_report_failed_like_broker(http_streaming, auth_header, user_id):
    """Проверяет: Redis publish то SSE уведомление"""
    async with http_streaming.stream("GET", "/api/reports/events", headers=auth_header) as resp:
        assert resp.status_code == 200
        lines = resp.aiter_lines()
        await asyncio.wait_for(anext(lines), timeout=5.0)

        await asyncio.to_thread(publish_report_failed_sync, int(user_id), 42, "ошибка генерации")

        async def _wait_failed() -> dict:
            async for line in lines:
                if line.startswith("data: "):
                    return json.loads(line.removeprefix("data: ").strip())
            raise AssertionError("SSE stream closed without data")

        got = await asyncio.wait_for(_wait_failed(), timeout=5.0)
        assert got["event"] == "report_failed"
        assert got["report_id"] == 42
        assert "ошибка" in (got.get("error_message") or "")