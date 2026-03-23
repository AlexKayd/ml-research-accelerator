import asyncio
import logging
import re
import tempfile
import urllib.parse
import zipfile
import urllib.request
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import aiohttp
from ucimlrepo import fetch_ucirepo
from bs4 import BeautifulSoup
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


UCI_BASE_URL = "https://archive.ics.uci.edu"
UCI_API_DATASETS_LIST_URL = f"{UCI_BASE_URL}/api/datasets/list"


def _slug_from_repository_url(repo_url: str) -> Optional[str]:
    try:
        p = urllib.parse.urlparse(repo_url)
        parts = p.path.strip("/").split("/")

        if len(parts) >= 2 and parts[-2] == "dataset":
            return parts[-1]
    except Exception:
        return None
    return None


def _select_best_zip_url(html: str, page_url: str, external_id: str) -> Optional[str]:
    """Выбирает URL ZIP на странице датасета"""
    soup = BeautifulSoup(html, "html.parser")
    candidates: List[str] = []

    for link in soup.find_all("a", href=True):
        href = str(link["href"]).strip()

        if ".zip" not in href.lower():
            continue
        abs_u = urllib.parse.urljoin(page_url, href)
        low = abs_u.lower()

        if not (low.endswith(".zip") or ".zip?" in low):
            continue
        candidates.append(abs_u.split("?")[0])

    if not candidates:
        return None
    dedup = list(dict.fromkeys(candidates))
    needle = f"/static/public/{external_id}/"

    for c in dedup:
        path = urllib.parse.urlparse(c).path.replace("\\", "/")
        if needle in path:
            return c

    for c in dedup:
        if "/static/public/" in urllib.parse.urlparse(c).path:
            return c
    return dedup[0]


def _fallback_static_zip_url(external_id: str, repo_url: str) -> Optional[str]:
    slug = _slug_from_repository_url(repo_url)

    if not slug or slug == str(external_id):
        return None
    return f"{UCI_BASE_URL}/static/public/{external_id}/{slug}.zip"


def _http_get_text_sync(url: str, timeout: Optional[float] = None) -> str:
    """Загрузка HTML"""
    if timeout is None:
        timeout = float(get_settings().HTTP_CLIENT_TIMEOUT_SECONDS)
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "ml-research-accelerator/1.0 (UCI aggregation)"},
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read().decode("utf-8", errors="replace")


def _parse_size_kb(size_str: str) -> float:
    """Парсит строку размера в килобайты"""
    if not size_str:
        return 0.0
    
    u = size_str.strip().upper().replace(',', '')
    
    match = re.match(r"([\d.]+)", u)
    if not match:
        return 0.0
    
    num = float(match.group(1))
    
    if "GB" in u:
        return num * 1024 * 1024
    elif "MB" in u:
        return num * 1024
    elif "KB" in u:
        return num
    elif "BYTE" in u:
        return num / 1024
    else:
        return num / 1024


def _normalize_archive_relative_path(name: str) -> str:
    """Базовый относительный путь внутри распакованного архива / каталога"""
    if not name:
        return ""
    s = str(name).replace("\\", "/").strip()

    while s.startswith("./"):
        s = s[2:]
    s = s.lstrip("/")
    parts: List[str] = []

    for p in s.split("/"):
        if p in ("", "."):
            continue
        if p == "..":
            if parts:
                parts.pop()
        else:
            parts.append(p)
    return "/".join(parts)


