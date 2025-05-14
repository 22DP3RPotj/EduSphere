from django.http import JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie

@ensure_csrf_cookie
def csrf(request):
    """
    View that sets the CSRF cookie.
    """
    return JsonResponse({"SetCsrfToken": "X-CSRFToken"})
