from unittest.mock import MagicMock
import pytest
from app.service.eda_notifier import EDANotifier


@pytest.mark.asyncio
async def test_eda_event_includes_file_id():
    """Событие для EDA содержит file_id из БД"""
    celery_app = MagicMock()
    celery_app.send_task = MagicMock(return_value=MagicMock(id="task-1"))

    notifier = EDANotifier(celery_app=celery_app)
    notifier.add_file_notification(
        event_type="file_deleted",
        dataset_id=10,
        file_id=777,
        file_name="data/a.csv",
        external_id="ds99",
        source="uci",
    )

    sent = await notifier.send_notifications()
    assert sent == 1

    celery_app.send_task.assert_called_once()
    call_kw = celery_app.send_task.call_args.kwargs
    inner = call_kw["kwargs"]
    assert inner["file_id"] == 777
    assert inner["dataset_id"] == 10
    assert inner["event_type"] == "file_deleted"