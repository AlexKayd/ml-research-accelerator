from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock
import pytest
from app.domain.entities import Dataset, File
from app.domain.value_objects import DatasetFormat, DatasetStatus
from app.service.eda_notifier import EDANotifier
from app.service.file_processor import FileProcessor
from app.service.update_service import UpdateService


def _uci_dataset(dataset_id: int = 1, source_updated_at=None) -> Dataset:
    return Dataset(
        dataset_id=dataset_id,
        source="uci",
        external_id="uci-99",
        title="Title",
        description="d",
        tags=["a"],
        dataset_format=DatasetFormat.CSV,
        dataset_size_kb=100.0,
        status=DatasetStatus.ACTIVE,
        download_url="http://dl",
        repository_url="http://repo",
        source_updated_at=source_updated_at,
        files=[],
    )


@pytest.mark.asyncio
async def test_update_deleted_dataset_marks_deleted():
    """Датасет исчез в источнике то статус deleted в БД"""
    session = MagicMock()
    session.commit = AsyncMock()
    session.rollback = AsyncMock()

    ds = _uci_dataset(1)

    repo = MagicMock()
    repo.get_active_datasets_by_source = AsyncMock(side_effect=[[ds], []])
    repo.update_dataset_status = AsyncMock(return_value=True)
    repo.update_source_updated_at = AsyncMock(return_value=True)

    client = MagicMock()
    client.check_dataset_exists = AsyncMock(return_value=False)
    client.get_repository_url = MagicMock(return_value="http://r")
    client.get_download_url = MagicMock(return_value="http://d")

    notifier = EDANotifier(celery_app=None)
    fp = FileProcessor()

    svc = UpdateService(
        session=session,
        dataset_repository=repo,
        source_client=client,
        file_processor=fp,
        eda_notifier=notifier,
        source="uci",
        batch_size=10,
        limit=10,
    )
    await svc.run_updates()

    repo.update_dataset_status.assert_awaited()
    args = repo.update_dataset_status.await_args
    assert args[1]["status"] == "deleted"


@pytest.mark.asyncio
async def test_update_date_optimization_skip_uci():
    """UCI: совпали даты updated_at то полная сверка пропускается"""
    same = datetime(2022, 6, 15, 12, 0, 0, tzinfo=timezone.utc)
    ds = _uci_dataset(1, source_updated_at=same)

    session = MagicMock()
    session.commit = AsyncMock()
    session.rollback = AsyncMock()

    repo = MagicMock()
    repo.get_active_datasets_by_source = AsyncMock(side_effect=[[ds], []])

    client = MagicMock()
    client.check_dataset_exists = AsyncMock(return_value=True)
    client.get_metadata = AsyncMock(return_value={"title": "Title", "last_modified": same.isoformat()})
    client.get_repository_url = MagicMock(return_value="http://r")
    client.get_download_url = MagicMock(return_value="http://d")

    notifier = EDANotifier(celery_app=None)
    fp = FileProcessor()

    svc = UpdateService(
        session=session,
        dataset_repository=repo,
        source_client=client,
        file_processor=fp,
        eda_notifier=notifier,
        source="uci",
        batch_size=10,
        limit=10,
        uci_skip_date_optimization=False,
    )
    res = await svc.run_updates()

    assert res.datasets_skipped == 1
    client.get_files_list.assert_not_called()


