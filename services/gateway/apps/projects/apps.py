import logging
import os

from django.apps import AppConfig

logger = logging.getLogger(__name__)


class ProjectsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.projects"
    label = "gateway_projects"

    def ready(self) -> None:
        storage_backend = os.environ.get("STORAGE_BACKEND", "").lower()
        if storage_backend == "minio":
            try:
                from storage.backends import MinIOBackend

                backend = MinIOBackend()
                backend.ensure_bucket()
                logger.info("MinIO bucket auto-creation complete.")
            except Exception:
                logger.warning("Could not auto-create MinIO bucket on startup.", exc_info=True)
