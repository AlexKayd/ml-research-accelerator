import asyncio
import hashlib
import logging
import shutil
import tempfile
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Optional
import aiohttp
from app.core.config import get_settings
from app.core.minio import get_minio_client
from app.domain.entities import FileInfo, DatasetInfo, Report
from app.domain.exceptions import (
    DatasetArchiveDownloadError,
    FileNotFoundInArchiveError,
    ReportGenerationError,
    StorageError,
)
from app.domain.interfaces import IReportStorage
from app.schemas import GeneratedReportArtifact
import pandas as pd
from ydata_profiling import ProfileReport

logger = logging.getLogger(__name__)


def _sha256_hex(data: bytes) -> str:
    """Возвращает SHA-256 содержимого в нижнем регистре"""
    return hashlib.sha256(data).hexdigest().lower()


def _normalize_path(p: str) -> str:
    """Нормализует путь для сравнения путей в архиве"""
    return (p or "").replace("\\", "/")


class ReportGenerator:

    def __init__(self, storage: Optional[IReportStorage] = None) -> None:
        self._settings = get_settings()
        self._storage = storage if storage is not None else get_minio_client()

    async def generate(
        self,
        report: Report,
        file_info: FileInfo,
        dataset_info: DatasetInfo,
    ) -> GeneratedReportArtifact:
        """Скачивает архив, строит профиль, загружает HTML в MinIO и возвращает артефакт"""
        if not dataset_info.download_url:
            raise DatasetArchiveDownloadError(
                dataset_id=file_info.dataset_id,
                download_url="",
                reason="у датасета отсутствует download_url",
            )

        temp_root = Path(tempfile.mkdtemp(prefix=f"eda_{report.report_id or 'new'}_"))
        zip_path = temp_root / "dataset.zip"
        extract_dir = temp_root / "extract"
        extract_dir.mkdir(parents=True, exist_ok=True)

        try:
            logger.info(
                "EDA: старт report_id=%s file_id=%s dataset_id=%s — скачивание ZIP",
                report.report_id,
                file_info.file_id,
                file_info.dataset_id,
            )
            await self._download_zip(dataset_info.download_url, zip_path)
            logger.info("EDA: распаковка ZIP report_id=%s", report.report_id)
            await asyncio.to_thread(self._extract_zip, zip_path, extract_dir)

            target_path = await asyncio.to_thread(
                self._find_file_in_extracted_dir,
                extract_dir,
                file_info.file_name,
            )
            if target_path is None:
                raise FileNotFoundInArchiveError(
                    dataset_id=file_info.dataset_id,
                    file_name=file_info.file_name,
                )

            raw_bytes = await asyncio.to_thread(target_path.read_bytes)
            input_hash = _sha256_hex(raw_bytes)

            html = await self._build_profile_html(target_path)

            object_key = Report.build_default_object_key(file_info.file_id)
            await self._storage.upload_report_html(object_key, html)

            return GeneratedReportArtifact(
                html=html,
                input_file_hash=input_hash,
                bucket_name=self._storage.reports_bucket,
                object_key=object_key,
            )

        except (DatasetArchiveDownloadError, FileNotFoundInArchiveError, StorageError):
            raise
        except Exception as e:
            raise ReportGenerationError(
                report_id=int(report.report_id or 0),
                reason=str(e),
            )
        finally:
            try:
                await asyncio.to_thread(shutil.rmtree, temp_root, True)
            except Exception:
                logger.debug("Не удалось удалить временную директорию %s", temp_root, exc_info=True)

    async def compute_input_file_hash_from_dataset_zip(
        self,
        file_info: FileInfo,
        dataset_info: DatasetInfo,
    ) -> str:
        """Для проверки свежести: скачивает архив, находит файл, возвращает SHA-256"""
        if not dataset_info.download_url:
            raise DatasetArchiveDownloadError(
                dataset_id=file_info.dataset_id,
                download_url="",
                reason="у датасета отсутствует download_url",
            )

        temp_root = Path(tempfile.mkdtemp(prefix=f"eda_hash_{file_info.file_id}_"))
        zip_path = temp_root / "dataset.zip"
        extract_dir = temp_root / "extract"
        extract_dir.mkdir(parents=True, exist_ok=True)

        try:
            await self._download_zip(dataset_info.download_url, zip_path)
            await asyncio.to_thread(self._extract_zip, zip_path, extract_dir)
            target_path = await asyncio.to_thread(
                self._find_file_in_extracted_dir,
                extract_dir,
                file_info.file_name,
            )
            if target_path is None:
                raise FileNotFoundInArchiveError(
                    dataset_id=file_info.dataset_id,
                    file_name=file_info.file_name,
                )
            raw_bytes = await asyncio.to_thread(target_path.read_bytes)
            return _sha256_hex(raw_bytes)
        finally:
            try:
                await asyncio.to_thread(shutil.rmtree, temp_root, True)
            except Exception:
                pass

    async def _download_zip(self, url: str, target_path: Path) -> None:
        """Скачивает ZIP по URL"""
        timeout_seconds = float(getattr(self._settings, 'HTTP_CLIENT_TIMEOUT_SECONDS', 120.0))
        max_retries = int(getattr(self._settings, 'HTTP_CLIENT_MAX_RETRIES', 3))
        base_delay = float(getattr(self._settings, 'HTTP_CLIENT_RETRY_DELAY_SECONDS', 1.0))
        timeout = aiohttp.ClientTimeout(total=timeout_seconds)

        last_error: Optional[Exception] = None
        for attempt in range(max_retries + 1):
            try:
                if attempt > 0:
                    logger.warning("EDA: повтор скачивания ZIP попытка %s/%s", attempt + 1, max_retries + 1)
                async with aiohttp.ClientSession(timeout=timeout) as session:
                    async with session.get(url) as resp:
                        if resp.status >= 400:
                            raise RuntimeError(f"HTTP {resp.status}")
                        data = await resp.read()
                        await asyncio.to_thread(target_path.write_bytes, data)
                        logger.info(
                            "EDA: ZIP скачан, bytes=%s",
                            len(data),
                        )
                        return
            except Exception as e:
                last_error = e
                if attempt >= max_retries:
                    break
                delay = base_delay * (2**attempt)
                await asyncio.sleep(delay)

        raise DatasetArchiveDownloadError(
            dataset_id=0,
            download_url=url,
            reason=f"не удалось скачать ZIP после {max_retries + 1} попыток: {last_error}",
        )

    def _extract_zip(self, zip_path: Path, extract_dir: Path) -> None:
        """Распаковывает ZIP"""
        if not zip_path.exists():
            raise RuntimeError(f"ZIP файл не найден: {zip_path}")
        with zipfile.ZipFile(zip_path, "r") as zf:
            zf.extractall(extract_dir)

    def _find_file_in_extracted_dir(self, extract_dir: Path, want_name: str) -> Optional[Path]:
        """Ищет файл в дереве"""
        want = _normalize_path(want_name)
        if not want:
            return None

        candidate = extract_dir / Path(want)
        if candidate.exists() and candidate.is_file():
            return candidate

        want_norm = want.lower()
        for p in extract_dir.rglob("*"):
            if not p.is_file():
                continue
            rel = _normalize_path(str(p.relative_to(extract_dir))).lower()
            if rel == want_norm:
                return p

        base = want.rsplit("/", 1)[-1].lower()
        matches = []
        for p in extract_dir.rglob("*"):
            if p.is_file() and p.name.lower() == base:
                matches.append(p)

        if len(matches) == 1:
            return matches[0]
        if len(matches) > 1:
            logger.warning(
                "Найдено несколько файлов с basename=%r; нужен точный путь files.file_name",
                base,
            )
        return None

    async def _build_profile_html(self, file_path: Path) -> str:
        """Генерация HTML отчёта"""
        start = datetime.now()
        logger.info("Генерация EDA отчёта: file=%s", file_path.name)

        def _sync_build() -> str:

            df = pd.read_csv(file_path) if file_path.suffix.lower() == ".csv" else pd.read_json(file_path)
            profile = ProfileReport(
                df,
                minimal=True,
                title=f"EDA отчёт: {file_path.name}",
            )
            return profile.to_html()

        html = await asyncio.to_thread(_sync_build)
        dur = (datetime.now() - start).total_seconds()
        logger.info("EDA отчёт сгенерирован за %.2f сек", dur)
        return html