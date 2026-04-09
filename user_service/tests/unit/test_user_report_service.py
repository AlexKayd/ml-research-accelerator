import pytest
from app.domain.exceptions import ReportNotFoundError, ReportNotInHistoryError
from app.domain.user import UserReport
from app.service.user_report_service import UserReportService
from app.domain.exceptions import ReportAlreadyExistsError


class FakeReportRepo:
    def __init__(self, existing: set[int]) -> None:
        self._existing = set(existing)

    async def exists(self, report_id: int) -> bool:
        return int(report_id) in self._existing

    async def get_user_reports_list(self, user_id: int):
        return [
            {
                "report_id": 1,
                "bucket_name": "reports",
                "object_key": "u/1/r/1.html",
            }
        ]


class FakeUserReportRepo:
    def __init__(self) -> None:
        self._pairs: set[tuple[int, int]] = set()

    async def add(self, user_id: int, report_id: int) -> UserReport:
        key = (int(user_id), int(report_id))
        if key in self._pairs:
            raise ReportAlreadyExistsError(user_id=user_id, report_id=report_id)
        self._pairs.add(key)
        return UserReport(user_id=user_id, report_id=report_id)

    async def remove(self, user_id: int, report_id: int) -> bool:
        key = (int(user_id), int(report_id))
        if key not in self._pairs:
            return False
        self._pairs.remove(key)
        return True


@pytest.mark.asyncio
async def test_save_report_requires_report_exists():
    """Проверяет, что нельзя привязать к пользователю несуществующий report_id (404)"""
    svc = UserReportService(FakeUserReportRepo(), FakeReportRepo(existing=set()))
    with pytest.raises(ReportNotFoundError) as e:
        await svc.save_report(user_id=1, report_id=123)
    assert e.value.status_code == 404
    assert e.value.code == "REPORT_NOT_FOUND"


@pytest.mark.asyncio
async def test_save_report_idempotent_on_duplicate():
    """Проверяет: повторное сохранение связи не падает"""
    svc = UserReportService(FakeUserReportRepo(), FakeReportRepo(existing={10}))
    await svc.save_report(user_id=1, report_id=10)
    link = await svc.save_report_idempotent(user_id=1, report_id=10)
    assert link.user_id == 1
    assert link.report_id == 10


@pytest.mark.asyncio
async def test_delete_report_from_history_success():
    """Проверяет удаление отчёта из истории"""
    svc = UserReportService(FakeUserReportRepo(), FakeReportRepo(existing={10}))
    await svc.save_report(user_id=1, report_id=10)
    await svc.remove_from_history(user_id=1, report_id=10)


@pytest.mark.asyncio
async def test_delete_report_from_history_missing_link_404():
    """Проверяет, что удаление отсутствующей связи даёт 404 REPORT_NOT_IN_HISTORY"""
    svc = UserReportService(FakeUserReportRepo(), FakeReportRepo(existing={10}))
    with pytest.raises(ReportNotInHistoryError) as e:
        await svc.remove_from_history(user_id=1, report_id=10)
    assert e.value.status_code == 404
    assert e.value.code == "REPORT_NOT_IN_HISTORY"