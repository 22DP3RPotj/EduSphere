from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name="home"),
    path('room/<uuid:id>/', views.room, name="room"),
    path('create-room/', views.create_room, name="create-room"),
]
