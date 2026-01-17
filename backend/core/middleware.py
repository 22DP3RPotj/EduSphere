import pghistory.middleware


class PgHistoryMiddleware(pghistory.middleware.HistoryMiddleware):
    """
    Custom pghistory middleware that extends the built-in HistoryMiddleware
    to add remote_addr context following the pattern from:
    https://django-pghistory.readthedocs.io/en/3.8.1/context/#middleware
    """

    def get_context(self, request):
        context = super().get_context(request)

        # Add remote address with proxy support
        remote_addr = request.META.get("HTTP_X_FORWARDED_FOR")
        # Get the first IP if there are multiple (proxy chain), or fall back to REMOTE_ADDR
        remote_addr = (
            remote_addr.split(",")[0].strip()
            if remote_addr
            else request.META.get("REMOTE_ADDR")
        )

        context["remote_addr"] = remote_addr
        return context
