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


@pytest.mark.asyncio(loop_scope="session")
async def test_api_auth_login_wrong_password_401(http):
    """Проверяет POST /api/auth/login с неверным паролем"""
    await http.post("/api/auth/register", json={"login": "carol", "password": "passw0rd1"})
    r = await http.post("/api/auth/login", json={"login": "carol", "password": "wrong-password"})
    assert r.status_code == 401
    body = r.json()
    assert body["status"] == "error"
    assert body["code"] == "INVALID_CREDENTIALS"
    assert body["message"] == "Неверный логин или пароль"


@pytest.mark.asyncio(loop_scope="session")
async def test_api_auth_login_unknown_user_404(http):
    """Проверяет POST /api/auth/login с несуществующим логином"""
    r = await http.post(
        "/api/auth/login",
        json={"login": "user_that_does_not_exist_12345", "password": "passw0rd1"},
    )
    assert r.status_code == 404
    body = r.json()
    assert body["status"] == "error"
    assert body["code"] == "USER_NOT_FOUND"
    assert body["details"].get("login") == "user_that_does_not_exist_12345"


@pytest.mark.asyncio(loop_scope="session")
async def test_api_auth_register_duplicate_login_409(http):
    """Проверяет повторную регистрацию с тем же логином"""
    r1 = await http.post("/api/auth/register", json={"login": "dave", "password": "passw0rd1"})
    assert r1.status_code == 201

    r2 = await http.post("/api/auth/register", json={"login": "dave", "password": "otherpass1"})
    assert r2.status_code == 409
    body = r2.json()
    assert body["status"] == "error"
    assert body["code"] == "USER_ALREADY_EXISTS"
    assert body["details"].get("login") == "dave"