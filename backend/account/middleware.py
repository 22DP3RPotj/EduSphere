from django.utils.timezone import now

from backend.account.utils import get_inactivity_threshold, update_last_seen


class LastSeenMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        user = getattr(request, "user", None)
        if user and user.is_authenticated:
            threshold = get_inactivity_threshold()
            if not user.last_seen or (now() - user.last_seen) > threshold:
                update_last_seen(user=user)

        return response
