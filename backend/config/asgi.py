from django.core.asgi import get_asgi_application
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from backend.core.chat.routing import websocket_urlpatterns
from backend.core.chat.middleware import JwtAuthMiddleware

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        JwtAuthMiddleware(
            URLRouter(websocket_urlpatterns)
        )
    ),
})