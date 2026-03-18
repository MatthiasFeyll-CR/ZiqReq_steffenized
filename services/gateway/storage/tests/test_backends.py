from unittest.mock import MagicMock, patch

from django.test import TestCase

from storage.backends import AzureBlobBackend, MinIOBackend, StorageBackend
from storage.factory import get_storage_backend, reset_storage_backend


class TestStorageBackendABC(TestCase):
    """Test that StorageBackend is a proper ABC with required methods."""

    def test_cannot_instantiate_abc(self):
        with self.assertRaises(TypeError):
            StorageBackend()  # type: ignore[abstract]

    def test_has_required_methods(self):
        assert hasattr(StorageBackend, "upload_file")
        assert hasattr(StorageBackend, "delete_file")
        assert hasattr(StorageBackend, "get_presigned_url")
        assert hasattr(StorageBackend, "file_exists")


class TestMinIOBackend(TestCase):
    """Test MinIOBackend with mocked minio client."""

    def setUp(self):
        patcher = patch("storage.backends.Minio")
        self.mock_minio_cls = patcher.start()
        self.mock_client = MagicMock()
        self.mock_minio_cls.return_value = self.mock_client
        self.addCleanup(patcher.stop)

    @patch.dict("os.environ", {
        "MINIO_ENDPOINT": "localhost:9000",
        "MINIO_ACCESS_KEY": "testkey",
        "MINIO_SECRET_KEY": "testsecret",
        "MINIO_BUCKET": "test-bucket",
        "MINIO_SECURE": "false",
    })
    def _make_backend(self) -> MinIOBackend:
        return MinIOBackend()

    def test_init_creates_client(self):
        backend = self._make_backend()
        self.mock_minio_cls.assert_called_once_with(
            "localhost:9000",
            access_key="testkey",
            secret_key="testsecret",
            secure=False,
        )
        assert backend.bucket == "test-bucket"

    def test_ensure_bucket_creates_when_missing(self):
        backend = self._make_backend()
        self.mock_client.bucket_exists.return_value = False
        backend.ensure_bucket()
        self.mock_client.make_bucket.assert_called_once_with("test-bucket")

    def test_ensure_bucket_skips_when_exists(self):
        backend = self._make_backend()
        self.mock_client.bucket_exists.return_value = True
        backend.ensure_bucket()
        self.mock_client.make_bucket.assert_not_called()

    def test_upload_file(self):
        backend = self._make_backend()
        backend.upload_file("path/to/file.pdf", b"file-content", "application/pdf")
        self.mock_client.put_object.assert_called_once()
        call_args = self.mock_client.put_object.call_args
        assert call_args[0][0] == "test-bucket"
        assert call_args[0][1] == "path/to/file.pdf"
        assert call_args[1]["content_type"] == "application/pdf"
        assert call_args[1]["length"] == len(b"file-content")

    def test_delete_file(self):
        backend = self._make_backend()
        backend.delete_file("path/to/file.pdf")
        self.mock_client.remove_object.assert_called_once_with("test-bucket", "path/to/file.pdf")

    def test_delete_file_logs_on_error(self):
        from minio.error import S3Error

        backend = self._make_backend()
        self.mock_client.remove_object.side_effect = S3Error(
            "NoSuchKey", "Not found", "resource", "request_id", "host_id", "response"
        )
        # Should not raise
        backend.delete_file("path/to/file.pdf")

    def test_get_presigned_url(self):
        backend = self._make_backend()
        self.mock_client.presigned_get_object.return_value = "https://minio:9000/test-bucket/file.pdf?token=abc"
        url = backend.get_presigned_url("file.pdf", expires_seconds=300, filename="report.pdf")
        assert url == "https://minio:9000/test-bucket/file.pdf?token=abc"
        call_args = self.mock_client.presigned_get_object.call_args
        assert call_args[0][0] == "test-bucket"
        assert call_args[0][1] == "file.pdf"
        assert call_args[1]["extra_query_params"]["response-content-disposition"] == 'attachment; filename="report.pdf"'

    def test_get_presigned_url_without_filename(self):
        backend = self._make_backend()
        self.mock_client.presigned_get_object.return_value = "https://minio:9000/test-bucket/file.pdf"
        url = backend.get_presigned_url("file.pdf")
        assert url == "https://minio:9000/test-bucket/file.pdf"
        call_args = self.mock_client.presigned_get_object.call_args
        assert call_args[1]["extra_query_params"] is None

    def test_file_exists_true(self):
        backend = self._make_backend()
        self.mock_client.stat_object.return_value = MagicMock()
        assert backend.file_exists("path/to/file.pdf") is True

    def test_file_exists_false(self):
        from minio.error import S3Error

        backend = self._make_backend()
        self.mock_client.stat_object.side_effect = S3Error(
            "NoSuchKey", "Not found", "resource", "request_id", "host_id", "response"
        )
        assert backend.file_exists("path/to/file.pdf") is False


class TestAzureBlobBackend(TestCase):
    """Test that AzureBlobBackend raises NotImplementedError."""

    def setUp(self):
        self.backend = AzureBlobBackend()

    def test_upload_file_raises(self):
        with self.assertRaises(NotImplementedError):
            self.backend.upload_file("key", b"data", "type")

    def test_delete_file_raises(self):
        with self.assertRaises(NotImplementedError):
            self.backend.delete_file("key")

    def test_get_presigned_url_raises(self):
        with self.assertRaises(NotImplementedError):
            self.backend.get_presigned_url("key")

    def test_file_exists_raises(self):
        with self.assertRaises(NotImplementedError):
            self.backend.file_exists("key")


class TestGetStorageBackend(TestCase):
    """Test the factory function."""

    def setUp(self):
        reset_storage_backend()

    def tearDown(self):
        reset_storage_backend()

    @patch("storage.factory.MinIOBackend")
    @patch.dict("os.environ", {"STORAGE_BACKEND": "minio"})
    def test_returns_minio_backend(self, mock_cls):
        mock_cls.return_value = MagicMock(spec=MinIOBackend)
        backend = get_storage_backend()
        assert isinstance(backend, MagicMock)
        mock_cls.assert_called_once()

    @patch("storage.factory.AzureBlobBackend")
    @patch.dict("os.environ", {"STORAGE_BACKEND": "azure"})
    def test_returns_azure_backend(self, mock_cls):
        mock_cls.return_value = MagicMock(spec=AzureBlobBackend)
        backend = get_storage_backend()
        assert isinstance(backend, MagicMock)
        mock_cls.assert_called_once()

    @patch.dict("os.environ", {"STORAGE_BACKEND": "unknown"})
    def test_raises_for_unknown_backend(self):
        with self.assertRaises(ValueError, msg="Unknown STORAGE_BACKEND"):
            get_storage_backend()

    @patch("storage.factory.MinIOBackend")
    @patch.dict("os.environ", {"STORAGE_BACKEND": "minio"})
    def test_returns_singleton(self, mock_cls):
        mock_cls.return_value = MagicMock(spec=MinIOBackend)
        b1 = get_storage_backend()
        b2 = get_storage_backend()
        assert b1 is b2
        mock_cls.assert_called_once()

    @patch.dict("os.environ", {"STORAGE_BACKEND": "minio"}, clear=False)
    def test_default_is_minio(self):
        with patch("storage.factory.MinIOBackend") as mock_cls:
            mock_cls.return_value = MagicMock(spec=MinIOBackend)
            get_storage_backend()
            mock_cls.assert_called_once()
