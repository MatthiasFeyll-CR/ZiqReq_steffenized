import abc
import io
import logging
import os

from minio import Minio
from minio.error import S3Error

logger = logging.getLogger(__name__)


class StorageBackend(abc.ABC):
    """Abstract base class for file storage backends."""

    @abc.abstractmethod
    def upload_file(self, storage_key: str, file_data: bytes, content_type: str) -> None:
        """Upload a file to storage."""

    @abc.abstractmethod
    def delete_file(self, storage_key: str) -> None:
        """Delete a file from storage."""

    @abc.abstractmethod
    def get_presigned_url(self, storage_key: str, expires_seconds: int = 900, filename: str | None = None) -> str:
        """Get a presigned URL for downloading a file. Default TTL is 15 minutes."""

    @abc.abstractmethod
    def download_file(self, storage_key: str) -> tuple[bytes, str]:
        """Download a file from storage. Returns (file_data, content_type)."""

    @abc.abstractmethod
    def file_exists(self, storage_key: str) -> bool:
        """Check if a file exists in storage."""


class MinIOBackend(StorageBackend):
    """MinIO storage backend implementation."""

    def __init__(self) -> None:
        self.endpoint = os.environ.get("MINIO_ENDPOINT", "minio:9000")
        self.access_key = os.environ.get("MINIO_ACCESS_KEY", "minioadmin")
        self.secret_key = os.environ.get("MINIO_SECRET_KEY", "minioadmin")
        self.bucket = os.environ.get("MINIO_BUCKET", "attachments")
        self.secure = os.environ.get("MINIO_SECURE", "false").lower() == "true"
        self.client = Minio(
            self.endpoint,
            access_key=self.access_key,
            secret_key=self.secret_key,
            secure=self.secure,
        )

    def ensure_bucket(self) -> None:
        """Create the bucket if it doesn't exist."""
        if not self.client.bucket_exists(self.bucket):
            self.client.make_bucket(self.bucket)
            logger.info("Created MinIO bucket: %s", self.bucket)

    def upload_file(self, storage_key: str, file_data: bytes, content_type: str) -> None:
        data = io.BytesIO(file_data)
        self.client.put_object(
            self.bucket,
            storage_key,
            data,
            length=len(file_data),
            content_type=content_type,
        )

    def delete_file(self, storage_key: str) -> None:
        try:
            self.client.remove_object(self.bucket, storage_key)
        except S3Error as e:
            logger.warning("Failed to delete file %s from MinIO: %s", storage_key, e)

    def get_presigned_url(self, storage_key: str, expires_seconds: int = 900, filename: str | None = None) -> str:
        from datetime import timedelta

        extra_query_params = {}
        if filename:
            extra_query_params["response-content-disposition"] = f"attachment; filename=\"{filename}\""

        return self.client.presigned_get_object(
            self.bucket,
            storage_key,
            expires=timedelta(seconds=expires_seconds),
            extra_query_params=extra_query_params if extra_query_params else None,
        )

    def download_file(self, storage_key: str) -> tuple[bytes, str]:
        response = None
        try:
            response = self.client.get_object(self.bucket, storage_key)
            data = response.read()
            content_type = response.headers.get("Content-Type", "application/octet-stream")
            return data, content_type
        finally:
            if response is not None:
                response.close()
                response.release_conn()

    def file_exists(self, storage_key: str) -> bool:
        try:
            self.client.stat_object(self.bucket, storage_key)
            return True
        except S3Error:
            return False


class AzureBlobBackend(StorageBackend):
    """Azure Blob Storage backend stub (production concern, not M22 scope)."""

    def upload_file(self, storage_key: str, file_data: bytes, content_type: str) -> None:
        raise NotImplementedError("AzureBlobBackend is not implemented yet.")

    def delete_file(self, storage_key: str) -> None:
        raise NotImplementedError("AzureBlobBackend is not implemented yet.")

    def get_presigned_url(self, storage_key: str, expires_seconds: int = 900, filename: str | None = None) -> str:
        raise NotImplementedError("AzureBlobBackend is not implemented yet.")

    def download_file(self, storage_key: str) -> tuple[bytes, str]:
        raise NotImplementedError("AzureBlobBackend is not implemented yet.")

    def file_exists(self, storage_key: str) -> bool:
        raise NotImplementedError("AzureBlobBackend is not implemented yet.")
