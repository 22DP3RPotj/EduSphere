from django.urls import path
from .consumers import ChatConsumer

websocket_urlpatterns = [
    path('ws/room/<slug:username>/<slug:room>', ChatConsumer.as_asgi()),
]
