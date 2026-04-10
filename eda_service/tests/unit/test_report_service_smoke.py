import pytest
from app.service.report_service import ReportService
from app.domain.value_objects import ReportStatus


@pytest.mark.asyncio
async def test_generate_when_processing_registers_subscriber_only(monkeypatch):
    """Проверяет: если отчёт уже processing то только подписка"""

    class FakeReports:
        async def get_by_file_id(self, file_id: int):
            class R:
                report_id = 5
                status = ReportStatus.PROCESSING
                updated_at = None
                object_key = None
                bucket_name = None
                input_file_hash = None

            return R()

    class FakeSession:
        async def commit(self):
            return None

    called = {"register": 0, "enqueue": 0}

    async def fake_register(report_id: int, user_id: int):
        called["register"] += 1

    async def fake_mark_processing_and_enqueue_generate(_session, report_id: int):
        called["enqueue"] += 1

    monkeypatch.setattr("app.service.report_service.register_report_subscriber", fake_register)
    monkeypatch.setattr("app.service.report_service.mark_processing_and_enqueue_generate", fake_mark_processing_and_enqueue_generate)

    svc = ReportService(session=FakeSession())
    svc._reports = FakeReports()

    resp = await svc.get_or_create_report(file_id=1, user_id=7)
    assert resp.status == "processing"
    assert called["register"] == 1
    assert called["enqueue"] == 0