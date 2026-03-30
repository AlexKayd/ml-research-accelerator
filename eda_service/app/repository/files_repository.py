import logging
from typing import Optional, Tuple
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from app.domain.exceptions import DatabaseError
from app.domain.entities import FileInfo, DatasetInfo
from app.domain.interfaces import IFilesRepository
from app.repository.models import DatasetORM, FileORM

logger = logging.getLogger(__name__)


class FilesRepository(IFilesRepository):

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def resolve_file_id(self, dataset_id: int, file_name: str) -> Optional[int]:
        """Разрешает file_id по dataset_id и file_name"""
        logger.debug(
            "Разрешение file_id по dataset_id=%s file_name=%r",
            dataset_id,
            file_name,
        )
        try:
            q = select(FileORM.file_id).where(
                FileORM.dataset_id == dataset_id,
                FileORM.file_name == file_name,
            )
            res = await self.session.execute(q)
            return res.scalar_one_or_none()

        except SQLAlchemyError as e:
            logger.error(
                "Ошибка при resolve_file_id (dataset_id=%s file_name=%r): %s",
                dataset_id,
                file_name,
                e,
                exc_info=True,
            )
            raise DatabaseError(
                f"Не удалось разрешить file_id по dataset_id={dataset_id} и file_name={file_name!r}: {e}",
                operation="resolve_file_id",
            )

    async def get_file_info(self, file_id: int) -> Optional[FileInfo]:
        """Возвращает метаданные файла по file_id"""
        logger.debug("Получение FileInfo: file_id=%s", file_id)
        try:
            q = select(FileORM).where(FileORM.file_id == file_id)
            res = await self.session.execute(q)
            row = res.scalar_one_or_none()
            if row is None:
                return None

            return FileInfo(
                file_id=int(row.file_id),
                dataset_id=int(row.dataset_id),
                file_name=str(row.file_name),
                is_data=bool(row.is_data),
                file_hash=row.file_hash,
            )

        except SQLAlchemyError as e:
            logger.error("Ошибка при get_file_info (file_id=%s): %s", file_id, e, exc_info=True)
            raise DatabaseError(
                f"Не удалось получить информацию о файле file_id={file_id}: {e}",
                operation="get_file_info",
            )

    async def get_dataset_info(self, dataset_id: int) -> Optional[DatasetInfo]:
        """Возвращает данные датасета по dataset_id"""
        logger.debug("Получение DatasetInfo: dataset_id=%s", dataset_id)
        try:
            q = select(DatasetORM).where(DatasetORM.dataset_id == dataset_id)
            res = await self.session.execute(q)
            row = res.scalar_one_or_none()
            if row is None:
                return None
            return DatasetInfo(
                dataset_id=int(row.dataset_id),
                download_url=row.download_url,
            )

        except SQLAlchemyError as e:
            logger.error(
                "Ошибка при get_dataset_info (dataset_id=%s): %s",
                dataset_id,
                e,
                exc_info=True,
            )
            raise DatabaseError(
                f"Не удалось получить информацию о датасете dataset_id={dataset_id}: {e}",
                operation="get_dataset_info",
            )

    async def get_file_and_dataset_info(self, file_id: int) -> Optional[Tuple[FileInfo, DatasetInfo]]:
        """Возвращает (FileInfo, DatasetInfo) за один запрос"""
        logger.debug("Получение FileInfo+DatasetInfo: file_id=%s", file_id)
        try:
            q = (
                select(FileORM, DatasetORM)
                .join(DatasetORM, DatasetORM.dataset_id == FileORM.dataset_id)
                .where(FileORM.file_id == file_id)
            )
            res = await self.session.execute(q)
            pair = res.first()
            if pair is None:
                return None
            file_row: FileORM = pair[0]
            dataset_row: DatasetORM = pair[1]

            return (
                FileInfo(
                    file_id=int(file_row.file_id),
                    dataset_id=int(file_row.dataset_id),
                    file_name=str(file_row.file_name),
                    is_data=bool(file_row.is_data),
                    file_hash=file_row.file_hash,
                ),
                DatasetInfo(
                    dataset_id=int(dataset_row.dataset_id),
                    download_url=dataset_row.download_url,
                ),
            )

        except SQLAlchemyError as e:
            logger.error(
                "Ошибка при get_file_and_dataset_info (file_id=%s): %s",
                file_id,
                e,
                exc_info=True,
            )
            raise DatabaseError(
                f"Не удалось получить FileInfo+DatasetInfo для file_id={file_id}: {e}",
                operation="get_file_and_dataset_info",
            )