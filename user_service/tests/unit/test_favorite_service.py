import pytest
from app.domain.exceptions import DatasetNotFoundError, FavoriteAlreadyExistsError, FavoriteNotFoundError
from app.domain.user import FavoriteDataset
from app.service.favorite_service import FavoriteService


class FakeDatasetRepo:
    def __init__(self, existing: set[int]) -> None:
        self._existing = set(existing)

    async def exists(self, dataset_id: int) -> bool:
        return int(dataset_id) in self._existing

    async def get_favorite_datasets_with_data_files_and_user_reports(self, user_id: int):
        return [{"dataset_id": 1, "title": "demo", "files": [], "has_user_report": False}]


class FakeFavoriteRepo:
    def __init__(self) -> None:
        self._pairs: set[tuple[int, int]] = set()

    async def add(self, user_id: int, dataset_id: int) -> FavoriteDataset:
        key = (int(user_id), int(dataset_id))
        if key in self._pairs:
            raise FavoriteAlreadyExistsError(user_id=user_id, dataset_id=dataset_id)
        self._pairs.add(key)
        return FavoriteDataset(user_id=user_id, dataset_id=dataset_id)

    async def remove(self, user_id: int, dataset_id: int) -> bool:
        key = (int(user_id), int(dataset_id))
        if key not in self._pairs:
            return False
        self._pairs.remove(key)
        return True


@pytest.mark.asyncio
async def test_add_to_favorites_success():
    """Проверяет добавление датасета в избранное"""
    svc = FavoriteService(FakeFavoriteRepo(), FakeDatasetRepo(existing={10}))
    fav = await svc.add_to_favorites(user_id=1, dataset_id=10)
    assert fav.user_id == 1
    assert fav.dataset_id == 10


@pytest.mark.asyncio
async def test_add_to_favorites_dataset_not_found_404():
    """Проверяет, что при несуществующем dataset_id получаем 404 DATASET_NOT_FOUND"""
    svc = FavoriteService(FakeFavoriteRepo(), FakeDatasetRepo(existing=set()))
    with pytest.raises(DatasetNotFoundError) as e:
        await svc.add_to_favorites(user_id=1, dataset_id=999)
    assert e.value.status_code == 404
    assert e.value.code == "DATASET_NOT_FOUND"


@pytest.mark.asyncio
async def test_add_to_favorites_duplicate_409():
    """Проверяет, что повторное добавление в избранное даёт 409 FAVORITE_ALREADY_EXISTS"""
    svc = FavoriteService(FakeFavoriteRepo(), FakeDatasetRepo(existing={10}))
    await svc.add_to_favorites(user_id=1, dataset_id=10)
    with pytest.raises(FavoriteAlreadyExistsError) as e:
        await svc.add_to_favorites(user_id=1, dataset_id=10)
    assert e.value.status_code == 409
    assert e.value.code == "FAVORITE_ALREADY_EXISTS"


@pytest.mark.asyncio
async def test_remove_from_favorites_success():
    """Проверяет удаление датасета из избранного"""
    svc = FavoriteService(FakeFavoriteRepo(), FakeDatasetRepo(existing={10}))
    await svc.add_to_favorites(user_id=1, dataset_id=10)
    await svc.remove_from_favorites(user_id=1, dataset_id=10)


@pytest.mark.asyncio
async def test_remove_from_favorites_missing_404():
    """Проверяет, что удаление отсутствующей связи даёт 404 FAVORITE_NOT_FOUND"""
    svc = FavoriteService(FakeFavoriteRepo(), FakeDatasetRepo(existing={10}))
    with pytest.raises(FavoriteNotFoundError) as e:
        await svc.remove_from_favorites(user_id=1, dataset_id=10)
    assert e.value.status_code == 404
    assert e.value.code == "FAVORITE_NOT_FOUND"


@pytest.mark.asyncio
async def test_list_favorites_with_data_files_and_has_user_report():
    """Проверяет, что сервис возвращает список избранного с деталями"""
    svc = FavoriteService(FakeFavoriteRepo(), FakeDatasetRepo(existing={10}))
    rows = await svc.get_all_favorites_with_details(user_id=1)
    assert isinstance(rows, list)
    assert rows and "dataset_id" in rows[0]