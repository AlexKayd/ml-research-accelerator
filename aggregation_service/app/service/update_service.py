import asyncio
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.domain.entities import Dataset, File, AggregationResult
from app.domain.value_objects import DatasetStatus
from app.domain.interfaces import IDatasetRepository, ISourceClient
from app.domain.exceptions import DatasetTooLargeError, InvalidFileError
from app.core.config import get_settings
from app.service.file_processor import FileProcessor
from app.service.eda_notifier import EDANotifier
from app.service.log_labels import format_source_log

logger = logging.getLogger(__name__)


def _find_file_in_extract_result(
    processed_files: List[Dict[str, Any]],
    file_name: str,
) -> Optional[Dict[str, Any]]:
    """Выбирает строку из результата extract_and_hash_files по логическому имени"""
    if not processed_files:
        return None
    want = file_name.replace("\\", "/")
    for row in processed_files:
        got = row.get("file_name", "")
        if isinstance(got, str) and got.replace("\\", "/") == want:
            return row
    base = want.rsplit("/", 1)[-1]
    matches = [
        row
        for row in processed_files
        if isinstance(row.get("file_name"), str)
        and row["file_name"].replace("\\", "/").rsplit("/", 1)[-1] == base
    ]
    if len(matches) == 1:
        return matches[0]
    if len(matches) > 1:
        logger.warning(
            "Несколько файлов с basename=%r при сопоставлении %r; нужен точный путь в БД",
            base,
            file_name,
        )
    return None


