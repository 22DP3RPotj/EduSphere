from django.urls import re_path
from . import views


urlpatterns = [
    re_path(r'^delete-room/(?P<id>[a-f0-9\-]+)/$', views.delete_room, name='delete-room'),
    re_path(r'^delete-message/(?P<id>[a-f0-9\-]+)/$', views.delete_message, name='delete-message'),
]
