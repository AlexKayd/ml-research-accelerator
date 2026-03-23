import asyncio
import json
import logging
import os
import re
import tempfile
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional
from kaggle.api.kaggle_api_extended import KaggleApi
from app.core.config import get_settings
from app.clients.base_client import BaseClient
from app.domain.exceptions import (
    SourceUnavailableError,
    DatasetNotFoundError,
    DatasetTooLargeError,
    InvalidFileError,
    NoValidFilesError,
)

logger = logging.getLogger(__name__)


_TABULAR_TAG_RE = re.compile(r"\btabular\b", re.IGNORECASE)


def _is_kaggle_api_http_404(exc: BaseException) -> bool:
    try:
        from kaggle.rest import ApiException
    except ImportError:
        return False

    seen: set[int] = set()
    stack: List[BaseException] = [exc]
    while stack:
        e = stack.pop()
        eid = id(e)
        if eid in seen:
            continue
        seen.add(eid)

        if isinstance(e, ApiException) and getattr(e, "status", None) == 404:
            return True
        if e.__cause__ is not None:
            stack.append(e.__cause__)
        if e.__context__ is not None and e.__context__ is not e.__cause__:
            stack.append(e.__context__)
    return False


def _is_kaggle_api_http_429(exc: BaseException) -> bool:
    try:
        import requests
    except ImportError:
        requests = None
    try:
        from kaggle.rest import ApiException
    except ImportError:
        ApiException = None

    seen: set[int] = set()
    stack: List[BaseException] = [exc]
    while stack:
        e = stack.pop()
        eid = id(e)
        if eid in seen:
            continue
        seen.add(eid)

        if ApiException and isinstance(e, ApiException) and getattr(e, "status", None) == 429:
            return True
        if requests is not None and isinstance(e, requests.exceptions.HTTPError):
            resp = getattr(e, "response", None)
            if resp is not None and getattr(resp, "status_code", None) == 429:
                return True
        if e.__cause__ is not None:
            stack.append(e.__cause__)
        if e.__context__ is not None and e.__context__ is not e.__cause__:
            stack.append(e.__context__)
    return False


def _kaggle_retry_after_seconds(exc: BaseException) -> Optional[float]:
    seen: set[int] = set()
    stack: List[BaseException] = [exc]
    while stack:
        e = stack.pop()
        eid = id(e)
        if eid in seen:
            continue
        seen.add(eid)
        resp = getattr(e, "response", None)

        if resp is not None:
            headers = getattr(resp, "headers", None)
            if headers is not None:
                ra = headers.get("Retry-After")
                if ra is not None:
                    try:
                        return float(ra)
                    except (ValueError, TypeError):
                        pass

        headers = getattr(e, "headers", None)

        if isinstance(headers, dict):
            ra = headers.get("Retry-After")
            if ra is not None:
                try:
                    return float(ra)
                except (ValueError, TypeError):
                    pass

        if e.__cause__ is not None:
            stack.append(e.__cause__)
        if e.__context__ is not None and e.__context__ is not e.__cause__:
            stack.append(e.__context__)
    return None


def _kaggle_dataset_zip_path(api: KaggleApi, external_id: str, target_dir: str) -> str:
    """Путь к zip после dataset_download_files"""
    _owner, dataset_slug, _ver = api.split_dataset_string(external_id)
    return str(Path(target_dir) / f"{dataset_slug}.zip")


def _keywords_from_kaggle_metadata(raw: Dict[str, Any]) -> List[str]:
    """Теги из JSON метаданных"""
    out: List[str] = []
    keywords = raw.get("keywords")

    if isinstance(keywords, list):
        for x in keywords:
            if isinstance(x, str) and x.strip():
                out.append(x.strip())
            elif isinstance(x, dict):
                name = x.get("name") or x.get("ref")
                if name:
                    out.append(str(name))
    if out:
        return out
    tags = raw.get("tags")

    if isinstance(tags, list):
        for t in tags:
            if isinstance(t, dict):
                name = t.get("name") or t.get("ref") or t.get("slug")
                if name:
                    out.append(str(name))
            elif isinstance(t, str) and t.strip():
                out.append(t.strip())
    return out


