import asyncio
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.domain.entities import Dataset, File, AggregationResult
from app.domain.value_objects import DatasetStatus
from app.domain.interfaces import IDatasetRepository, ISourceClient
from app.domain.exceptions import DatasetTooLargeError, InvalidFileError, NoValidFilesError, AggregationError
from app.core.config import get_settings
from app.service.file_processor import FileProcessor
from app.service.log_labels import format_source_log
from app.clients.kaggle_client import kaggle_metadata_has_tabular_tag

logger = logging.getLogger(__name__)


class AggregationService:
    
    def __init__(
        self,
        session: AsyncSession,
        dataset_repository: IDatasetRepository,
        source_client: ISourceClient,
        file_processor: FileProcessor,
        source: str,
        batch_size: Optional[int] = None,
    ) -> None:
        if batch_size is None:
            batch_size = int(get_settings().AGGREGATION_BATCH_SIZE)
        self._session = session
        self._repo = dataset_repository
        self._client = source_client
        self._file_processor = file_processor
        self._source = source
        self._batch_size = batch_size
        
        logger.debug(
            f"Инициализирован AggregationService для источника '{source}', "
            f"batch_size={batch_size}"
        )
    
    async def run_aggregation(self) -> AggregationResult:
        """Запускает процесс первичной агрегации новых датасетов"""
        logger.info("%sНачало первичной агрегации", format_source_log(self._source))
        
        result = AggregationResult(
            started_at=datetime.now()
        )
        
        temp_dir = None
        
        try:
            logger.debug("%sПолучение списка ID датасетов из источника", format_source_log(self._source))
            all_ids = await self._client.list_dataset_ids(batch_size=self._batch_size)
            logger.info(
                "%sПолучено %s ID датасетов из источника",
                format_source_log(self._source),
                len(all_ids),
            )
            
            total_batches = (len(all_ids) + self._batch_size - 1) // self._batch_size
            for i in range(0, len(all_ids), self._batch_size):
                batch_ids = all_ids[i:i + self._batch_size]
                batch_num = i // self._batch_size + 1
                logger.debug(
                    "Обработка батча %s/%s: %s датасетов",
                    batch_num,
                    total_batches,
                    len(batch_ids),
                )
                
                temp_dir = await self._file_processor.create_temp_directory(
                    prefix=f"{self._source}_agg_"
                )

                batch_result = AggregationResult()
                
                for external_id in batch_ids:
                    await self._process_single_dataset(
                        external_id=external_id,
                        temp_dir=temp_dir,
                        result=batch_result
                    )
                
                if temp_dir:
                    await self._file_processor.cleanup_temp_directory(temp_dir)
                    temp_dir = None

                result.merge_from(batch_result)
                logger.info(
                    "%s%s\n%s",
                    format_source_log(self._source),
                    f"Первичная агрегация: батч {batch_num}/{total_batches} ({len(batch_ids)} датасетов)",
                    batch_result.get_summary("Первичная агрегация (батч)"),
                )
                
                if i + self._batch_size < len(all_ids):
                    await asyncio.sleep(1)
            
        except Exception as e:
            logger.error(
                "%sКритическая ошибка при агрегации: %s",
                format_source_log(self._source),
                e,
            )
            result.add_error(f"Критическая ошибка: {str(e)}")
            
        finally:
            if temp_dir:
                await self._file_processor.cleanup_temp_directory(temp_dir)
            
            await self._file_processor.cleanup_all_temp_directories()
            
            result.completed_at = datetime.now()
            logger.info(
                "%sЗавершение первичной агрегации (итого)\n%s",
                format_source_log(self._source),
                result.get_summary("Первичная агрегация"),
            )
        
        return result
    
    async def _process_single_dataset(
        self,
        external_id: str,
        temp_dir: Optional[Any],
        result: AggregationResult
    ) -> None:
        """Обрабатывает один датасет: проверка, загрузка, валидация, сохранение"""
        try:
            exists = await self._repo.exists(source=self._source, external_id=external_id)
            
            if exists:
                logger.debug(f"Датасет {external_id} уже существует в БД, пропускаем")
                result.mark_dataset_processed(skipped=True)
                return
            
            logger.debug(f"Обработка нового датасета: {external_id}")
            
            source_exists = await self._client.check_dataset_exists(external_id)
            
            if not source_exists:
                logger.debug(f"Датасет {external_id} не найден в источнике, пропускаем")
                result.mark_dataset_processed(skipped=True)
                return
            
            metadata = await self._client.get_metadata(external_id)

            if self._source == "kaggle" and not kaggle_metadata_has_tabular_tag(metadata):
                logger.debug(
                    "%sДатасет %s: нет тега tabular - пропуск",
                    format_source_log(self._source),
                    external_id,
                )
                result.mark_dataset_processed(skipped=True)
                return
            
            files_list = await self._client.get_files_list(external_id)
            
            if not files_list:
                logger.debug(
                    "%sДатасет %s: список файлов из источника пуст - пропуск",
                    format_source_log(self._source),
                    external_id,
                )
                result.mark_dataset_processed(skipped=True)
                return
            
            try:
                validation = await self._client.validate_dataset_files(
                    files_list=files_list,
                    external_id=external_id
                )
            except (DatasetTooLargeError, NoValidFilesError, InvalidFileError) as e:
                logger.debug(f"Датасет {external_id} не прошёл валидацию: {e.message}")
                result.mark_dataset_processed(skipped=True)
                return
            
            domain_files = await self._download_and_hash_files(
                external_id=external_id,
                files_list=files_list,
                temp_dir=temp_dir
            )
            
            if not domain_files:
                logger.warning(
                    "%sНе удалось обработать файлы датасета %s",
                    format_source_log(self._source),
                    external_id,
                )
                result.mark_dataset_processed(failed=True)
                result.add_error(f"Нет файлов для датасета {external_id}")
                return
            
            dataset = self._create_dataset_entity(
                external_id=external_id,
                metadata=metadata,
                files=domain_files,
                validation=validation
            )
            
            dataset_id = await self._repo.save_dataset_with_files(dataset)
            
            await self._session.commit()
            
            logger.info(
                "%sДобавлен новый датасет: %s (ID=%s)",
                format_source_log(self._source),
                external_id,
                dataset_id,
            )
            result.mark_dataset_processed(added=True)
            result.add_files_processed(len(domain_files))
            
        except Exception as e:
            logger.error(
                "%sОшибка обработки датасета %s: %s",
                format_source_log(self._source),
                external_id,
                e,
            )
            result.mark_dataset_processed(failed=True)
            result.add_error(f"Датасет {external_id}: {str(e)}")
            
            await self._session.rollback()
    
    async def _download_and_hash_files(
        self,
        external_id: str,
        files_list: List[Dict[str, Any]],
        temp_dir: Optional[Any]
    ) -> List[File]:
        """Скачивает файлы и вычисляет хеши для data-файлов"""
        domain_files: List[File] = []
        
        try:
            download_path = await self._client.download_dataset(
                external_id=external_id,
                target_dir=str(temp_dir)
            )
            
            processed_files = await self._client.extract_and_hash_files(
                download_path=download_path,
                files_list=files_list
            )
            
            for file_data in processed_files:
                file_entity = File(
                    file_name=file_data['file_name'],
                    file_size_kb=file_data['file_size_kb'],
                    is_data=file_data['is_data'],
                    file_hash=file_data.get('file_hash'),
                    file_updated_at=datetime.now()
                )
                domain_files.append(file_entity)
            
        except Exception as e:
            logger.error(
                "%sОшибка скачивания/хеширования файлов %s: %s",
                format_source_log(self._source),
                external_id,
                e,
            )
            raise AggregationError(
                message=f"Ошибка обработки файлов: {e}",
                source=self._source,
                external_id=external_id
            ) from e
        
        return domain_files
    
    def _create_dataset_entity(
        self,
        external_id: str,
        metadata: Dict[str, Any],
        files: List[File],
        validation: Dict[str, Any]
    ) -> Dataset:
        """Создаёт доменную сущность Dataset из метаданных и файлов"""
        raw_dt = metadata.get("last_modified") or metadata.get("lastUpdated")
        source_updated_at: Optional[datetime] = None

        if isinstance(raw_dt, datetime):
            source_updated_at = raw_dt
        elif isinstance(raw_dt, str):
            try:
                source_updated_at = datetime.fromisoformat(
                    raw_dt.replace("Z", "+00:00")
                )
            except ValueError:
                source_updated_at = None
        
        download_url = metadata.get('download_url') or self._client.get_download_url(
            external_id
        )

        dataset_size_kb = (
            round(sum(float(f.file_size_kb or 0) for f in files), 2)
            if files
            else float(validation.get('total_size_kb') or 0.0)
        )

        return Dataset(
            source=self._source,
            external_id=external_id,
            title=metadata.get('title', external_id),
            description=metadata.get('description'),
            tags=metadata.get('tags', []) or metadata.get('keywords', []),
            dataset_format=validation.get('format'),
            dataset_size_kb=dataset_size_kb,
            status=DatasetStatus.ACTIVE,
            download_url=download_url,
            repository_url=metadata.get('repository_url') or self._client.get_repository_url(external_id),
            source_updated_at=source_updated_at,
            files=files
        )