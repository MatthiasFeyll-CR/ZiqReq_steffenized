import os

from storage.backends import AzureBlobBackend, MinIOBackend, StorageBackend

_backend_instance: StorageBackend | None = None


def get_storage_backend() -> StorageBackend:
    """Return the configured storage backend based on the STORAGE_BACKEND env var.

    Returns a singleton instance to avoid creating multiple clients.
    """
    global _backend_instance
    if _backend_instance is not None:
        return _backend_instance

    backend_name = os.environ.get("STORAGE_BACKEND", "minio").lower()

    if backend_name == "minio":
        _backend_instance = MinIOBackend()
    elif backend_name == "azure":
        _backend_instance = AzureBlobBackend()
    else:
        raise ValueError(f"Unknown STORAGE_BACKEND: {backend_name!r}. Must be 'minio' or 'azure'.")

    return _backend_instance


def reset_storage_backend() -> None:
    """Reset the singleton instance. Used in tests."""
    global _backend_instance
    _backend_instance = None
