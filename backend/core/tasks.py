from celery import shared_task
from django.apps import apps
from django.conf import settings
from django.db import DatabaseError
from django.utils import timezone
import pghistory.models
import logging

logger = logging.getLogger(__name__)


@shared_task
def cleanup_old_audit_logs():
    """
    Deletes audit logs older than settings.AUDIT_LOG_RETENTION_DAYS.
    """
    days = settings.AUDIT_LOG_RETENTION_DAYS
    batch_size = settings.AUDIT_LOG_BATCH_SIZE
    cutoff_date = timezone.now() - timezone.timedelta(days=days)

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

            try:
                while True:
                    ids_to_delete = list(
                        model.objects.filter(
                            pgh_created_at__lt=cutoff_date
                        ).values_list("pk", flat=True)[:batch_size]
                    )

                    if not ids_to_delete:
                        break

                    count, _ = model.objects.filter(pk__in=ids_to_delete).delete()
                    model_deleted_count += count

                if model_deleted_count > 0:
                    logger.info(
                        f"Deleted {model_deleted_count} records from {model_name}"
                    )
                    total_deleted += model_deleted_count
            except DatabaseError as e:
                logger.error(f"Error cleaning up {model_name}: {e}")

    logger.info(f"Total audit log records deleted: {total_deleted}")
    return total_deleted
