import pytest
from app.service.aggregation_service import AggregationEventService
from app.domain.entities import DatasetChangeEvent
from app.domain.value_objects import EDAEventType, ReportStatus


@pytest.mark.asyncio
async def test_process_file_updated_same_hash_noop(monkeypatch):
    """Проверяет: если file_updated с тем же хешем то ничего не меняем"""

    class FakeFilesRepo:
        async def resolve_file_id(self, dataset_id: int, file_name: str):
            return 10

    class FakeReportsRepo:
        async def get_by_file_id(self, file_id: int):
            class R:
                report_id = 1
                status = ReportStatus.COMPLETED
                input_file_hash = "abc"

            return R()

    svc = AggregationEventService(session=None)
    svc._files = FakeFilesRepo()
    svc._reports = FakeReportsRepo()

    called = {"n": 0}

    async def fake_mark_processing_and_enqueue_generate(_session, report_id: int):
        called["n"] += 1

    monkeypatch.setattr(
        "app.service.aggregation_service.mark_processing_and_enqueue_generate",
        fake_mark_processing_and_enqueue_generate,
    )

    ev = DatasetChangeEvent(
        event_type=EDAEventType.FILE_UPDATED,
        dataset_id=1,
        file_name="data.csv",
        file_hash="abc",
        file_id=10,
        source="kaggle",
        external_id="x",
    )
    await svc.process_event(ev)
    assert called["n"] == 0


@pytest.mark.asyncio
async def test_process_file_updated_diff_hash_regenerates_when_completed_or_failed(monkeypatch):
    """Проверяет: если file_updated с другим хешем то ставим processing при completed/failed"""

    class FakeFilesRepo:
        async def resolve_file_id(self, dataset_id: int, file_name: str):
            return 10

    class FakeReportsRepo:
        async def get_by_file_id(self, file_id: int):
            class R:
                report_id = 1
                status = ReportStatus.COMPLETED
                input_file_hash = "old"

            return R()

    svc = AggregationEventService(session="S")
    svc._files = FakeFilesRepo()
    svc._reports = FakeReportsRepo()

    called = {"report_id": None}

    async def fake_mark_processing_and_enqueue_generate(session, report_id: int):
        called["report_id"] = report_id

    monkeypatch.setattr(
        "app.service.aggregation_service.mark_processing_and_enqueue_generate",
        fake_mark_processing_and_enqueue_generate,
    )

    ev = DatasetChangeEvent(
        event_type=EDAEventType.FILE_UPDATED,
        dataset_id=1,
        file_name="data.csv",
        file_hash="new",
        file_id=10,
        source="kaggle",
        external_id="x",
    )
    await svc.process_event(ev)
    assert called["report_id"] == 1


@pytest.mark.asyncio
async def test_process_file_updated_processing_enqueues_waiter_once_via_redis_dedup(monkeypatch):
    """Проверяет: если file_updated при processing то ставим ожидалку"""

    class FakeFilesRepo:
        async def resolve_file_id(self, dataset_id: int, file_name: str):
            return 10

    class FakeReportsRepo:
        async def get_by_file_id(self, file_id: int):
            class R:
                report_id = 7
                status = ReportStatus.PROCESSING
                input_file_hash = "old"

            return R()

    svc = AggregationEventService(session=None)
    svc._files = FakeFilesRepo()
    svc._reports = FakeReportsRepo()

    sends = {"n": 0}

    class FakeRedis:
        def __init__(self):
            self.was = False

        async def set(self, name, value, nx, ex):
            if self.was:
                return False
            self.was = True
            return True

        async def aclose(self):
            return None

    class FakeRedisModule:
        @staticmethod
        def from_url(*_a, **_kw):
            return FakeRedis()

    monkeypatch.setattr("app.service.aggregation_service.redis", FakeRedisModule)

    def fake_send_task(*_a, **_kw):
        sends["n"] += 1

    monkeypatch.setattr("app.service.aggregation_service.celery_app.send_task", fake_send_task)

    ev = DatasetChangeEvent(
        event_type=EDAEventType.FILE_UPDATED,
        dataset_id=1,
        file_name="data.csv",
        file_hash="new",
        file_id=10,
        source="kaggle",
        external_id="x",
    )
    await svc.process_event(ev)
    assert sends["n"] == 1


