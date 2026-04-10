import asyncio
import io
import zipfile
from app.service import report_generator as gen_mod
import pytest
from app.celery.tasks import _generate_report_async
from app.core.minio import get_minio_client
from datetime import datetime
from app.repository.models import ReportORM
from app.domain.value_objects import ReportStatus


def _zip_bytes(file_name: str, content: bytes) -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr(file_name, content)
    return buf.getvalue()


@pytest.mark.asyncio(loop_scope="session")
async def test_api_generate_report_end_to_end_with_minio_object_created(
    http_minio,
    auth_header,
    db_session,
    seed_file_and_dataset,
    test_minio,
    monkeypatch,
):
    """generate создаёт processing и потом completed с объектом в MinIO (подмена ydata-profiling)"""

    f = seed_file_and_dataset["file"]

    async def fake_build_profile_html(self, file_path):
        return "<html><body>ok</body></html>"

    monkeypatch.setattr(gen_mod.ReportGenerator, "_build_profile_html", fake_build_profile_html)

    zip_bytes = _zip_bytes("data.csv", b"a,b\n1,2\n")

    async def fake_download(self, url, target_path):
        target_path.write_bytes(zip_bytes)

    monkeypatch.setattr(gen_mod.ReportGenerator, "_download_zip", fake_download)

    r = await http_minio.post("/api/reports/generate", headers=auth_header, json={"file_id": int(f.file_id)})
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "processing"
    report_id = int(body["report_id"])

    res = await _generate_report_async(report_id)
    assert res["status"] == "completed"

    r2 = await http_minio.get(f"/api/reports/status/{report_id}", headers=auth_header)
    assert r2.status_code == 200
    body2 = r2.json()
    assert body2["status"] == "completed"
    assert body2["report_url"]

    minio = get_minio_client()
    obj_key = res["object_key"]
    stat = await asyncio.to_thread(minio._client.stat_object, test_minio["bucket"], obj_key)
    assert stat.size > 0


@pytest.mark.asyncio(loop_scope="session")
async def test_api_status_completed_triggers_attach_enqueue_dedup(http, auth_header, db_session, seed_file_and_dataset, monkeypatch, user_id):
    """Проверяет: GET /status completed то ставится notify_user_service_report_ready_task"""
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

    sent = {"n": 0}

    def fake_send_task(*_a, **_kw):
        sent["n"] += 1

    monkeypatch.setattr("app.service.report_subscribers_redis.celery_app.send_task", fake_send_task)

    r1 = await http.get(f"/api/reports/status/{int(rep.report_id)}", headers=auth_header)
    assert r1.status_code == 200
    r2 = await http.get(f"/api/reports/status/{int(rep.report_id)}", headers=auth_header)
    assert r2.status_code == 200
    assert sent["n"] == 1