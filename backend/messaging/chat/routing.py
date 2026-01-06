from django.urls import path
from backend.messaging.chat import consumers


websocket_urlpatterns = [
    path("ws/chat/<uuid:room_id>", consumers.ChatConsumer.as_asgi()),
]
