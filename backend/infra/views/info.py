from django.conf import settings
from django.http import JsonResponse, HttpRequest
from django.views.decorators.http import require_GET


@require_GET
def version(request: HttpRequest) -> JsonResponse:
    return JsonResponse(
        {"version": settings.APP_VERSION, "commit": settings.GIT_SHA}, status=200
    )
