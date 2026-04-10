import pytest
from app.service.checking_stuck_report import CheckingStuckReport


@pytest.mark.asyncio
async def test_detect_and_mark_stuck_marks_failed_and_returns_ids(monkeypatch):
    """Проверяет: зависшие processing отчёты помечаются failed и возвращаются их id"""

    class FakeRepo:
        async def mark_stuck_processing_reports_failed(self, stuck_before, error_message: str):
            assert error_message == "отчёт завис"
            return 2, [11, 12]

    class FakeSession:
        async def commit(self):
            return None

    svc = CheckingStuckReport(session=FakeSession())
    svc._reports = FakeRepo()

    count, ids = await svc.detect_and_mark_stuck()
    assert count == 2
    assert ids == [11, 12]