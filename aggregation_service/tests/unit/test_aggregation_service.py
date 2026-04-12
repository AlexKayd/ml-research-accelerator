from unittest.mock import AsyncMock, MagicMock
import pytest
from app.domain.entities import AggregationResult
from app.service.aggregation_service import AggregationService
from app.service.file_processor import FileProcessor


@pytest.mark.asyncio
async def test_aggregation_skips_existing_in_db():
    """Если датасет уже есть в БД то пропуск без скачивания"""
    session = MagicMock()
    session.commit = AsyncMock()
    session.rollback = AsyncMock()

    repo = MagicMock()
    repo.exists = AsyncMock(return_value=True)

    client = MagicMock()
    client.list_dataset_ids = AsyncMock(return_value=["ext-1"])

    fp = FileProcessor()

    svc = AggregationService(
        session=session,
        dataset_repository=repo,
        source_client=client,
        file_processor=fp,
        source="uci",
        batch_size=10,
    )
    res: AggregationResult = await svc.run_aggregation()

    assert res.datasets_processed == 1
    assert res.datasets_skipped == 1
    assert res.datasets_added == 0
    client.check_dataset_exists.assert_not_called()
    client.get_metadata.assert_not_called()


@pytest.mark.asyncio
async def test_aggregation_skips_empty_files_list():
    """Пустой files_list из источника то датасет пропускается"""
    session = MagicMock()
    session.commit = AsyncMock()
    session.rollback = AsyncMock()

    repo = MagicMock()
    repo.exists = AsyncMock(return_value=False)

    client = MagicMock()
    client.list_dataset_ids = AsyncMock(return_value=["ext-1"])
    client.check_dataset_exists = AsyncMock(return_value=True)
    client.get_metadata = AsyncMock(return_value={"title": "T", "last_modified": "2020-01-01T00:00:00+00:00"})
    client.get_files_list = AsyncMock(return_value=[])
    client.get_repository_url = MagicMock(return_value="http://repo")
    client.get_download_url = MagicMock(return_value="http://dl")

    fp = FileProcessor()

    svc = AggregationService(
        session=session,
        dataset_repository=repo,
        source_client=client,
        file_processor=fp,
        source="uci",
        batch_size=10,
    )
    res = await svc.run_aggregation()

    assert res.datasets_skipped == 1
    client.download_dataset.assert_not_called()


@pytest.mark.asyncio
async def test_aggregation_skips_kaggle_without_tabular_tag():
    """Kaggle: без тега tabular в keywords то пропуск"""
    session = MagicMock()
    session.commit = AsyncMock()
    session.rollback = AsyncMock()

    repo = MagicMock()
    repo.exists = AsyncMock(return_value=False)

    client = MagicMock()
    client.list_dataset_ids = AsyncMock(return_value=["owner/pkg"])
    client.check_dataset_exists = AsyncMock(return_value=True)
    client.get_metadata = AsyncMock(return_value={"title": "x", "keywords": ["image"]})
    client.get_repository_url = MagicMock(return_value="http://k")
    client.get_download_url = MagicMock(return_value="http://d")

    fp = FileProcessor()

    svc = AggregationService(
        session=session,
        dataset_repository=repo,
        source_client=client,
        file_processor=fp,
        source="kaggle",
        batch_size=10,
    )
    res = await svc.run_aggregation()

    assert res.datasets_skipped == 1
    client.get_files_list.assert_not_called()


@pytest.mark.asyncio
async def test_aggregation_happy_path_saves_new_dataset():
    """Первичная агрегация полный прогон"""
    session = MagicMock()
    session.commit = AsyncMock()
    session.rollback = AsyncMock()

    repo = MagicMock()
    repo.exists = AsyncMock(return_value=False)
    repo.save_dataset_with_files = AsyncMock(return_value=501)

    client = MagicMock()
    client.list_dataset_ids = AsyncMock(return_value=["uci-new-1"])
    client.check_dataset_exists = AsyncMock(return_value=True)
    client.get_metadata = AsyncMock(
        return_value={
            "title": "New dataset",
            "description": "desc",
            "tags": ["tabular"],
            "last_modified": "2021-06-15T12:00:00",
            "repository_url": "https://example.com/ds",
        }
    )
    client.get_files_list = AsyncMock(
        return_value=[
            {"file_name": "data.csv", "size_bytes": 5120},
        ]
    )
    client.validate_dataset_files = AsyncMock(return_value={"format": "csv", "total_size_kb": 5.0})
    client.download_dataset = AsyncMock(return_value="/tmp/uci_agg.zip")
    client.extract_and_hash_files = AsyncMock(
        return_value=[
            {
                "file_name": "data.csv",
                "file_size_kb": 5.0,
                "is_data": True,
                "file_hash": "abc123deadbeef",
            }
        ]
    )
    client.get_repository_url = MagicMock(return_value="https://example.com/ds")
    client.get_download_url = MagicMock(return_value="https://example.com/ds.zip")

    fp = FileProcessor()

    svc = AggregationService(
        session=session,
        dataset_repository=repo,
        source_client=client,
        file_processor=fp,
        source="uci",
        batch_size=10,
    )
    res: AggregationResult = await svc.run_aggregation()

    assert res.success is True
    assert res.datasets_processed == 1
    assert res.datasets_added == 1
    assert res.datasets_skipped == 0
    assert res.datasets_failed == 0
    assert res.files_processed == 1

    repo.save_dataset_with_files.assert_awaited_once()
    session.commit.assert_awaited()
    client.download_dataset.assert_awaited()
    client.extract_and_hash_files.assert_awaited()
    client.validate_dataset_files.assert_awaited()

    saved = repo.save_dataset_with_files.await_args.args[0]
    assert saved.external_id == "uci-new-1"
    assert saved.source.value == "uci"
    assert len(saved.files) == 1
    assert saved.files[0].file_name == "data.csv"
    assert saved.files[0].file_hash == "abc123deadbeef"