def _resolve_extracted_file_path(
    base_path: Path,
    logical_name: str,
    size_bytes_hint: Optional[int] = None,
) -> Optional[Path]:
    """Находит файл после распаковки ZIP"""
    key = _normalize_archive_relative_path(logical_name)
    if not key:
        return None

    direct = base_path.joinpath(*key.split("/"))
    if direct.is_file():
        return direct.resolve()

    try:
        base_res = base_path.resolve()
    except OSError:
        base_res = base_path

    candidates: List[Path] = []
    for fp in base_path.rglob("*"):
        if not fp.is_file():
            continue
        try:
            rel = fp.resolve().relative_to(base_res)
        except ValueError:
            continue
        r = rel.as_posix()
        if r == key or r.endswith("/" + key):
            candidates.append(fp)

    if len(candidates) == 1:
        return candidates[0]

    if len(candidates) > 1:
        if size_bytes_hint is not None:
            for fp in candidates:
                try:
                    if fp.stat().st_size == size_bytes_hint:
                        return fp
                except OSError:
                    continue
        logger.warning(
            "Несколько путей для %r в %s (кандидатов: %s); подсказка размера: %s",
            logical_name,
            base_path,
            len(candidates),
            size_bytes_hint,
        )
        return None

    basename = Path(key).name
    name_hits = [p for p in base_path.rglob(basename) if p.is_file() and p.name == basename]

    if len(name_hits) == 1:
        return name_hits[0]

    if len(name_hits) > 1:
        if size_bytes_hint is not None:
            for fp in name_hits:
                try:
                    if fp.stat().st_size == size_bytes_hint:
                        return fp
                except OSError:
                    continue
        logger.warning(
            "Несколько файлов с именем %r в %s; не удалось однозначно сопоставить с %r",
            basename,
            base_path,
            logical_name,
        )
        return None

    logger.warning(
        "Файл %r не найден под %s после распаковки (нормализованный ключ: %r)",
        logical_name,
        base_path,
        key,
    )
    return None


def _parse_uci_date(date_str: Optional[str]) -> Optional[datetime]:
    """Парсит строку даты из метаданных UCI"""
    if not date_str:
        return None
    
    date_str = date_str.strip()
    
    formats = [
        ("%a %b %d %Y", 15),
        ("%Y-%m-%d", 10),
        ("%m/%d/%Y", 10),
    ]
    
    for fmt, max_len in formats:
        try:
            return datetime.strptime(date_str[:max_len], fmt)
        except ValueError:
            continue
    
    return None


def _fetch_ucirepo_sync(external_id: str) -> Any:
    return fetch_ucirepo(id=int(external_id))


def _is_uci_not_importable_error(exc: BaseException) -> bool:
    """True, если ucimlrepo отклоняет датасет: есть на сайте, но нет в Python-импорте"""
    return "not available for import" in str(exc).lower()


def _parse_uci_keyword_tags_from_html(soup: BeautifulSoup) -> List[str]:
    """Теги из ссылок на странице датасета"""
    tags: List[str] = []
    seen: set[str] = set()

    for a in soup.find_all("a", href=True):
        href = str(a.get("href", ""))

        if "Keywords=" not in href and "keywords=" not in href.lower():
            continue
        try:
            q = urllib.parse.parse_qs(urllib.parse.urlparse(href).query)
            for key in ("Keywords", "keywords"):
                vals = q.get(key)
                if not vals or not vals[0]:
                    continue
                w = urllib.parse.unquote_plus(str(vals[0])).strip()
                low = w.lower()
                if w and low not in seen:
                    seen.add(low)
                    tags.append(w)

        except Exception:
            continue
    return tags[:50]


def _build_uci_metadata_from_dataset_page(html: str, external_id: str) -> Dict[str, Any]:
    """Метаданные со страницы, если fetch_ucirepo недоступен"""
    repo_url = f"{UCI_BASE_URL}/dataset/{external_id}"
    soup = BeautifulSoup(html, "html.parser")

    title: Optional[str] = None
    h1 = soup.find("h1")

    if h1:
        title = h1.get_text(strip=True)
        for suf in (" - UCI Machine Learning Repository",):
            if title.endswith(suf):
                title = title[: -len(suf)].strip()
    if not title:
        og = soup.find("meta", property="og:title")
        if og and og.get("content"):
            title = str(og["content"]).strip()
    if not title:
        title = f"Dataset {external_id}"

    description = ""
    md = soup.find("meta", attrs={"name": "description"})

    if md and md.get("content"):
        description = str(md["content"]).strip()
    if not description:
        ogd = soup.find("meta", property="og:description")
        if ogd and ogd.get("content"):
            description = str(ogd["content"]).strip()
    if not description and soup.body:
        chunks: List[str] = []
        for p in soup.body.find_all("p", limit=16):
            t = p.get_text(strip=True)
            if len(t) < 40:
                continue
            tl = t.lower()
            if "cookie" in tl and "privacy" in tl:
                continue
            if tl.startswith("accept ") and "policy" in tl:
                continue
            chunks.append(t)
            if len(chunks) >= 6:
                break
        description = "\n\n".join(chunks)

    max_desc_length = 10000
    if description and len(description) > max_desc_length:
        description = description[: max_desc_length - 3] + "..."

    zip_url = _select_best_zip_url(html, repo_url, external_id)
    if not zip_url:
        zip_url = _fallback_static_zip_url(external_id, repo_url)

    tags = _parse_uci_keyword_tags_from_html(soup)

    return {
        "external_id": external_id,
        "title": title,
        "description": description,
        "repository_url": repo_url,
        "download_url": zip_url,
        "last_modified": None,
        "tags": tags,
        "uci_metadata": {
            "source": "html_fallback",
            "name": title[:500],
        },
    }