def kaggle_metadata_has_tabular_tag(metadata: Dict[str, Any]) -> bool:
    """True если есть tabular"""
    tags = metadata.get("keywords")

    if not isinstance(tags, list):
        return False
    for tag in tags:
        if _TABULAR_TAG_RE.search(str(tag)):
            return True
    return False


def _parse_last_updated_from_metadata(raw: Dict[str, Any]) -> Optional[datetime]:
    """Дата обновления из JSON"""
    val = (
        raw.get("last_updated")
        or raw.get("lastUpdated")
        or raw.get("update_time")
        or raw.get("updateTime")
    )
    if val is None and isinstance(raw.get("dataset"), dict):
        ds = raw["dataset"]
        val = (
            ds.get("last_updated")
            or ds.get("lastUpdated")
            or ds.get("update_time")
            or ds.get("updateTime")
        )
    if val is None:
        return None
    if isinstance(val, datetime):
        return val
    s = str(val).strip()
    if not s:
        return None
    try:
        return datetime.fromisoformat(s.replace("Z", "+00:00"))
    except ValueError:
        pass

    try:
        ts = float(s)
        if ts > 1e12:
            ts /= 1000.0
        if ts > 1e9:
            return datetime.fromtimestamp(ts, tz=timezone.utc).replace(tzinfo=None)
    except (ValueError, OSError, OverflowError):
        pass
    return None


def _merge_kaggle_metadata_loaded(loaded: Dict[str, Any]) -> Dict[str, Any]:
    """Объединяет корень JSON и вложенный info"""
    if not isinstance(loaded, dict):
        return {}
    info = loaded.get("info")
    if isinstance(info, dict):
        return {**loaded, **info}
    return dict(loaded)