@pytest.mark.asyncio
async def test_process_file_deleted_enqueues_delete_when_completed_or_failed(monkeypatch):
    """Проверяет: если file_deleted то ставим delete_report_task при completed/failed"""

    class FakeFilesRepo:
        async def resolve_file_id(self, dataset_id: int, file_name: str):
            return 10

    class FakeReportsRepo:
        async def get_by_file_id(self, file_id: int):
            class R:
                report_id = 3
                status = ReportStatus.COMPLETED
                input_file_hash = "x"

            return R()

    svc = AggregationEventService(session=None)
    svc._files = FakeFilesRepo()
    svc._reports = FakeReportsRepo()

    sent = {"queue": None, "kwargs": None}

    def fake_send_task(name, kwargs, queue):
        sent["queue"] = queue
        sent["kwargs"] = kwargs

    monkeypatch.setattr("app.service.aggregation_service.celery_app.send_task", fake_send_task)

    ev = DatasetChangeEvent(
        event_type=EDAEventType.FILE_DELETED,
        dataset_id=1,
        file_name="data.csv",
        file_hash=None,
        file_id=10,
        source="kaggle",
        external_id="x",
    )
    await svc.process_event(ev)
    assert sent["kwargs"] == {"report_id": 3}


@pytest.mark.asyncio
async def test_process_file_deleted_processing_enqueues_delete_waiter_once(monkeypatch):
    """Проверяет: если file_deleted при processing то ставим ожидалку"""

    class FakeFilesRepo:
        async def resolve_file_id(self, dataset_id: int, file_name: str):
            return 10

    class FakeReportsRepo:
        async def get_by_file_id(self, file_id: int):
            class R:
                report_id = 9
                status = ReportStatus.PROCESSING
                input_file_hash = "x"

            return R()

    svc = AggregationEventService(session=None)
    svc._files = FakeFilesRepo()
    svc._reports = FakeReportsRepo()

    sends = {"n": 0, "name": None, "kwargs": None}

    class FakeRedis:
        def __init__(self):
            self.was = False

        async def set(self, name, value, nx, ex):
            if self.was:
                return False
            self.was = True
            return True

        async def aclose(self):
            return None

    class FakeRedisModule:
        @staticmethod
        def from_url(*_a, **_kw):
            return FakeRedis()

    monkeypatch.setattr("app.service.aggregation_service.redis", FakeRedisModule)

    def fake_send_task(name, kwargs=None, queue=None):
        sends["n"] += 1
        sends["name"] = name
        sends["kwargs"] = kwargs

    monkeypatch.setattr("app.service.aggregation_service.celery_app.send_task", fake_send_task)

    ev = DatasetChangeEvent(
        event_type=EDAEventType.FILE_DELETED,
        dataset_id=1,
        file_name="data.csv",
        file_hash=None,
        file_id=10,
        source="kaggle",
        external_id="x",
    )
    await svc.process_event(ev)
    assert sends["n"] == 1
    assert sends["name"] == "app.celery.tasks.delete_waiter_task"
    assert sends["kwargs"] == {"report_id": 9}


@pytest.mark.asyncio
async def test_process_event_uses_file_id_from_event_without_resolve(monkeypatch):
    """Проверяет: если file_id пришёл в событии то поиск file_id не вызывается"""

    class FakeFilesRepo:
        async def resolve_file_id(self, dataset_id: int, file_name: str):
            raise AssertionError("resolve_file_id() не должен вызываться")

    class FakeReportsRepo:
        async def get_by_file_id(self, file_id: int):
            class R:
                report_id = 1
                status = ReportStatus.COMPLETED
                input_file_hash = "old"

            return R()

    svc = AggregationEventService(session=None)
    svc._files = FakeFilesRepo()
    svc._reports = FakeReportsRepo()

    async def fake_mark_processing_and_enqueue_generate(_session, report_id: int):
        return None

    monkeypatch.setattr(
        "app.service.aggregation_service.mark_processing_and_enqueue_generate",
        fake_mark_processing_and_enqueue_generate,
    )

    ev = DatasetChangeEvent(
        event_type=EDAEventType.FILE_UPDATED,
        dataset_id=1,
        file_name="data.csv",
        file_hash="new",
        file_id=999,
        source="kaggle",
        external_id="x",
    )
    await svc.process_event(ev)