@pytest.mark.asyncio
async def test_update_date_optimization_skip_kaggle():
    """Kaggle: совпали даты то полная сверка пропускается"""
    same = datetime(2023, 1, 2, 3, 4, 5, tzinfo=timezone.utc)
    ds = Dataset(
        dataset_id=2,
        source="kaggle",
        external_id="o/pkg",
        title="K",
        dataset_format=DatasetFormat.CSV,
        dataset_size_kb=10.0,
        status=DatasetStatus.ACTIVE,
        source_updated_at=same,
        files=[],
    )

    session = MagicMock()
    session.commit = AsyncMock()
    session.rollback = AsyncMock()

    repo = MagicMock()
    repo.get_active_datasets_by_source = AsyncMock(side_effect=[[ds], []])

    client = MagicMock()
    client.check_dataset_exists = AsyncMock(return_value=True)
    client.get_metadata = AsyncMock(
        return_value={"title": "K", "lastUpdated": same.isoformat()}
    )
    client.get_repository_url = MagicMock(return_value="http://r")
    client.get_download_url = MagicMock(return_value="http://d")

    notifier = EDANotifier(celery_app=None)
    fp = FileProcessor()

    svc = UpdateService(
        session=session,
        dataset_repository=repo,
        source_client=client,
        file_processor=fp,
        eda_notifier=notifier,
        source="kaggle",
        batch_size=10,
        limit=10,
        kaggle_skip_date_optimization=False,
    )
    res = await svc.run_updates()

    assert res.datasets_skipped == 1
    client.get_files_list.assert_not_called()


@pytest.mark.asyncio
async def test_update_file_deleted_sends_eda_only_for_data_files():
    """Удалён data-файл то EDA file_deleted; non-data то без EDA"""
    data_f = File(
        file_id=101,
        file_name="a.csv",
        file_size_kb=10.0,
        is_data=True,
        file_hash="h1",
    )
    meta_f = File(
        file_id=102,
        file_name="readme.txt",
        file_size_kb=1.0,
        is_data=False,
    )
    ds = _uci_dataset(1, source_updated_at=None)

    session = MagicMock()
    session.commit = AsyncMock()
    session.rollback = AsyncMock()

    repo = MagicMock()
    repo.get_active_datasets_by_source = AsyncMock(side_effect=[[ds], []])
    repo.get_files_by_dataset = AsyncMock(return_value=[data_f, meta_f])
    repo.delete_file = AsyncMock(return_value=True)
    repo.recalculate_dataset_size = AsyncMock(return_value=10.0)
    repo.update_dataset = AsyncMock(return_value=True)

    client = MagicMock()
    client.check_dataset_exists = AsyncMock(return_value=True)
    client.get_metadata = AsyncMock(return_value={"title": "Title", "last_modified": "2099-01-01T00:00:00+00:00"})
    client.get_files_list = AsyncMock(
        return_value=[
            {"file_name": "readme.txt", "size_bytes": 1024},
        ]
    )
    client.download_dataset = AsyncMock(return_value="/tmp/x.zip")
    client.extract_and_hash_files = AsyncMock(return_value=[])
    client.get_repository_url = MagicMock(return_value="http://r")
    client.get_download_url = MagicMock(return_value="http://d")

    notifier = EDANotifier(celery_app=None)
    fp = FileProcessor()

    svc = UpdateService(
        session=session,
        dataset_repository=repo,
        source_client=client,
        file_processor=fp,
        eda_notifier=notifier,
        source="uci",
        batch_size=10,
        limit=10,
        uci_skip_date_optimization=True,
    )
    await svc.run_updates()

    pending = notifier._pending_notifications
    types = [p["event_type"] for p in pending]
    assert "file_deleted" in types
    assert sum(1 for p in pending if p["event_type"] == "file_deleted") == 1
    del_ev = next(p for p in pending if p["event_type"] == "file_deleted")
    assert del_ev["file_id"] == 101


