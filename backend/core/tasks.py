from celery import shared_task
from django.apps import apps
from django.conf import settings
from django.db import DatabaseError
from django.utils import timezone
from typing import Optional
from datetime import timedelta
import pghistory.models
import logging


logger = logging.getLogger(__name__)


def run_audit_log_cleanup(days: Optional[int] = None, batch_size: Optional[int] = None):
    """
    Core logic for cleaning up audit logs.
    Separated from the task for easier testing and manual execution.
    """
    if days is None:
        days = settings.AUDIT_LOG_RETENTION_DAYS
    if batch_size is None:
        batch_size = settings.AUDIT_LOG_BATCH_SIZE

    cutoff_date = timezone.now() - timedelta(days=days)

    logger.info(f"Cleaning up audit logs older than {days} days (before {cutoff_date})")

    total_deleted = 0

    for model in apps.get_models():
        if (
            issubclass(model, pghistory.models.Event)
            and model is not pghistory.models.Event
        ):
            if model._meta.proxy:
                continue

            model_name = f"{model._meta.app_label}.{model.__name__}"
            model_deleted_count = 0

            while True:
                ids_to_delete = list(
                    model.objects.filter(pgh_created_at__lt=cutoff_date).values_list(
                        "pk", flat=True
                    )[:batch_size]
                )

                if not ids_to_delete:
                    break

                # We define the transaction boundary here, per batch, just to be safe,
                # though single delete statements are atomic by default in Postgres.
                count, _ = model.objects.filter(pk__in=ids_to_delete).delete()
                model_deleted_count += count

            if model_deleted_count > 0:
                logger.info(f"Deleted {model_deleted_count} records from {model_name}")
                total_deleted += model_deleted_count

    logger.info(f"Total audit log records deleted: {total_deleted}")
    return total_deleted


@shared_task(
    bind=True,
    autoretry_for=(DatabaseError,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 5},
)
def cleanup_old_audit_logs(self):
    """
    Celery task wrapper for audit log cleanup.
    """
    return run_audit_log_cleanup()