class UpdateService:
    
    def __init__(
        self,
        session: AsyncSession,
        dataset_repository: IDatasetRepository,
        source_client: ISourceClient,
        file_processor: FileProcessor,
        eda_notifier: EDANotifier,
        source: str,
        batch_size: Optional[int] = None,
        limit: Optional[int] = None,
        uci_skip_date_optimization: bool = False,
        kaggle_skip_date_optimization: bool = False,
        uci_force_hash_recalc_on_same_size: bool = False,
        kaggle_force_hash_recalc_on_same_size: bool = False,
    ) -> None:
        s = get_settings()
        if limit is None:
            limit = int(s.UPDATE_BATCH_SIZE)
        if batch_size is None:
            batch_size = int(s.UPDATE_BATCH_SIZE)
        self._session = session
        self._repo = dataset_repository
        self._client = source_client
        self._file_processor = file_processor
        self._eda_notifier = eda_notifier
        self._source = source
        self._batch_size = batch_size
        self._limit = limit
        self._uci_skip_date_optimization = uci_skip_date_optimization
        self._kaggle_skip_date_optimization = kaggle_skip_date_optimization
        self._uci_force_hash_recalc_on_same_size = uci_force_hash_recalc_on_same_size
        self._kaggle_force_hash_recalc_on_same_size = kaggle_force_hash_recalc_on_same_size
        self._max_file_size_kb = int(s.MAX_FILE_SIZE_KB)

        logger.debug(
            f"Инициализирован UpdateService для источника '{source}', "
            f"batch_size={batch_size}, limit={limit}"
        )

    async def _flush_eda_notifications_after_batch(self) -> None:
        """Отправляет в EDA все уведомления, накопленные за текущий батч"""
        if self._eda_notifier.get_pending_count() <= 0:
            return
        sent = await self._eda_notifier.send_notifications()
        if sent:
            logger.info(
                "%sПосле батча проверки обновлений: отправлено %s уведомлений в EDA",
                format_source_log(self._source),
                sent,
            )
    
    async def run_updates(self) -> AggregationResult:
        """Запускает процесс проверки обновлений для всех активных датасетов"""
        logger.info("%sНачало проверки обновлений", format_source_log(self._source))
        
        result = AggregationResult(
            started_at=datetime.now()
        )
        
        temp_dir = None
        offset = 0
        
        try:
            while True:
                logger.debug(f"Выборка датасетов: offset={offset}, limit={self._limit}")
                datasets = await self._repo.get_active_datasets_by_source(
                    source=self._source,
                    limit=self._limit,
                    offset=offset
                )
                
                if not datasets:
                    logger.debug("Больше нет активных датасетов для проверки")
                    break
                
                logger.info(
                    "%sПолучено %s датасетов для проверки (offset=%s)",
                    format_source_log(self._source),
                    len(datasets),
                    offset,
                )
                
                temp_dir = await self._file_processor.create_temp_directory(
                    prefix=f"{self._source}_upd_"
                )

                batch_result = AggregationResult()
                
                for dataset in datasets:
                    await self._check_single_dataset(
                        dataset=dataset,
                        temp_dir=temp_dir,
                        result=batch_result
                    )
                
                if temp_dir:
                    await self._file_processor.cleanup_temp_directory(temp_dir)
                    temp_dir = None

                await self._flush_eda_notifications_after_batch()

                result.merge_from(batch_result)
                logger.info(
                    "%s%s\n%s",
                    format_source_log(self._source),
                    f"Проверка обновлений: батч (offset={offset}, датасетов={len(datasets)})",
                    batch_result.get_update_summary("Проверка обновлений (батч)"),
                )
                
                offset = max(offset, max(ds.dataset_id for ds in datasets))
                
                await asyncio.sleep(1)
            
        except Exception as e:
            logger.error(
                "%sКритическая ошибка при проверке обновлений: %s",
                format_source_log(self._source),
                e,
            )
            result.add_error(f"Критическая ошибка: {str(e)}")
            
        finally:
            if temp_dir:
                await self._file_processor.cleanup_temp_directory(temp_dir)
            
            await self._file_processor.cleanup_all_temp_directories()
            
            if not result.success:
                self._eda_notifier.clear_pending_notifications()
            
            result.completed_at = datetime.now()
            logger.info(
                "%sЗавершение проверки обновлений (итого)\n%s",
                format_source_log(self._source),
                result.get_update_summary("Проверка обновлений"),
            )
        
        return result
    
    async def _check_single_dataset(
        self,
        dataset: Dataset,
        temp_dir: Optional[Any],
        result: AggregationResult
    ) -> None:
        """Проверяет один датасет на наличие обновлений"""
        external_id = dataset.external_id
        
        try:
            logger.debug(f"Проверка датасета: {external_id} (ID={dataset.dataset_id})")
            
            source_exists = await self._client.check_dataset_exists(external_id)
            
            if not source_exists:
                logger.info(
                    "%sДатасет %s удалён из источника, помечаем как deleted",
                    format_source_log(self._source),
                    external_id,
                )
                await self._handle_deleted_dataset(dataset)
                result.mark_dataset_processed(updated=True)
                return
            
            metadata = await self._client.get_metadata(external_id)
            
            should_skip = await self._check_update_optimization(dataset, metadata)
            
            if should_skip:
                logger.debug(f"Датасет {external_id} не изменился (по дате), пропускаем")
                result.mark_dataset_processed(skipped=True)
                return
            
            metadata_changed = await self._check_metadata_changes(dataset, metadata)
            
            current_files_list = await self._client.get_files_list(external_id)
            
            db_files = await self._repo.get_files_by_dataset(dataset.dataset_id)
            
            file_changes = await self._compare_files(
                dataset=dataset,
                db_files=db_files,
                current_files_list=current_files_list,
                temp_dir=temp_dir
            )

            db_source_updated_at_before = dataset.source_updated_at

            if metadata_changed or file_changes['has_changes']:
                await self._apply_changes(
                    dataset=dataset,
                    metadata=metadata,
                    file_changes=file_changes
                )

                await self._session.commit()

                if file_changes.get("has_changes"):
                    fc = (
                        len(file_changes.get("added", []))
                        + len(file_changes.get("updated", []))
                        + len(file_changes.get("deleted", []))
                    )
                    result.add_files_processed(fc)

                logger.info(
                    "%sДатасет %s обновлён",
                    format_source_log(self._source),
                    external_id,
                )
                eda_n = int(file_changes.get("eda_notifications_queued") or 0)
                if eda_n > 0:
                    logger.info(
                        "%sДатасет %s: в очередь уведомлений EDA добавлено событий: %s",
                        format_source_log(self._source),
                        external_id,
                        eda_n,
                    )
                elif metadata_changed and not file_changes.get("has_changes"):
                    logger.info(
                        "%sДатасет %s: изменены только метаданные",
                        format_source_log(self._source),
                        external_id,
                    )
                elif file_changes.get("has_changes") and eda_n == 0:
                    logger.info(
                        "%sДатасет %s: файлы изменились, но без затронутых data-файлов или смены хеша",
                        format_source_log(self._source),
                        external_id,
                    )
                result.mark_dataset_processed(updated=True)
            else:
                from_repo = self._parse_source_updated_at_from_metadata(metadata)
                if db_source_updated_at_before is None and from_repo is not None:
                    await self._repo.update_source_updated_at(
                        dataset_id=dataset.dataset_id,
                        updated_at=from_repo,
                    )
                    dataset.source_updated_at = from_repo
                    await self._session.commit()
                    logger.info(
                        "%sДатасет %s: без изменений контента, записан source_updated_at из источника "
                        "(ранее NULL)",
                        format_source_log(self._source),
                        external_id,
                    )
                    result.mark_dataset_processed(updated=True)
                else:
                    result.mark_dataset_processed(skipped=True)
            
        except DatasetTooLargeError as e:
            logger.warning(f"Датасет {external_id} превышает лимит размера: {e.message}")
            await self._handle_size_error(dataset)
            await self._session.commit()
            result.mark_dataset_processed(updated=True)

        except InvalidFileError as e:
            logger.warning(f"Датасет {external_id}: недопустимый файл: {e.message}")
            await self._handle_size_error(dataset)
            await self._session.commit()
            result.mark_dataset_processed(updated=True)

        except Exception as e:
            logger.error(f"Ошибка проверки датасета {external_id}: {e}")
            result.mark_dataset_processed(failed=True)
            result.add_error(f"Датасет {external_id}: {str(e)}")
            await self._session.rollback()
    
    def _normalize_dt_for_compare(self, dt: datetime) -> datetime:
        """Приводит дату к сравнению"""
        return dt.replace(microsecond=0)

    def _parse_source_updated_at_from_metadata(
        self, metadata: Optional[Dict[str, Any]]
    ) -> Optional[datetime]:
        """Дата из метаданных источника или None"""
        if not metadata:
            return None
        val = metadata.get("last_modified") or metadata.get("lastUpdated")

        if isinstance(val, datetime):
            return val
        if isinstance(val, str):
            try:
                return datetime.fromisoformat(val.replace("Z", "+00:00"))
            except ValueError:
                return None
        return None

    def _merge_source_updated_at_for_persist(
        self,
        dataset: Dataset,
        metadata: Optional[Dict[str, Any]],
    ) -> None:
        """Обработка даты обновления из источника"""
        from_repo = self._parse_source_updated_at_from_metadata(metadata)
        if dataset.source_updated_at is not None:
            if from_repo is not None:
                dataset.source_updated_at = from_repo
            return
        if from_repo is not None:
            dataset.source_updated_at = from_repo

    def _extract_uci_freshness_datetime(
        self, metadata: Dict[str, Any]
    ) -> Optional[datetime]:
        """Дата актуальности для UCI"""
        lm = metadata.get('last_modified')

        if lm is None:
            return None
        if isinstance(lm, datetime):
            return lm
        if isinstance(lm, str):
            try:
                return datetime.fromisoformat(lm.replace('Z', '+00:00'))
            except ValueError:
                return None
        return None

    def _uci_should_skip_full_update_by_date(
        self,
        dataset: Dataset,
        metadata: Dict[str, Any],
    ) -> bool:
        """UCI: пропуск если дата из метаданных есть, корректна и совпадает с датой в бд."""
        if not dataset.source_updated_at:
            return False

        api_dt = self._extract_uci_freshness_datetime(metadata)
        if api_dt is None:
            logger.debug(
                "UCI: нет корректной last_modified - полная сверка"
            )
            return False

        try:
            db_dt = self._normalize_dt_for_compare(dataset.source_updated_at)
            api_norm = self._normalize_dt_for_compare(api_dt)
            if db_dt == api_norm:
                logger.debug(
                    "UCI: даты совпали - пропуск полной проверки"
                )
                return True
        except Exception as e:
            logger.debug(f"UCI: ошибка сравнения дат, полная сверка: {e}")

        return False

    def _kaggle_should_skip_full_update_by_date(
        self,
        dataset: Dataset,
        metadata: Dict[str, Any],
    ) -> bool:
        """Kaggle: пропуск если дата из метаданных есть, корректна и совпадает с датой в бд."""
        if not dataset.source_updated_at:
            return False

        try:
            last_updated = metadata.get('lastUpdated') or metadata.get('last_modified')

            if not last_updated:
                return False

            if isinstance(last_updated, str):
                try:
                    last_updated = datetime.fromisoformat(
                        last_updated.replace('Z', '+00:00')
                    )
                except ValueError:
                    return False

            db_date = self._normalize_dt_for_compare(dataset.source_updated_at)
            api_date = self._normalize_dt_for_compare(last_updated)

            if db_date == api_date:
                return True

        except Exception as e:
            logger.debug(f"Kaggle: не удалось выполнить оптимизацию по дате: {e}")

        return False

    async def _check_update_optimization(
        self,
        dataset: Dataset,
        metadata: Dict[str, Any],
    ) -> bool:
        """Проверяет, можно ли пропустить полную проверку только по дате"""
        if self._source == 'uci':
            if self._uci_skip_date_optimization:
                return False
            return self._uci_should_skip_full_update_by_date(dataset, metadata)
        if self._source == 'kaggle':
            if self._kaggle_skip_date_optimization:
                return False
            return self._kaggle_should_skip_full_update_by_date(dataset, metadata)

        return False
    
    async def _check_metadata_changes(
        self,
        dataset: Dataset,
        metadata: Dict[str, Any]
    ) -> bool:
        """Сравнивает метаданные датасета с данными из источника"""
        changed = False
        
        if dataset.title != metadata.get('title', dataset.title):
            changed = True
            logger.info(f"Изменилось title для {dataset.external_id}")
        
        if dataset.description != metadata.get('description', dataset.description):
            changed = True
            logger.info(f"Изменилось description для {dataset.external_id}")
        
        db_tags = set(dataset.tags or [])
        api_tags = set(metadata.get('tags', []) or metadata.get('keywords', []))
        if db_tags != api_tags:
            changed = True
            logger.info(f"Изменились tags для {dataset.external_id}")
        
        if dataset.repository_url != metadata.get('repository_url', dataset.repository_url):
            changed = True
            logger.info(f"Изменился repository_url для {dataset.external_id}")
        
        return changed
    
    async def _compare_files(
        self,
        dataset: Dataset,
        db_files: List[File],
        current_files_list: List[Dict[str, Any]],
        temp_dir: Optional[Any]
    ) -> Dict[str, Any]:
        """Сравнивает файлы из бд с текущими файлами из источника"""
        changes = {
            'has_changes': False,
            'added': [],
            'deleted': [],
            'updated': [],
            'size_changed': False,
            'eda_notifications_queued': 0,
        }
        
        db_files_dict = {f.file_name: f for f in db_files}
        current_files_dict = {f['file_name']: f for f in current_files_list}
        
        db_file_names = set(db_files_dict.keys())
        current_file_names = set(current_files_dict.keys())

        shared_archive_path: Optional[str] = None

        async def _ensure_dataset_archive() -> str:
            nonlocal shared_archive_path
            if shared_archive_path is not None:
                return shared_archive_path
            if temp_dir is None:
                raise RuntimeError(
                    "temp_dir обязателен для скачивания архива при обновлении файлов"
                )
            logger.debug(
                "%sСкачивание архива для датасета %s",
                format_source_log(self._source),
                dataset.external_id,
            )
            shared_archive_path = await self._client.download_dataset(
                external_id=dataset.external_id,
                target_dir=str(temp_dir),
            )
            return shared_archive_path
        
        deleted_files = db_file_names - current_file_names
        for file_name in deleted_files:
            db_file = db_files_dict[file_name]
            changes['deleted'].append(db_file)
            changes['has_changes'] = True
            
            logger.info(f"Файл удалён в источнике: {file_name}")
            
            if db_file.is_data:
                self._eda_notifier.add_file_notification(
                    event_type='file_deleted',
                    dataset_id=dataset.dataset_id,
                    file_id=getattr(db_file, "file_id", None),
                    file_name=file_name,
                    external_id=dataset.external_id,
                    source=self._source
                )
                changes['eda_notifications_queued'] += 1
            
            await self._repo.delete_file(dataset.dataset_id, file_name)
        
        added_files = current_file_names - db_file_names
        for file_name in added_files:
            current_file = current_files_dict[file_name]
            size_kb = round(current_file.get('size_bytes', 0) / 1024, 2)
            
            if size_kb > self._max_file_size_kb:
                logger.error(
                    "Новый файл %s превышает лимит %s КБ",
                    file_name,
                    self._max_file_size_kb,
                )
                raise DatasetTooLargeError(
                    file_name=file_name,
                    file_size_kb=size_kb,
                    max_size_kb=float(self._max_file_size_kb),
                )
            
            new_file = await self._process_new_file(
                dataset=dataset,
                file_name=file_name,
                file_data=current_file,
                temp_dir=temp_dir,
                download_path=await _ensure_dataset_archive(),
            )
            
            if new_file:
                changes['added'].append(new_file)
                changes['has_changes'] = True
                
                logger.info(f"Добавлен новый файл: {file_name}")

                await self._repo.add_file(dataset.dataset_id, new_file)
        
        existing_files = db_file_names & current_file_names
        for file_name in existing_files:
            db_file = db_files_dict[file_name]
            current_file = current_files_dict[file_name]
            
            cur_sz = int(current_file.get("size_bytes", 0) or 0)
            current_size_kb = round(cur_sz / 1024, 2)

            if cur_sz <= 0:
                raise InvalidFileError(
                    f"Файл '{file_name}' в источнике имеет нулевой размер",
                    file_name=file_name,
                )
            
            if current_size_kb > self._max_file_size_kb:
                logger.error(
                    "Файл %s превышает лимит %s КБ",
                    file_name,
                    self._max_file_size_kb,
                )
                raise DatasetTooLargeError(
                    file_name=file_name,
                    file_size_kb=current_size_kb,
                    max_size_kb=float(self._max_file_size_kb),
                )
            
            size_changed = abs(db_file.file_size_kb - current_size_kb) > 0.01

            force_hash_recalc = False
            if db_file.is_data:
                if self._source == 'uci':
                    force_hash_recalc = self._uci_force_hash_recalc_on_same_size
                elif self._source == 'kaggle':
                    force_hash_recalc = self._kaggle_force_hash_recalc_on_same_size
            
            if size_changed:
                changes['size_changed'] = True
                changes['has_changes'] = True
                
                db_file.file_size_kb = current_size_kb
                db_file.file_updated_at = datetime.now()
                await self._repo.update_file(dataset.dataset_id, db_file)
                
                logger.info(f"Изменился размер файла: {file_name}")
                
            if db_file.is_data and (size_changed or force_hash_recalc):
                if force_hash_recalc and not size_changed:
                    logger.debug(
                        "Принудительный пересчёт хеша data-файла без изменения размера: %s",
                        file_name,
                    )

                updated_file = await self._update_file_hash(
                    dataset=dataset,
                    file=db_file,
                    temp_dir=temp_dir,
                    download_path=await _ensure_dataset_archive(),
                )
                
                if updated_file:
                    changes['updated'].append(updated_file)
                    changes['has_changes'] = True
                    
                    self._eda_notifier.add_file_notification(
                        event_type='file_updated',
                        dataset_id=dataset.dataset_id,
                        file_id=getattr(db_file, "file_id", None),
                        file_name=file_name,
                        file_hash=updated_file.file_hash,
                        external_id=dataset.external_id,
                        source=self._source
                    )
                    changes['eda_notifications_queued'] += 1
                    
                    logger.debug(f"Изменился хеш файла: {file_name}")
        
        if changes['has_changes']:
            new_total_size = await self._repo.recalculate_dataset_size(dataset.dataset_id)
            dataset.dataset_size_kb = new_total_size
            changes['size_changed'] = True
        
        return changes
    
    async def _process_new_file(
        self,
        dataset: Dataset,
        file_name: str,
        file_data: Dict[str, Any],
        temp_dir: Optional[Any],
        download_path: Optional[str] = None,
    ) -> Optional[File]:
        """Обрабатывает новый файл"""
        try:
            path = download_path
            if path is None:
                path = await self._client.download_dataset(
                    external_id=dataset.external_id,
                    target_dir=str(temp_dir),
                )
            
            processed_files = await self._client.extract_and_hash_files(
                download_path=path,
                files_list=[file_data],
            )
            
            file_info = _find_file_in_extract_result(processed_files, file_name)
            if file_info:
                return File(
                    file_name=file_info['file_name'],
                    file_size_kb=file_info['file_size_kb'],
                    is_data=file_info['is_data'],
                    file_hash=file_info.get('file_hash'),
                    file_updated_at=datetime.now()
                )
            
        except Exception as e:
            logger.error(f"Ошибка обработки нового файла {file_name}: {e}")
        
        return None
    
    async def _update_file_hash(
        self,
        dataset: Dataset,
        file: File,
        temp_dir: Optional[Any],
        download_path: Optional[str] = None,
    ) -> Optional[File]:
        """Пересчитывает хеш для существующего data-файла после изменения размера в источнике"""
        old_hash = file.file_hash

        try:
            path = download_path
            if path is None:
                path = await self._client.download_dataset(
                    external_id=dataset.external_id,
                    target_dir=str(temp_dir),
                )

            file_meta = {
                'file_name': file.file_name,
                'size_bytes': int(round(file.file_size_kb * 1024)),
            }

            processed_files = await self._client.extract_and_hash_files(
                download_path=path,
                files_list=[file_meta],
            )

            if not processed_files:
                logger.warning(
                    f"Пустой результат extract_and_hash_files для {file.file_name}"
                )
                return None

            file_info = _find_file_in_extract_result(processed_files, file.file_name)
            if not file_info:
                logger.warning(
                    "Файл %s не найден среди результатов распаковки (%s записей)",
                    file.file_name,
                    len(processed_files),
                )
                return None

            new_hash = file_info.get('file_hash')

            if file.is_data and not new_hash:
                logger.warning(
                    f"Не удалось вычислить хеш для data-файла {file.file_name}"
                )
                return None

            if file_info.get('file_size_kb') is not None:
                file.file_size_kb = float(file_info['file_size_kb'])

            if new_hash == old_hash:
                return None

            file.file_hash = new_hash
            file.file_updated_at = datetime.now()
            await self._repo.update_file(dataset.dataset_id, file)
            return file

        except Exception as e:
            logger.error(f"Ошибка обновления хеша файла {file.file_name}: {e}")

        return None
    
    async def _handle_deleted_dataset(self, dataset: Dataset) -> None:
        """Обрабатывает удаление датасета из источника"""
        dataset.mark_as_deleted()
        await self._repo.update_dataset_status(
            dataset_id=dataset.dataset_id,
            status=DatasetStatus.DELETED.value
        )
        await self._repo.update_source_updated_at(
            dataset_id=dataset.dataset_id,
            updated_at=datetime.now()
        )
        
    
    async def _handle_size_error(self, dataset: Dataset) -> None:
        """Обрабатывает ошибку превышения размера файла"""
        dataset.mark_as_error()
        await self._repo.update_dataset_status(
            dataset_id=dataset.dataset_id,
            status=DatasetStatus.ERROR.value
        )
        await self._repo.update_source_updated_at(
            dataset_id=dataset.dataset_id,
            updated_at=datetime.now()
        )
        
    
    async def _apply_changes(
        self,
        dataset: Dataset,
        metadata: Dict[str, Any],
        file_changes: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Применяет изменения к датасету в бд"""
        self._merge_source_updated_at_for_persist(dataset, metadata)

        if metadata:
            dataset.title = metadata.get('title', dataset.title)
            dataset.description = metadata.get('description', dataset.description)
            dataset.tags = metadata.get('tags', []) or metadata.get('keywords', [])
            dataset.repository_url = metadata.get(
                'repository_url',
                dataset.repository_url
            )

            await self._repo.update_dataset(dataset)
        else:
            await self._repo.update_source_updated_at(
                dataset_id=dataset.dataset_id,
                updated_at=dataset.source_updated_at,
            )