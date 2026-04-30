from django.db import close_old_connections, connection
from django.db.utils import DatabaseError
from django.http import HttpRequest, JsonResponse
from django.views.decorators.http import require_GET


@require_GET
def live(request: HttpRequest) -> JsonResponse:
    return JsonResponse({"status": "ok"}, status=200)


@require_GET
def ready(request: HttpRequest) -> JsonResponse:
    close_old_connections()

    checks: dict[str, str] = {}

    try:
        connection.ensure_connection()
    except DatabaseError:
        return JsonResponse(
            {
                "status": "error",
                "checks": {"database": "failed"},
            },
            status=503,
        )
    else:
        checks["database"] = "ok"
        return JsonResponse({"status": "ok", "checks": checks}, status=200)
    finally:
        connection.close()
