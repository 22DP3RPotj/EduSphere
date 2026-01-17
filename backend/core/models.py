import pghistory.models
from django.db import models


class CoreEvent(pghistory.models.Events):
    """
    Custom Events proxy model that exposes context fields as structured fields.

    This allows querying and displaying context data like user, url, and remote_addr
    as regular model fields instead of accessing nested JSON data.
    """

    # Middleware-provided fields
    user = pghistory.ProxyField("pgh_context__user", models.UUIDField(null=True))
    url = pghistory.ProxyField("pgh_context__url", models.TextField(null=True))
    remote_addr = pghistory.ProxyField(
        "pgh_context__remote_addr", models.CharField(max_length=45, null=True)
    )

    # Process identification fields
    # source = pghistory.ProxyField("pgh_context__source", models.CharField(max_length=50, null=True))
    # scan_type = pghistory.ProxyField("pgh_context__scan_type", models.CharField(max_length=100, null=True))

    class Meta:
        proxy = True
        app_label = "core"
