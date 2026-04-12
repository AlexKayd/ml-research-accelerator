from datetime import datetime
from unittest.mock import AsyncMock, MagicMock
import pytest
from app.domain.entities import Dataset, File
from app.domain.value_objects import DatasetFormat, DatasetStatus
from app.repository.dataset_repository import DatasetRepository
from app.service.eda_notifier import EDANotifier
from app.service.file_processor import FileProcessor
from app.service.update_service import UpdateService


@pytest.mark.asyncio(loop_scope="session")
async def test_update_sends_events_to_eda_queue_and_payload_has_file_id(db_session):
    """Если удаляем data-файл, то отправляем событие в очередь EDA с file_id"""
    ds = Dataset(
        source="uci",
        external_id="integration-ds-1",
        title="Integration DS",
        description="d",
        tags=["t"],
        dataset_format=DatasetFormat.CSV,
        dataset_size_kb=11.0,
        status=DatasetStatus.ACTIVE,
        download_url="http://dl",
        repository_url="http://repo",
        source_updated_at=None,
        files=[
            File(file_name="keep.txt", file_size_kb=1.0, is_data=False),
            File(file_name="gone.csv", file_size_kb=10.0, is_data=True, file_hash="abc"),
        ],
    )
    repo = DatasetRepository(db_session)
    dataset_id = await repo.save_dataset_with_files(ds)
    await db_session.commit()

    files_db = await repo.get_files_by_dataset(dataset_id)
    gone = next(f for f in files_db if f.file_name == "gone.csv")
    assert gone.file_id is not None

    celery_app = MagicMock()
    celery_app.send_task = MagicMock(return_value=MagicMock(id="t1"))

    client = MagicMock()
    client.check_dataset_exists = AsyncMock(return_value=True)
    client.get_metadata = AsyncMock(
        return_value={
            "title": "Integration DS",
            "description": "d",
            "tags": ["t"],
            "last_modified": datetime(2099, 1, 1, 0, 0, 0).isoformat(),
        }
    )
    client.get_files_list = AsyncMock(
        return_value=[
            {"file_name": "keep.txt", "size_bytes": 1024},
        ]
    )
    client.download_dataset = AsyncMock(return_value="/tmp/fake.zip")
    client.extract_and_hash_files = AsyncMock(return_value=[])
    client.get_repository_url = MagicMock(return_value="http://repo")
    client.get_download_url = MagicMock(return_value="http://dl")

    notifier = EDANotifier(celery_app=celery_app)
    fp = FileProcessor()

    svc = UpdateService(
        session=db_session,
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

    celery_app.send_task.assert_called()
    calls = [c.kwargs.get("kwargs") or {} for c in celery_app.send_task.call_args_list]
    deleted = [c for c in calls if c.get("event_type") == "file_deleted"]
    assert len(deleted) >= 1
    assert deleted[0].get("file_id") == int(gone.file_id)
    assert deleted[0].get("file_name") == "gone.csv"

    files_after = await repo.get_files_by_dataset(dataset_id)
    names = {f.file_name for f in files_after}
    assert "gone.csv" not in names
    assert "keep.txt" in names