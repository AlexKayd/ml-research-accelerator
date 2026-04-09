import pytest
from app.domain.exceptions import InvalidCredentialsError, UserAlreadyExistsError, UserNotFoundError
from app.domain.user import User, UserCreate, UserLogin
from app.service.auth_service import AuthService
from app.core.security import create_refresh_token


class FakeUserRepo:
    def __init__(self) -> None:
        self._users_by_id: dict[int, User] = {}
        self._users_by_login: dict[str, User] = {}
        self._next_id = 1

    async def exists_by_login(self, login: str) -> bool:
        return login in self._users_by_login

    async def create(self, user: User) -> User:
        uid = self._next_id
        self._next_id += 1
        created = User(
            user_id=uid,
            login=user.login,
            hashed_password=user.hashed_password,
            created_at=user.created_at,
        )
        self._users_by_id[uid] = created
        self._users_by_login[created.login] = created
        return created

    async def get_by_login(self, login: str):
        return self._users_by_login.get(login)

    async def get_by_id(self, user_id: int):
        return self._users_by_id.get(int(user_id))


@pytest.mark.asyncio
async def test_register_user_success():
    """Проверяет успешную регистрацию: создаётся пользователь, пароль хешируется"""
    repo = FakeUserRepo()
    svc = AuthService(user_repository=repo, secret_key="secret", algorithm="HS256")

    user = await svc.register(UserCreate(login="alice", password="passw0rd1"))
    assert user.user_id is not None
    assert user.login == "alice"
    assert user.hashed_password != "passw0rd1"


@pytest.mark.asyncio
async def test_register_user_duplicate_login_raises_409():
    """Проверяет, что повторная регистрация того же login даёт 409 USER_ALREADY_EXISTS"""
    repo = FakeUserRepo()
    svc = AuthService(user_repository=repo, secret_key="secret", algorithm="HS256")

    await svc.register(UserCreate(login="alice", password="passw0rd1"))
    with pytest.raises(UserAlreadyExistsError) as e:
        await svc.register(UserCreate(login="alice", password="passw0rd1"))
    assert e.value.status_code == 409
    assert e.value.code == "USER_ALREADY_EXISTS"


@pytest.mark.asyncio
async def test_login_success_returns_tokens():
    """Проверяет успешный логин: возвращаются access и refresh токены и профиль"""
    repo = FakeUserRepo()
    svc = AuthService(user_repository=repo, secret_key="secret", algorithm="HS256")

    await svc.register(UserCreate(login="alice", password="passw0rd1"))
    access, refresh, profile = await svc.login(UserLogin(login="alice", password="passw0rd1"))

    assert isinstance(access, str) and access
    assert isinstance(refresh, str) and refresh
    assert profile.user_id is not None
    assert profile.login == "alice"


@pytest.mark.asyncio
async def test_login_wrong_password_raises_401():
    """Проверяет, что неверный пароль даёт 401 INVALID_CREDENTIALS"""
    repo = FakeUserRepo()
    svc = AuthService(user_repository=repo, secret_key="secret", algorithm="HS256")

    await svc.register(UserCreate(login="alice", password="passw0rd1"))
    with pytest.raises(InvalidCredentialsError) as e:
        await svc.login(UserLogin(login="alice", password="wrong-pass"))
    assert e.value.status_code == 401
    assert e.value.code == "INVALID_CREDENTIALS"


@pytest.mark.asyncio
async def test_refresh_token_returns_new_access_same_refresh():
    """Проверяет refresh: access обновляется, refresh остаётся тем же"""
    repo = FakeUserRepo()
    svc = AuthService(user_repository=repo, secret_key="secret", algorithm="HS256")

    await svc.register(UserCreate(login="alice", password="passw0rd1"))
    _access1, refresh, _profile1 = await svc.login(UserLogin(login="alice", password="passw0rd1"))

    access2, refresh2, profile2 = await svc.refresh_tokens(refresh)
    assert access2
    assert refresh2 == refresh
    assert profile2.login == "alice"


@pytest.mark.asyncio
async def test_access_token_validation_and_get_current_user():
    """Проверяет refresh по токену, где user_id отсутствует в репозитории то 404 USER_NOT_FOUND"""
    repo = FakeUserRepo()
    svc = AuthService(user_repository=repo, secret_key="secret", algorithm="HS256")

    refresh = create_refresh_token(user_id=999, secret_key="secret", expire_days=1, algorithm="HS256")
    with pytest.raises(UserNotFoundError) as e:
        await svc.refresh_tokens(refresh)
    assert e.value.status_code == 404
    assert e.value.code == "USER_NOT_FOUND"