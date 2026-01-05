from django.db import connection
from django.db.utils import OperationalError, DatabaseError
from django.http import JsonResponse, HttpRequest
from django.views.decorators.http import require_GET


@require_GET
def live(request: HttpRequest) -> JsonResponse:
    return JsonResponse({"status": "ok"}, status=200)


@require_GET
def ready(request: HttpRequest) -> JsonResponse:
    checks: dict[str, str] = {}

    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            checks["database"] = "ok"
    except (OperationalError, DatabaseError):
        return JsonResponse(
            {
                "status": "error",
                "checks": {"database": "failed"},
            },
            status=503,
        )

    return JsonResponse({"status": "ok", "checks": checks}, status=200)