@pytest.mark.asyncio
async def test_update_file_hash_recalc_sends_file_updated_when_hash_changed():
    """Пересчёт хеша data-файла то EDA file_updated только при смене хеша"""
    data_f = File(
        file_id=55,
        file_name="a.csv",
        file_size_kb=10.0,
        is_data=True,
        file_hash="oldhash",
    )
    ds = _uci_dataset(1, source_updated_at=None)

    session = MagicMock()
    session.commit = AsyncMock()
    session.rollback = AsyncMock()

    repo = MagicMock()
    repo.get_active_datasets_by_source = AsyncMock(side_effect=[[ds], []])
    repo.get_files_by_dataset = AsyncMock(return_value=[data_f])
    repo.update_file = AsyncMock(return_value=True)
    repo.recalculate_dataset_size = AsyncMock(return_value=10.0)
    repo.update_dataset = AsyncMock(return_value=True)

    client = MagicMock()
    client.check_dataset_exists = AsyncMock(return_value=True)
    client.get_metadata = AsyncMock(return_value={"title": "Title", "last_modified": "2099-01-01T00:00:00+00:00"})
    client.get_files_list = AsyncMock(
        return_value=[
            {"file_name": "a.csv", "size_bytes": 10240},
        ]
    )
    client.download_dataset = AsyncMock(return_value="/tmp/z.zip")
    client.extract_and_hash_files = AsyncMock(
        return_value=[
            {
                "file_name": "a.csv",
                "file_size_kb": 10.0,
                "is_data": True,
                "file_hash": "newhash",
            }
        ]
    )
    client.get_repository_url = MagicMock(return_value="http://r")
    client.get_download_url = MagicMock(return_value="http://d")

    notifier = EDANotifier(celery_app=None)
    fp = FileProcessor()

    svc = UpdateService(
        session=session,
        dataset_repository=repo,
        source_client=client,
        file_processor=fp,
        eda_notifier=notifier,
        source="uci",
        batch_size=10,
        limit=10,
        uci_skip_date_optimization=True,
        uci_force_hash_recalc_on_same_size=True,
    )
    await svc.run_updates()

    pending = notifier._pending_notifications
    upd = [p for p in pending if p["event_type"] == "file_updated"]
    assert len(upd) == 1
    assert upd[0]["file_id"] == 55
    assert upd[0]["file_hash"] == "newhash"


@pytest.mark.asyncio
async def test_update_added_files_do_not_send_eda_events():
    """Новый файл в источнике то в БД добавляется"""
    data_f = File(
        file_id=1,
        file_name="old.csv",
        file_size_kb=5.0,
        is_data=True,
        file_hash="h",
    )
    ds = _uci_dataset(1, source_updated_at=None)

    session = MagicMock()
    session.commit = AsyncMock()
    session.rollback = AsyncMock()

    repo = MagicMock()
    repo.get_active_datasets_by_source = AsyncMock(side_effect=[[ds], []])
    repo.get_files_by_dataset = AsyncMock(return_value=[data_f])
    repo.add_file = AsyncMock(return_value=True)
    repo.recalculate_dataset_size = AsyncMock(return_value=15.0)
    repo.update_dataset = AsyncMock(return_value=True)

    client = MagicMock()
    client.check_dataset_exists = AsyncMock(return_value=True)
    client.get_metadata = AsyncMock(return_value={"title": "Title", "last_modified": "2099-01-01T00:00:00+00:00"})
    client.get_files_list = AsyncMock(
        return_value=[
            {"file_name": "old.csv", "size_bytes": 5120},
            {"file_name": "new.csv", "size_bytes": 10240},
        ]
    )
    client.download_dataset = AsyncMock(return_value="/tmp/a.zip")
    client.extract_and_hash_files = AsyncMock(
        return_value=[
            {
                "file_name": "new.csv",
                "file_size_kb": 10.0,
                "is_data": True,
                "file_hash": "nh",
            }
        ]
    )
    client.get_repository_url = MagicMock(return_value="http://r")
    client.get_download_url = MagicMock(return_value="http://d")

    notifier = EDANotifier(celery_app=None)
    fp = FileProcessor()

    svc = UpdateService(
        session=session,
        dataset_repository=repo,
        source_client=client,
        file_processor=fp,
        eda_notifier=notifier,
        source="uci",
        batch_size=10,
        limit=10,
        uci_skip_date_optimization=True,
    )
    await svc.run_updates()

    assert notifier.get_pending_count() == 0