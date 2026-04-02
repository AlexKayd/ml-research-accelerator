from app.schemas.dataset_schemas import DatasetWithFilesResponse


# избранное возвращает тот же DTO, что и datasets, но ограниченный датасетами из favorite_datasets конкретного пользователя
FavoriteDatasetResponse = DatasetWithFilesResponse