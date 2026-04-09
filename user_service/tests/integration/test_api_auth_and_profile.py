import pytest


@pytest.mark.asyncio(loop_scope="session")
async def test_api_auth_register_login_refresh(http):
    """Проверяет API auth"""
    r = await http.post("/api/auth/register", json={"login": "alice", "password": "passw0rd1"})
    assert r.status_code == 201
    body = r.json()
    assert body["login"] == "alice"
    assert "user_id" in body

    r = await http.post("/api/auth/login", json={"login": "alice", "password": "passw0rd1"})
    assert r.status_code == 200
    body = r.json()
    assert body["token_type"] == "bearer"
    assert body["access_token"]
    assert body["refresh_token"]

    refresh_token = body["refresh_token"]

    r = await http.post("/api/auth/refresh", json={"refresh_token": refresh_token})
    assert r.status_code == 200
    body2 = r.json()
    assert body2["access_token"]
    assert body2["refresh_token"] == refresh_token
    assert body2["user"]["login"] == "alice"


@pytest.mark.asyncio(loop_scope="session")
async def test_api_users_me_requires_bearer(http):
    """Проверяет, что /api/users/me требует Bearer и с Bearer возвращает профиль"""
    r = await http.get("/api/users/me")
    assert r.status_code == 401

    await http.post("/api/auth/register", json={"login": "bob", "password": "passw0rd1"})
    r = await http.post("/api/auth/login", json={"login": "bob", "password": "passw0rd1"})
    assert r.status_code == 200
    access = r.json()["access_token"]

    r = await http.get("/api/users/me", headers={"Authorization": f"Bearer {access}"})
    assert r.status_code == 200
    assert r.json()["login"] == "bob"