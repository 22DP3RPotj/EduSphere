from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from django.core.asgi import get_asgi_application

from backend.messaging.chat.middleware import JwtAuthMiddleware
from backend.messaging.chat.routing import websocket_urlpatterns

application = ProtocolTypeRouter(
    {
        "http": get_asgi_application(),
        "websocket": AllowedHostsOriginValidator(
            JwtAuthMiddleware(URLRouter(websocket_urlpatterns))
        ),
    }
)
