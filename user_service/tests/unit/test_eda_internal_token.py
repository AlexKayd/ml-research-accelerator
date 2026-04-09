import pytest
from fastapi import HTTPException
from app.handler import eda_internal_handler


@pytest.mark.asyncio
async def test_internal_token_required_503_if_not_configured(monkeypatch):
    """Проверяет: если EDA_SERVICE_INTERNAL_TOKEN пустой то 503"""

    class S:
        EDA_SERVICE_INTERNAL_TOKEN = "   "

    monkeypatch.setattr(eda_internal_handler, "get_settings", lambda: S())

    with pytest.raises(HTTPException) as e:
        await eda_internal_handler.verify_eda_internal_token(x_eda_internal_token="any")
    assert e.value.status_code == 503


@pytest.mark.asyncio
async def test_internal_token_wrong_403(monkeypatch):
    """Проверяет: если токен неправильный то 403"""

    class S:
        EDA_SERVICE_INTERNAL_TOKEN = "expected"

    monkeypatch.setattr(eda_internal_handler, "get_settings", lambda: S())

    with pytest.raises(HTTPException) as e:
        await eda_internal_handler.verify_eda_internal_token(x_eda_internal_token="wrong")
    assert e.value.status_code == 403