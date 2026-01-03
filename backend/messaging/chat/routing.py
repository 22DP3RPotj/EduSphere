from django.urls import path
from backend.messaging.chat import consumers


websocket_urlpatterns = [
    path('ws/chat/<slug:username>/<slug:room>', consumers.ChatConsumer.as_asgi()),
]
