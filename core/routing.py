from django.urls import path
from .consumers import ChatConsumer

websocket_urlpatterns = [
    path('ws/room/<uuid:id>/', ChatConsumer.as_asgi()),
]