class UCIClient(BaseClient):
    
    def __init__(
        self,
        timeout: Optional[float] = None,
        max_retries: Optional[int] = None,
        rate_limit_delay: Optional[float] = None,
        *,
        catalog_filter_python: bool = True,
    ) -> None:
        super().__init__(
            source_name='uci',
            timeout=timeout,
            max_retries=max_retries,
            rate_limit_delay=rate_limit_delay
        )
        
        self._all_ids: Optional[List[str]] = None
        self._catalog_filter_python = catalog_filter_python
        self._max_file_size_kb = int(get_settings().MAX_FILE_SIZE_KB)

        logger.debug("Инициализирован клиент UCI Repository")

    async def _resolve_zip_download_url(self, external_id: str, repo_url: str) -> Optional[str]:
        """Прямая ссылка на ZIP"""
        try:
            html = await self._get_text(repo_url, external_id)
            z = _select_best_zip_url(html, repo_url, external_id)
            if z:
                return z
        except Exception as e:
            logger.debug("ZIP со страницы UCI не извлечён (%s): %s", external_id, e)
        return _fallback_static_zip_url(external_id, repo_url)

    async def _fetch_uci_datasets_list_from_api(
        self,
        *,
        filter_python: bool = True,
    ) -> List[Dict[str, Any]]:
        """Загружает каталог датасетов с JSON API UCI"""
        query: Dict[str, str] = {}
        if filter_python:
            query["filter"] = "python"
        url = (
            UCI_API_DATASETS_LIST_URL
            + ("?" + urllib.parse.urlencode(query) if query else "")
        )

        session = await self._get_session()

        retry_delays_sec = (0.0, 2.0, 5.0)
        last_client_error: Optional[BaseException] = None
        payload: Any = None

        for attempt, delay in enumerate(retry_delays_sec):
            if delay > 0:
                await asyncio.sleep(delay)
            await self._wait_rate_limit()
            try:
                async with session.get(url) as resp:
                    if resp.status == 404:
                        raise SourceUnavailableError(
                            source="uci",
                            reason="UCI list API вернул 404",
                        )
                    resp.raise_for_status()
                    payload = await resp.json(content_type=None)
                last_client_error = None
                break
            except SourceUnavailableError:
                raise
            except aiohttp.ClientError as e:
                last_client_error = e
                logger.warning(
                    "UCI list API: сеть, попытка %s/%s: %s",
                    attempt + 1,
                    len(retry_delays_sec),
                    e,
                )
                continue

        if last_client_error is not None:
            raise SourceUnavailableError(
                source="uci",
                reason=f"Ошибка HTTP при запросе списка датасетов после {len(retry_delays_sec)} попыток: {last_client_error}",
            ) from last_client_error

        if not isinstance(payload, dict):
            raise SourceUnavailableError(
                source="uci",
                reason="UCI list API: ответ не является JSON-объектом",
            )

        if payload.get("status") != 200:
            msg = payload.get("message", "неизвестная ошибка API")
            raise SourceUnavailableError(
                source="uci",
                reason=f"UCI list API status={payload.get('status')}: {msg}",
            )

        data = payload.get("data")
        if data is None:
            return []
        if not isinstance(data, list):
            raise SourceUnavailableError(
                source="uci",
                reason="UCI list API: поле data не является списком",
            )
        return data

    async def _load_dataset_ids(self) -> List[str]:
        """Загружает список всех доступных датасетов из UCI"""
        if self._all_ids is not None:
            return self._all_ids

        logger.debug("Загрузка списка датасетов UCI через %s", UCI_API_DATASETS_LIST_URL)

        try:
            datasets = await self._fetch_uci_datasets_list_from_api(
                filter_python=self._catalog_filter_python
            )
            self._all_ids = sorted(
                {str(d["id"]) for d in datasets if d.get("id") is not None}
            )

            mode = (
                "filter=python (совместимо с ucimlrepo)"
                if self._catalog_filter_python
                else "полный каталог API (без filter=python)"
            )
            logger.info(
                "Загружено %s датасетов из UCI (%s)",
                len(self._all_ids),
                mode,
            )
            return self._all_ids

        except SourceUnavailableError:
            raise
        except Exception as e:
            raise SourceUnavailableError(
                source='uci',
                reason=f"Ошибка загрузки списка датасетов: {e}"
            ) from e
    
    async def list_dataset_ids(
        self, 
        batch_size: Optional[int] = None
    ) -> List[str]:
        """Получает список внешних ID всех доступных датасетов"""
        logger.debug(f"Получение списка датасетов UCI")
        all_ids = await self._load_dataset_ids()
        return all_ids
    
    async def get_metadata(
        self, 
        external_id: str
    ) -> Dict[str, Any]:
        """Получает метаданные датасета"""
        logger.debug(f"Получение метаданных датасета: {external_id}")
        
        try:
            repo = await asyncio.to_thread(_fetch_ucirepo_sync, external_id)
            
        except Exception as e:
            if _is_uci_not_importable_error(e):
                logger.info(
                    "UCI %s: нет импорта через ucimlrepo, метаданные со страницы HTML",
                    external_id,
                )
                try:
                    repo_url = f"{UCI_BASE_URL}/dataset/{external_id}"
                    html = await self._get_text(repo_url, external_id)
                    return _build_uci_metadata_from_dataset_page(html, external_id)
                except DatasetNotFoundError:
                    raise
                except Exception as html_e:
                    raise SourceUnavailableError(
                        source="uci",
                        reason=(
                            f"Ошибка получения метаданных: {e}; "
                            f"HTML-fallback: {html_e}"
                        ),
                    ) from html_e

            error_msg = str(e).lower()
            if 'not found' in error_msg or '404' in error_msg:
                raise DatasetNotFoundError(
                    external_id=external_id,
                    source='uci'
                ) from e
            raise SourceUnavailableError(
                source='uci',
                reason=f"Ошибка получения метаданных: {e}"
            ) from e
        
        metadata = dict(repo.metadata)
        
        repo_url = metadata.get('repository_url') or f"{UCI_BASE_URL}/dataset/{external_id}"
        
        last_updated = metadata.get("last_updated")
        if isinstance(last_updated, datetime):
            last_modified = (
                last_updated.replace(tzinfo=None)
                if last_updated.tzinfo
                else last_updated
            )
        elif isinstance(last_updated, str):
            last_modified = _parse_uci_date(last_updated)
        else:
            last_modified = None
        
        abstract = metadata.get('abstract') or ''
        additional_info = metadata.get('additional_info') or {}
        summary = additional_info.get('summary') or ''
        
        description = abstract
        if summary:
            description = f"{abstract}\n\n{summary}".strip()
        
        max_desc_length = 10000
        if description and len(description) > max_desc_length:
            description = description[:max_desc_length - 3] + '...'
        
        tags = self._extract_tags_from_metadata(metadata)

        zip_url: Optional[str] = None
        try:
            zip_url = await self._resolve_zip_download_url(external_id, repo_url)
        except Exception as e:
            logger.warning(
                "Не удалось определить ZIP download_url для датасета %s: %s",
                external_id,
                e,
            )

        return {
            'external_id': external_id,
            'title': (metadata.get('name') or f"Dataset {external_id}"),
            'description': description,
            'repository_url': repo_url,
            'download_url': zip_url,
            'last_modified': last_modified,
            'tags': tags,
            'uci_metadata': metadata
        }
    
    def _extract_tags_from_metadata(self, metadata: Dict[str, Any]) -> List[str]:
        """Извлекает теги из различных полей метаданных UCI"""
        tags = []
        tag_fields = ['area', 'characteristics', 'tasks', 'subject_area']
        
        for field in tag_fields:
            value = metadata.get(field)
            if isinstance(value, list):
                tags.extend(str(x) for x in value if x)
            elif isinstance(value, str) and value:
                tags.append(value)
        
        unique_tags = list(dict.fromkeys(tags))
        return unique_tags[:50]
    
    async def _get_text(self, url: str, external_id: str = 'unknown') -> str:
        """Выполняет GET-запрос и возвращает текст ответа"""
        session = await self._get_session()
        await self._wait_rate_limit()
        
        async with session.get(url) as resp:
            if resp.status == 404:
                raise DatasetNotFoundError(
                    external_id=external_id,
                    source='uci'
                )
            resp.raise_for_status()
            return await resp.text()
    
    async def _download_bytes(self, url: str, external_id: str) -> bytes:
        """Скачивает содержимое по URL как байты"""
        session = await self._get_session()
        last_error: Optional[Exception] = None
        
        for attempt, delay in enumerate([0, 2, 6]):
            if delay > 0:
                await asyncio.sleep(delay)
            
            try:
                await self._wait_rate_limit()
                
                async with session.get(url) as resp:
                    if resp.status == 404:
                        raise DatasetNotFoundError(
                            external_id=external_id,
                            source='uci'
                        )
                    resp.raise_for_status()
                    return await resp.read()
                    
            except Exception as e:
                last_error = e
                logger.warning(
                    f"Попытка {attempt + 1} скачивания {external_id} не удалась: {e}"
                )
                if attempt < 2:
                    continue
                else:
                    break
        
        raise SourceUnavailableError(
            source='uci',
            reason=f"Не удалось скачать файл после 3 попыток: {last_error}"
        )
    
    def _parse_files_table(self, html: str) -> List[Tuple[str, float]]:
        """Парсит таблицу файлов из HTML страницы датасета """
        soup = BeautifulSoup(html, 'html.parser')
        
        for table in soup.find_all('table'):
            rows = table.find_all('tr')
            if len(rows) < 2:
                continue
            
            headers = [
                cell.get_text(strip=True).lower()
                for cell in rows[0].find_all(['th', 'td'])
            ]
            
            if 'file' in headers and 'size' in headers:
                file_idx = headers.index('file')
                size_idx = headers.index('size')
                
                files = []
                for row in rows[1:]:
                    cells = row.find_all(['td', 'th'])
                    if len(cells) <= max(file_idx, size_idx):
                        continue
                    
                    file_name = cells[file_idx].get_text(strip=True)
                    if not file_name or file_name.lower() == 'file':
                        continue
                    
                    size_str = cells[size_idx].get_text(strip=True)
                    size_kb = _parse_size_kb(size_str)
                    
                    files.append((file_name, size_kb))
                
                if files:
                    return files
        
        return []
    
    
    async def get_files_list(
        self, 
        external_id: str
    ) -> List[Dict[str, Any]]:
        """ Получает список всех файлов датасета с их размерами"""
        logger.debug(f"Получение списка файлов датасета: {external_id}")
        
        try:
            metadata = await self.get_metadata(external_id)
            repo_url = metadata['repository_url']
            
            html = await self._get_text(repo_url, external_id)
            file_rows = self._parse_files_table(html)
            
            result = []
            for file_name, size_kb in file_rows:
                size_bytes = int(size_kb * 1024)
                result.append({
                    'file_name': file_name,
                    'size_bytes': size_bytes
                })

            if file_rows and not any(
                self.is_data_file(fn) for fn, _ in file_rows
            ):
                names = [fn for fn, _ in file_rows[:12]]
                logger.debug(
                    "UCI %s: в таблице %s файлов, нет ни одного .csv/.json/.jsonl "
                    "Примеры имён: %s",
                    external_id,
                    len(file_rows),
                    names,
                )
            
            logger.debug(
                "Получено %s файлов (все строки таблицы) для датасета %s",
                len(result),
                external_id,
            )
            return result
            
        except (DatasetNotFoundError, SourceUnavailableError):
            raise
        except Exception as e:
            raise SourceUnavailableError(
                source='uci',
                reason=f"Ошибка получения списка файлов: {e}"
            ) from e
    
    async def download_dataset(
        self, 
        external_id: str, 
        target_dir: str
    ) -> str:
        """Скачивает датасет во временную директорию"""
        logger.debug(f"Скачивание датасета: {external_id} в {target_dir}")
        
        try:
            metadata = await self.get_metadata(external_id)
            repo_url = metadata['repository_url']
            zip_url = metadata.get('download_url')
            if not zip_url or '.zip' not in zip_url.lower():
                html = await self._get_text(repo_url, external_id)
                zip_url = _select_best_zip_url(html, repo_url, external_id)
                if not zip_url:
                    zip_url = _fallback_static_zip_url(external_id, repo_url)
            
            Path(target_dir).mkdir(parents=True, exist_ok=True)
            
            if zip_url:
                logger.debug(f"Скачивание архива: {zip_url}")
                zip_data = await self._download_bytes(zip_url, external_id)
                zip_path = Path(target_dir) / f"dataset_{external_id}.zip"
                zip_path.write_bytes(zip_data)
                return str(zip_path)
                
            else:
                files_list = await self.get_files_list(external_id)
                downloaded_paths = []
                
                for file_meta in files_list:
                    file_name = file_meta['file_name']
                    file_url = f"{repo_url}/{file_name}"
                    
                    try:
                        file_data = await self._download_bytes(file_url, external_id)
                        file_path = Path(target_dir) / file_name
                        file_path.parent.mkdir(parents=True, exist_ok=True)
                        file_path.write_bytes(file_data)
                        downloaded_paths.append(str(file_path))
                    except Exception as e:
                        logger.warning(f"Не удалось скачать файл {file_name}: {e}")
                        continue
                
                if downloaded_paths:
                    return downloaded_paths[0] if len(downloaded_paths) == 1 else target_dir
                else:
                    raise SourceUnavailableError(
                        source='uci',
                        reason=f"Не удалось скачать ни один файл для датасета {external_id}"
                    )
                    
        except (DatasetNotFoundError, SourceUnavailableError):
            raise
        except Exception as e:
            raise SourceUnavailableError(
                source='uci',
                reason=f"Ошибка скачивания датасета: {e}"
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
        except SourceUnavailableError as e:
            logger.warning(
                f"Не удалось проверить существование датасета {external_id}: {e}"
            )
            return True
    
    def get_repository_url(
        self, 
        external_id: str
    ) -> str:
        """Формирует URL страницы датасета в репозитории"""
        return f"{UCI_BASE_URL}/dataset/{external_id}"
    
    def get_download_url(
        self, 
        external_id: str
    ) -> Optional[str]:
        """Возвращает URL ZIP-архива"""
        repo_url = f"{UCI_BASE_URL}/dataset/{external_id}"
        try:
            repo = _fetch_ucirepo_sync(external_id)
            md = dict(repo.metadata)
            repo_url = md.get('repository_url') or repo_url

        except Exception as e:
            if not _is_uci_not_importable_error(e):
                logger.debug(
                    "get_download_url: не удалось получить ZIP для %s: %s",
                    external_id,
                    e,
                )
                return None
        try:
            html = _http_get_text_sync(repo_url)
            z = _select_best_zip_url(html, repo_url, external_id)
            if z:
                return z
            return _fallback_static_zip_url(external_id, repo_url)
        except Exception:
            try:
                return _fallback_static_zip_url(external_id, repo_url)
            except Exception:
                return None
    
    
    async def validate_dataset_files(
        self, 
        files_list: List[Dict[str, Any]],
        external_id: str
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
                lower = file_name.lower()
                if lower.endswith((".json", ".jsonl")):
                    dataset_format = dataset_format or "json"
                elif lower.endswith(".csv"):
                    dataset_format = dataset_format or "csv"
                
        
        if not has_data_file:
            raise NoValidFilesError(
                external_id=external_id,
                source='uci'
            )
        
        return {
            'valid': True,
            'format': dataset_format or 'json',
            'total_size_kb': round(total_size_kb, 2),
            'error': None
        }
    
    async def _process_single_file(
        self,
        file_name: str,
        base_path: Path,
        is_data: bool,
        size_bytes_hint: Optional[int] = None,
    ) -> Tuple[Optional[str], float]:
        """Обрабатывает один файл: вычисляет хеш если data-файл"""
        hint = size_bytes_hint if size_bytes_hint and size_bytes_hint > 0 else None
        file_path = _resolve_extracted_file_path(base_path, file_name, hint)

        if file_path is None or not file_path.is_file():
            logger.warning(
                "Файл %r не найден под %s (подсказка размера: %s)",
                file_name,
                base_path,
                hint,
            )
            return None, 0.0

        resolved_rel = None
        try:
            resolved_rel = file_path.resolve().relative_to(base_path.resolve()).as_posix()
        except ValueError:
            pass
        if resolved_rel and resolved_rel != _normalize_archive_relative_path(file_name):
            logger.debug(
                "Сопоставление UCI: логическое имя %r -> %s",
                file_name,
                resolved_rel,
            )

        actual_size_kb = round(file_path.stat().st_size / 1024, 2)

        file_hash = None
        if is_data:
            file_hash = await self.compute_file_hash(file_path)
            logger.debug(f"Вычислен хеш для файла {file_name}: {file_hash[:16]}...")

        return file_hash, actual_size_kb
    
    async def extract_and_hash_files(
        self, 
        download_path: str,
        files_list: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Распаковывает архив и вычисляет хеши"""
        logger.debug(f"Обработка файлов из {download_path}")
        
        result = []
        download_path_obj = Path(download_path)
        
        if download_path_obj.is_file() and download_path_obj.suffix.lower() == ".zip":
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_dir_path = Path(temp_dir)
                
                with zipfile.ZipFile(download_path, 'r') as zf:
                    zf.extractall(temp_dir)
                    
                    for file_meta in files_list:
                        file_name = file_meta.get('file_name', '')
                        size_bytes = file_meta.get('size_bytes', 0)
                        size_kb = round(size_bytes / 1024, 2)
                        
                        is_data = self.is_data_file(file_name)

                        file_hash, actual_size_kb = await self._process_single_file(
                            file_name=file_name,
                            base_path=temp_dir_path,
                            is_data=is_data,
                            size_bytes_hint=size_bytes,
                        )
                        
                        if actual_size_kb > 0:
                            size_kb = actual_size_kb
                        
                        result.append({
                            'file_name': file_name,
                            'file_size_kb': size_kb,
                            'is_data': is_data,
                            'file_hash': file_hash
                        })
                        
        elif download_path_obj.is_dir():
            for file_meta in files_list:
                file_name = file_meta.get('file_name', '')
                size_bytes = file_meta.get('size_bytes', 0)
                size_kb = round(size_bytes / 1024, 2)
                
                is_data = self.is_data_file(file_name)

                file_hash, actual_size_kb = await self._process_single_file(
                    file_name=file_name,
                    base_path=download_path_obj,
                    is_data=is_data,
                    size_bytes_hint=size_bytes,
                )
                
                if actual_size_kb > 0:
                    size_kb = actual_size_kb
                
                result.append({
                    'file_name': file_name,
                    'file_size_kb': size_kb,
                    'is_data': is_data,
                    'file_hash': file_hash
                })
        
        hashed_count = sum(1 for f in result if f['file_hash'])
        logger.debug(
            f"Обработано {len(result)} файлов, "
            f"хеши для {hashed_count} data-файлов"
        )
        return result