class KaggleClient(BaseClient):
    
    def __init__(
        self,
        timeout: Optional[float] = None,
        max_retries: Optional[int] = None,
        rate_limit_delay: Optional[float] = None
    ) -> None:
        effective_rl = (
            rate_limit_delay
            if rate_limit_delay is not None
            else float(get_settings().KAGGLE_HTTP_RATE_LIMIT_DELAY_SECONDS)
        )
        super().__init__(
            source_name='kaggle',
            timeout=timeout,
            max_retries=max_retries,
            rate_limit_delay=effective_rl,
        )
        
        self._api = KaggleApi()
        self._api.authenticate()
        self._max_file_size_kb = int(get_settings().MAX_FILE_SIZE_KB)
        self._kaggle_list_429_max_retries = int(get_settings().KAGGLE_LIST_429_MAX_RETRIES)
        self._kaggle_call_429_max_retries = int(get_settings().KAGGLE_CALL_429_MAX_RETRIES)

        logger.debug("Инициализирован клиент Kaggle API")

    async def _run_kaggle_sync_with_429_retry(
        self,
        operation_label: str,
        fn: Callable[[], Any],
    ) -> Any:
        """Выполняет синхронный вызов Kaggle API"""
        consecutive = 0
        while True:
            await self._wait_rate_limit()
            try:
                return await asyncio.to_thread(fn)
            except Exception as e:

                if _is_kaggle_api_http_429(e):
                    consecutive += 1
                    if consecutive > self._kaggle_call_429_max_retries:
                        logger.error(
                            "Kaggle %s: слишком много HTTP 429 (%s попыток)",
                            operation_label,
                            consecutive,
                            exc_info=True,
                        )
                        raise SourceUnavailableError(
                            source="kaggle",
                            reason=(
                                f"Превышен лимит запросов Kaggle (429) при «{operation_label}»"
                            ),
                        ) from e

                    ra = _kaggle_retry_after_seconds(e)
                    exp = min(
                        600.0,
                        20.0 * (2 ** min(consecutive - 1, 5)),
                    )
                    wait_s = ra if ra is not None else exp
                    logger.warning(
                        "Kaggle %s: HTTP 429, повтор %s/%s, пауза %.1f с",
                        operation_label,
                        consecutive,
                        self._kaggle_call_429_max_retries,
                        wait_s,
                    )
                    await asyncio.sleep(wait_s)
                    continue
                raise

    def _last_updated_from_dataset_list_sync(self, external_id: str) -> Optional[datetime]:
        """Резервный источник даты обновления"""
        parts = external_id.strip().split("/")
        if len(parts) != 2:
            return None
        owner, slug = parts[0], parts[1]
        
        try:
            rows = self._api.dataset_list(
                user=owner,
                search=slug,
                page=1,
                max_size=50,
            )
        except Exception as e:
            logger.debug(
                "Kaggle: не удалось получить lastUpdated через dataset_list(%s): %s",
                external_id,
                e,
            )
            return None

        if not rows:
            return None
        for ds in rows:
            ref = getattr(ds, "ref", None)
            if ref != external_id:
                continue
            v = getattr(ds, "last_updated", None)
            if v is None:
                v = getattr(ds, "lastUpdated", None)
            if v is None:
                return None
            if isinstance(v, datetime):
                if v.tzinfo is not None:
                    return v.replace(tzinfo=None)
                return v
            return _parse_last_updated_from_metadata({"lastUpdated": v})
        return None
    
    async def list_dataset_ids(
        self, 
        batch_size: Optional[int] = None
    ) -> List[str]:
        """Получает список ID Kaggle только для tabular и csv/json."""
        logger.debug(
            "Получение списка датасетов Kaggle (tabular и csv/json), batch_size=%s",
            batch_size,
        )

        dataset_ids: List[str] = []
        seen_ids: set[str] = set()
        file_types = ("csv", "json")

        for file_type in file_types:
            page = 1
            consecutive_429_on_page = 0
            while True:
                await self._wait_rate_limit()
                try:
                    datasets = self._api.dataset_list(
                        page=page,
                        sort_by="updated",
                        file_type=file_type,
                        tag_ids="tabular",
                    )
                    consecutive_429_on_page = 0
                except Exception as e:
                    if _is_kaggle_api_http_429(e):
                        consecutive_429_on_page += 1
                        if consecutive_429_on_page > self._kaggle_list_429_max_retries:
                            logger.error(
                                "Kaggle dataset_list: слишком много 429 подряд "
                                "(тип=%s, страница %s, попыток %s)",
                                file_type,
                                page,
                                consecutive_429_on_page,
                                exc_info=True,
                            )
                            raise SourceUnavailableError(
                                source="kaggle",
                                reason=(
                                    "Превышен лимит запросов Kaggle (429) при обходе "
                                    f"каталога tabular/{file_type} (страница {page})"
                                ),
                            ) from e
                        ra = _kaggle_retry_after_seconds(e)
                        exp = min(
                            600.0,
                            20.0 * (2 ** min(consecutive_429_on_page - 1, 5)),
                        )
                        wait_s = ra if ra is not None else exp
                        logger.warning(
                            "Kaggle dataset_list: HTTP 429 (тип=%s, страница %s), "
                            "повтор %s/%s, пауза %.1f с",
                            file_type,
                            page,
                            consecutive_429_on_page,
                            self._kaggle_list_429_max_retries,
                            wait_s,
                        )
                        await asyncio.sleep(wait_s)
                        continue
                    consecutive_429_on_page = 0

                    if _is_kaggle_api_http_404(e) and page > 1:
                        logger.info(
                            "Kaggle dataset_list: тип=%s, страница %s вернула HTTP 404 — "
                            "конец пагинации",
                            file_type,
                            page,
                        )
                        break

                    if _is_kaggle_api_http_404(e) and page == 1:
                        logger.error(
                            "Kaggle dataset_list: 404 на первой странице (тип=%s): %s",
                            file_type,
                            e,
                            exc_info=True,
                        )
                        raise SourceUnavailableError(
                            source="kaggle",
                            reason=(
                                "Список датасетов Kaggle недоступен (404) "
                                f"для tabular/{file_type}: {e}"
                            ),
                        ) from e
                    logger.error(
                        "Kaggle dataset_list не удался (тип=%s, страница %s): %s",
                        file_type,
                        page,
                        e,
                        exc_info=True,
                    )
                    raise SourceUnavailableError(
                        source="kaggle",
                        reason=(
                            "Ошибка получения списка датасетов "
                            f"(tabular/{file_type}, страница {page}): {e}"
                        ),
                    ) from e

                if not datasets:
                    break

                for ds in datasets:
                    if hasattr(ds, "ref") and ds.ref and ds.ref not in seen_ids:
                        seen_ids.add(ds.ref)
                        dataset_ids.append(ds.ref)

                page += 1
                logger.debug(
                    "Kaggle dataset_list: tabular/%s, обработана страница %s, "
                    "уникальных ID=%s",
                    file_type,
                    page - 1,
                    len(dataset_ids),
                )

        logger.info(
            "Всего получено %s уникальных ID датасетов из Kaggle (tabular и csv/json)",
            len(dataset_ids),
        )
        return dataset_ids
    
    async def get_metadata(
        self, 
        external_id: str
    ) -> Dict[str, Any]:
        """Получает метаданные датасета"""
        logger.debug(f"Получение метаданных датасета: {external_id}")
        
        try:
            def _fetch_metadata_json() -> Dict[str, Any]:
                with tempfile.TemporaryDirectory(prefix="kaggle_meta_") as tmp:
                    meta_file = self._api.dataset_metadata(external_id, tmp)
                    with open(meta_file, "r", encoding="utf-8") as f:
                        loaded = json.load(f)
                if not isinstance(loaded, dict):
                    return {}
                return _merge_kaggle_metadata_loaded(loaded)

            raw: Dict[str, Any] = await self._run_kaggle_sync_with_429_retry(
                f"dataset_metadata({external_id})",
                _fetch_metadata_json,
            )

            last_updated = _parse_last_updated_from_metadata(raw)
            _hint_keys = (
                "last_updated",
                "lastUpdated",
                "update_time",
                "updateTime",
            )
            _raw_has_update_hint = any(raw.get(k) is not None for k in _hint_keys)
            if _raw_has_update_hint and last_updated is None:
                logger.warning(
                    "Не удалось распарсить дату обновления для %s: %s",
                    external_id,
                    next((raw.get(k) for k in _hint_keys if raw.get(k) is not None), None),
                )

            if last_updated is None:
                last_updated = await self._run_kaggle_sync_with_429_retry(
                    f"dataset_list_lastUpdated({external_id})",
                    lambda: self._last_updated_from_dataset_list_sync(external_id),
                )
            
            repository_url = f"https://www.kaggle.com/datasets/{external_id}"
            
            title = (
                raw.get("title")
                or raw.get("name")
                or external_id.split("/")[-1]
            )
            if not isinstance(title, str):
                title = str(title)

            description = raw.get("description") or ""
            if not isinstance(description, str):
                description = str(description)
            max_desc_length = 10000
            if description and len(description) > max_desc_length:
                description = description[:max_desc_length - 3] + '...'
            
            return {
                'title': title[:500],
                'description': description,
                'keywords': _keywords_from_kaggle_metadata(raw),
                'lastUpdated': last_updated,
                'repository_url': repository_url,
                'external_id': external_id
            }
            
        except Exception as e:
            if _is_kaggle_api_http_404(e):
                raise DatasetNotFoundError(
                    external_id=external_id,
                    source="kaggle",
                ) from e
            logger.warning(
                "Kaggle dataset_metadata(%s): %s",
                external_id,
                e,
                exc_info=True,
            )
            raise SourceUnavailableError(
                source="kaggle",
                reason=f"Ошибка получения метаданных: {e}",
            ) from e

    async def get_files_list(
        self, 
        external_id: str
    ) -> List[Dict[str, Any]]:
        """Получает полный список файлов датасета с их размерами"""
        logger.debug(f"Получение списка файлов датасета: {external_id}")
        
        try:
            def _list_all() -> List[Dict[str, Any]]:
                acc: List[Dict[str, Any]] = []
                token: Optional[str] = None
                page_size = int(get_settings().AGGREGATION_BATCH_SIZE)
                while True:
                    resp = self._api.dataset_list_files(
                        external_id,
                        page_token=token,
                        page_size=page_size,
                    )
                    if resp is None:
                        break
                    err = getattr(resp, "error_message", None) or getattr(
                        resp, "errorMessage", None
                    )
                    if err:
                        raise RuntimeError(str(err))
                    batch = getattr(resp, "files", None) or []
                    for f in batch:
                        name = getattr(f, "name", None) or getattr(
                            f, "file_name", None
                        ) or ""
                        if not name:
                            continue
                        sz = (
                            getattr(f, "total_bytes", None)
                            or getattr(f, "sizeBytes", None)
                            or getattr(f, "size", None)
                            or 0
                        )
                        try:
                            sz_i = int(sz)
                        except (TypeError, ValueError):
                            sz_i = 0
                        acc.append({"file_name": name, "size_bytes": sz_i})
                    token = getattr(resp, "next_page_token", None) or getattr(
                        resp, "nextPageToken", None
                    )
                    if not token:
                        break
                return acc

            result = await self._run_kaggle_sync_with_429_retry(
                f"dataset_list_files({external_id})",
                _list_all,
            )
            
            logger.debug(f"Получено {len(result)} файлов для датасета {external_id}")
            return result
            
        except Exception as e:
            if _is_kaggle_api_http_404(e):
                raise DatasetNotFoundError(
                    external_id=external_id,
                    source="kaggle",
                ) from e
            logger.warning(
                "Kaggle dataset_list_files(%s): %s",
                external_id,
                e,
                exc_info=True,
            )
            raise SourceUnavailableError(
                source="kaggle",
                reason=f"Ошибка получения списка файлов: {e}",
            ) from e

    async def download_dataset(
        self, 
        external_id: str, 
        target_dir: str
    ) -> str:
        """Скачивает датасет во временную директорию"""
        logger.debug(f"Скачивание датасета: {external_id} в {target_dir}")
        
        try:
            Path(target_dir).mkdir(parents=True, exist_ok=True)
            
            zip_path = _kaggle_dataset_zip_path(self._api, external_id, target_dir)

            def _do_download() -> None:
                self._api.dataset_download_files(
                    dataset=external_id,
                    path=target_dir,
                    unzip=False,
                    quiet=True,
                )

            await self._run_kaggle_sync_with_429_retry(
                f"dataset_download_files({external_id})",
                _do_download,
            )

            if not os.path.isfile(zip_path):
                raise SourceUnavailableError(
                    source="kaggle",
                    reason=(
                        f"После скачивания не найден ожидаемый архив: {zip_path}"
                    ),
                )
            return zip_path
                
        except Exception as e:
            if _is_kaggle_api_http_404(e):
                raise DatasetNotFoundError(
                    external_id=external_id,
                    source="kaggle",
                ) from e
            logger.warning(
                "Kaggle dataset_download_files(%s): %s",
                external_id,
                e,
                exc_info=True,
            )
            raise SourceUnavailableError(
                source="kaggle",
                reason=f"Ошибка скачивания датасета: {e}",
            ) from e

    async def check_dataset_exists(
        self, 
        external_id: str
    ) -> bool:
        """Проверяет существование датасета в источнике"""
        try:
            await self.get_metadata(external_id)
            return True
        except DatasetNotFoundError:
            return False
        except SourceUnavailableError:
            logger.warning(
                f"Не удалось проверить существование датасета {external_id}: "
                f"источник временно недоступен"
            )
            return True
    
    def get_repository_url(
        self, 
        external_id: str
    ) -> str:
        """Формирует URL страницы датасета в репозитории"""
        return f"https://www.kaggle.com/datasets/{external_id}"
    
    def get_download_url(
        self, 
        external_id: str
    ) -> Optional[str]:
        """Формирует URL для скачивания датасета"""
        return f"https://www.kaggle.com/api/v1/datasets/download/{external_id}"
    
    
    async def validate_dataset_files(
        self, 
        files_list: List[Dict[str, Any]],
        external_id: str = 'unknown'
    ) -> Dict[str, Any]:
        """Валидирует список файлов датасета перед скачиванием"""
        logger.debug(f"Валидация файлов датасета {external_id} ({len(files_list)} файлов)")
        
        has_data_file = False
        total_size_kb = 0.0
        dataset_format = None
        
        for file in files_list:
            file_name = file.get('file_name', '')
            size_bytes = int(file.get('size_bytes', 0) or 0)
            size_kb = round(size_bytes / 1024, 2)

            if size_bytes <= 0:
                raise InvalidFileError(
                    f"Файл '{file_name}' имеет нулевой размер; датасет отклонён",
                    file_name=file_name or None,
                )
            
            if size_kb > self._max_file_size_kb:
                raise DatasetTooLargeError(
                    file_name=file_name,
                    file_size_kb=size_kb,
                    max_size_kb=float(self._max_file_size_kb),
                )
            
            total_size_kb += size_kb
            
            if self.is_data_file(file_name):
                has_data_file = True
                if file_name.lower().endswith(('.json', '.jsonl')) and dataset_format is None:
                    dataset_format = 'json'
                elif file_name.lower().endswith('.csv'):
                    dataset_format = dataset_format or 'csv'
        
        if not has_data_file:
            raise NoValidFilesError(
                external_id=external_id,
                source='kaggle'
            )
        
        return {
            'valid': True,
            'format': dataset_format or 'json',
            'total_size_kb': round(total_size_kb, 2),
            'error': None
        }
    
    async def extract_and_hash_files(
        self,
        download_path: str,
        files_list: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """Распаковывает ZIP-архив и формирует записи для таблицы files"""
        logger.debug(
            "Распаковка и хеширование файлов из %s (в архиве; метаданных API: %s)",
            download_path,
            len(files_list),
        )
        
        result: List[Dict[str, Any]] = []
        
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_dir_path = Path(temp_dir)
            with zipfile.ZipFile(download_path, 'r') as zf:
                zf.extractall(temp_dir)
            
            discovered = sorted(
                p for p in temp_dir_path.rglob('*') if p.is_file()
            )
            for file_path in discovered:
                try:
                    rel_name = file_path.relative_to(temp_dir_path).as_posix()
                except ValueError:
                    continue
                
                is_data = self.is_data_file(rel_name)
                size_kb = round(file_path.stat().st_size / 1024, 2)
                file_hash = None
                if is_data:
                    file_hash = await self.compute_file_hash(file_path)
                    logger.debug(
                        "Вычислен хеш для файла %s: %s...",
                        rel_name,
                        file_hash[:16],
                    )
                
                result.append({
                    'file_name': rel_name,
                    'file_size_kb': size_kb,
                    'is_data': is_data,
                    'file_hash': file_hash,
                })
        
        hashed_count = sum(1 for f in result if f['file_hash'])
        logger.debug(
            "Обработано %s файлов из архива, хеши для %s data-файлов",
            len(result),
            hashed_count,
        )
        return result