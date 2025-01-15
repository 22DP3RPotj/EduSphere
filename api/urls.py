from django.urls import path
from . import views

# TODO: Add regex

urlpatterns = [
    path('delete-room/<uuid:id>/', views.delete_room, name='delete-room'),
    path('delete-message/<id>/', views.delete_message, name='delete-message'),
]
