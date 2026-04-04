import asyncio
import io
import json
import logging
from typing import Optional
from app.core.config import settings
from app.domain.exceptions import StorageError
from app.domain.interfaces import IReportStorage
try:
    from minio import Minio
    from minio.error import S3Error
except Exception:
    Minio = None
    S3Error = None

logger = logging.getLogger(__name__)


class MinIOClient(IReportStorage):
    def __init__(self) -> None:
        if Minio is None:
            raise RuntimeError(
                "Пакет 'minio' не установлен"
            )
        self._client = Minio(
            endpoint=settings.MINIO_ENDPOINT,
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY,
            secure=settings.MINIO_SECURE,
        )
        self._reports_bucket = settings.MINIO_REPORTS_BUCKET
        self._anonymous_read_policy_applied = False
        logger.debug("Инициализирован MinIOClient endpoint=%s", settings.MINIO_ENDPOINT)

    @property
    def reports_bucket(self) -> str:
        return self._reports_bucket

    def _reports_bucket_anonymous_read_policy(self) -> str:
        resource = f"arn:aws:s3:::{self._reports_bucket}/*"
        doc = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {"AWS": ["*"]},
                    "Action": ["s3:GetObject"],
                    "Resource": [resource],
                }
            ],
        }
        return json.dumps(doc)

    def _apply_reports_bucket_anonymous_read_policy_sync(self) -> None:
        """Разрешает анонимное чтение объектов в бакете отчётов"""
        if not settings.MINIO_REPORTS_BUCKET_ANONYMOUS_READ:
            return
        if self._anonymous_read_policy_applied:
            return
        try:
            self._client.set_bucket_policy(
                self._reports_bucket,
                self._reports_bucket_anonymous_read_policy(),
            )
            self._anonymous_read_policy_applied = True
            logger.info(
                "Политика анонимного чтения объектов применена: bucket=%s",
                self._reports_bucket,
            )
        except Exception as e:
            if S3Error is not None and isinstance(e, S3Error):
                logger.error(
                    "Не удалось применить политику публичного чтения к bucket=%s: %s",
                    self._reports_bucket,
                    e,
                )
                raise StorageError(
                    "set_bucket_policy",
                    bucket=self._reports_bucket,
                    reason=str(e),
                ) from e
            logger.error(
                "Не удалось применить политику публичного чтения к bucket=%s: %s",
                self._reports_bucket,
                e,
                exc_info=True,
            )
            raise StorageError(
                "set_bucket_policy",
                bucket=self._reports_bucket,
                reason=str(e),
            ) from e

    def _ensure_reports_bucket_sync(self) -> None:
        """Создаёт bucket при необходимости и применяет policy анонимного чтения (если включено)."""
        try:
            if not self._client.bucket_exists(self._reports_bucket):
                if not settings.MINIO_AUTO_CREATE_BUCKET:
                    raise StorageError(
                        "ensure_bucket",
                        bucket=self._reports_bucket,
                        reason="bucket не существует и авто-создание отключено (MINIO_AUTO_CREATE_BUCKET)",
                    )
                self._client.make_bucket(self._reports_bucket)
                logger.info("Создан bucket MinIO: %s", self._reports_bucket)

            self._apply_reports_bucket_anonymous_read_policy_sync()
        except StorageError:
            raise

        except Exception as e:
            if S3Error is not None and isinstance(e, S3Error):
                raise StorageError(
                    "ensure_bucket",
                    bucket=self._reports_bucket,
                    reason=str(e),
                ) from e
            raise StorageError(
                "ensure_bucket",
                bucket=self._reports_bucket,
                reason=str(e),
            ) from e

    def _upload_report_html_sync(self, object_key: str, html_content: str) -> None:
        """Загружает HTML отчёта в MinIO"""
        self._ensure_reports_bucket_sync()
        try:
            payload = html_content.encode("utf-8")
            self._client.put_object(
                bucket_name=self._reports_bucket,
                object_name=object_key,
                data=io.BytesIO(payload),
                length=len(payload),
                content_type="text/html; charset=utf-8",
            )
        except StorageError:
            raise

        except Exception as e:
            if S3Error is not None and isinstance(e, S3Error):
                raise StorageError(
                    "upload_report_html",
                    bucket=self._reports_bucket,
                    key=object_key,
                    reason=str(e),
                ) from e
            raise StorageError(
                "upload_report_html",
                bucket=self._reports_bucket,
                key=object_key,
                reason=str(e),
            ) from e

        logger.info(
            "Отчёт загружен в MinIO: bucket=%s key=%s size=%s",
            self._reports_bucket,
            object_key,
            len(payload),
        )

    def _delete_report_object_sync(self, object_key: str) -> None:
        """Удаляет объект отчёта из MinIO"""
        try:
            self._client.remove_object(self._reports_bucket, object_key)
            logger.info(
                "Удалён объект отчёта из MinIO: bucket=%s key=%s",
                self._reports_bucket,
                object_key,
            )
        except Exception as e:
            if S3Error is None:
                raise StorageError(
                    "delete_report_object",
                    bucket=self._reports_bucket,
                    key=object_key,
                    reason=str(e),
                ) from e
            if isinstance(e, S3Error) and e.code == "NoSuchKey":
                logger.warning(
                    "Объект отчёта уже отсутствует в MinIO: bucket=%s key=%s",
                    self._reports_bucket,
                    object_key,
                )
                return
            raise StorageError(
                "delete_report_object",
                bucket=self._reports_bucket,
                key=object_key,
                reason=str(e),
            ) from e

    async def upload_report_html(self, object_key: str, html_content: str) -> None:
        """Загружает HTML отчёта в MinIO"""
        await asyncio.to_thread(self._upload_report_html_sync, object_key, html_content)

    async def delete_report_object(self, object_key: str) -> None:
        """Удаляет объект отчёта из MinIO"""
        await asyncio.to_thread(self._delete_report_object_sync, object_key)

    def build_report_url(self, object_key: str) -> str:
        """Формирует публичный URL"""
        if settings.MINIO_PUBLIC_BASE_URL:
            base = settings.MINIO_PUBLIC_BASE_URL.rstrip("/")
            return f"{base}/{self._reports_bucket}/{object_key}"
        scheme = "https" if settings.MINIO_SECURE else "http"
        return f"{scheme}://{settings.MINIO_ENDPOINT}/{self._reports_bucket}/{object_key}"

    def ensure_reports_bucket_and_policy_sync(self) -> None:
        """Создаёт бакет отчётов и применяет политику анонимного чтения"""
        self._ensure_reports_bucket_sync()

    def health_check(self) -> bool:
        """Проверяет, доступен ли MinIO"""
        try:
            self._client.list_buckets()
            return True
        except Exception as e:
            logger.error("Health check MinIO не прошёл: %s", e)
            return False


_minio_client_singleton: Optional[MinIOClient] = None


def get_minio_client() -> MinIOClient:
    global _minio_client_singleton
    if _minio_client_singleton is None:
        _minio_client_singleton = MinIOClient()
    return _minio_client_singleton