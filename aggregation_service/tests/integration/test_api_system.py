import pytest


@pytest.mark.asyncio(loop_scope="session")
async def test_api_ready_returns_200(http):
    r = await http.get("/ready")
    assert r.status_code == 200
    body = r.json()
    assert body.get("ready") is True


@pytest.mark.asyncio(loop_scope="session")
async def test_api_root_returns_service_info(http):
    r = await http.get("/")
    assert r.status_code == 200
    data = r.json()
    assert data.get("service") == "aggregation_service"
    assert "health" in (data.get("endpoints") or {})