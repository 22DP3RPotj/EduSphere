from http.cookies import SimpleCookie
from graphql_jwt.shortcuts import get_user_by_token
from channels.db import database_sync_to_async
from channels.middleware import BaseMiddleware


def _get_anonymous_user():
    from django.contrib.auth.models import AnonymousUser
    return AnonymousUser()

@database_sync_to_async
def _get_user(token: str):
    try:
        return get_user_by_token(token)
    except Exception:
        return None

class JwtAuthMiddleware(BaseMiddleware):
    """
    ASGI middleware that takes the JWT from the HttpOnly 'JWT' cookie,
    validates it via graphql_jwt.shortcuts.get_user_by_token, and
    populates scope['user'].
    """
    async def __call__(self, scope, receive, send):
        # Grab raw cookie header (if any)
        headers = {name: value for name, value in scope.get("headers", [])}
        raw_cookie = headers.get(b"cookie", b"").decode()

        user = _get_anonymous_user()
        
        if raw_cookie:
            cookie = SimpleCookie(raw_cookie)
            if "JWT" in cookie:
                token = cookie["JWT"].value
                user = await _get_user(token)

        scope["user"] = user
        return await super().__call__(scope, receive, send)
