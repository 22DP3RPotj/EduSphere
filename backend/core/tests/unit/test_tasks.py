from unittest import mock
import pytest
from django.test import TestCase, override_settings
from django.utils import timezone
from django.db import DatabaseError
import pghistory.models
from datetime import datetime, timedelta
from backend.core.tasks import cleanup_old_audit_logs


pytestmark = pytest.mark.unit


# Create a mock model class simulating a pghistory Event model
class MockEvent(pghistory.models.Event):
    class Meta:
        proxy = False
        app_label = "core"
        managed = False


class CleanupOldAuditLogsTests(TestCase):
    def setUp(self):
        self.MockEvent = MockEvent
        self.MockEvent.__name__ = "MockEvent"

    @override_settings(AUDIT_LOG_RETENTION_DAYS=30, AUDIT_LOG_BATCH_SIZE=100)
    @mock.patch("backend.core.tasks.apps.get_models")
    @mock.patch("backend.core.tasks.logger")
    @mock.patch("backend.core.tasks.timezone")
    def test_cleanup_successful_deletion(
        self, mock_timezone, mock_logger, mock_get_models
    ):
        """Test that old records are correctly identified and deleted."""
        # Setup fixed time
        fixed_now = timezone.make_aware(datetime(2025, 1, 1, 12, 0, 0))
        mock_timezone.now.return_value = fixed_now
        mock_timezone.timedelta = timedelta

        # Setup mock model behavior
        mock_objects = mock.MagicMock()
        self.MockEvent.objects = mock_objects

        # Setup filter return values
        mock_queryset = mock.MagicMock()
        mock_objects.filter.return_value = mock_queryset

        mock_values_list = mock.MagicMock()
        mock_queryset.values_list.return_value = mock_values_list

        # Simulate two batches:
        # 1. First batch returns [1, 2, 3]
        # 2. Second batch returns [] (terminating the loop)
        id_batch = [1, 2, 3]
        mock_values_list.__getitem__.side_effect = [id_batch, []]

        # Simulate deletion count
        mock_queryset.delete.return_value = (3, {"core.MockEvent": 3})

        # Setup get_models to return our mock model
        mock_get_models.return_value = [self.MockEvent]

        # Execute
        total_deleted = cleanup_old_audit_logs()

        # Verify
        expected_cutoff = fixed_now - timedelta(days=30)

        # Verify initial logging
        mock_logger.info.assert_any_call(
            f"Cleaning up audit logs older than 30 days (before {expected_cutoff})"
        )

        # Verify ID fetching
        mock_objects.filter.assert_any_call(pgh_created_at__lt=expected_cutoff)

        # Verify deletion calls
        mock_objects.filter.assert_any_call(pk__in=id_batch)
        self.assertTrue(mock_queryset.delete.called)

        # Verify logs for deleted records
        mock_logger.info.assert_any_call("Deleted 3 records from core.MockEvent")
        mock_logger.info.assert_any_call("Total audit log records deleted: 3")

        self.assertEqual(total_deleted, 3)

    @override_settings(AUDIT_LOG_RETENTION_DAYS=30)
    @mock.patch("backend.core.tasks.apps.get_models")
    @mock.patch("backend.core.tasks.logger")
    @mock.patch("backend.core.tasks.timezone")
    def test_cleanup_database_error(self, mock_timezone, mock_logger, mock_get_models):
        """Test handling of DatabaseError during cleanup."""
        mock_timezone.now.return_value = timezone.make_aware(datetime(2025, 1, 1))
        mock_timezone.timedelta = timedelta

        mock_objects = mock.MagicMock()
        self.MockEvent.objects = mock_objects

        # Raise DatabaseError when filtering
        mock_objects.filter.side_effect = DatabaseError("Connection failed")

        mock_get_models.return_value = [self.MockEvent]

        total_deleted = cleanup_old_audit_logs()

        # Verify error was logged
        mock_logger.error.assert_called_with(
            "Error cleaning up core.MockEvent: Connection failed"
        )

        # Should return 0 deleted
        self.assertEqual(total_deleted, 0)

    @mock.patch("backend.core.tasks.apps.get_models")
    @mock.patch("backend.core.tasks.timezone")
    def test_cleanup_ignores_non_pghistory_models(self, mock_timezone, mock_get_models):
        """Test that normal models are ignored."""
        mock_timezone.now.return_value = timezone.make_aware(datetime(2025, 1, 1))
        mock_timezone.timedelta = timedelta

        class NormalModel:
            pass

        mock_get_models.return_value = [NormalModel]

        total_deleted = cleanup_old_audit_logs()

        self.assertEqual(total_deleted, 0)

    @mock.patch("backend.core.tasks.apps.get_models")
    @mock.patch("backend.core.tasks.timezone")
    def test_cleanup_ignores_proxy_models(self, mock_timezone, mock_get_models):
        """Test that proxy models are ignored."""
        mock_timezone.now.return_value = timezone.make_aware(datetime(2025, 1, 1))
        mock_timezone.timedelta = timedelta

        # Temporarily modify the proxy status of the MockEvent
        original_proxy = self.MockEvent._meta.proxy
        self.MockEvent._meta.proxy = True

        try:
            mock_get_models.return_value = [self.MockEvent]

            total_deleted = cleanup_old_audit_logs()

            self.assertEqual(total_deleted, 0)
        finally:
            self.MockEvent._meta.proxy = original_proxy
