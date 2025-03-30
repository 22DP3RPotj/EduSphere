from django.urls import path, re_path
from .views import rooms, auth, main, api

urlpatterns = [
    path('', main.home, name="home"),
    path('update-user/', main.update_user, name="update-user"),
    
    path('login/', auth.login_user, name="login"),
    path('register/', auth.register_user, name="register"),        
    path('logout/', auth.logout_user, name="logout"),
    
    path('topics/', rooms.topics, name="topics"),
    path('activity/', rooms.activity, name="activity"),
    
    re_path(r'^delete-room/(?P<id>[a-f0-9\-]+)/$', api.delete_room, name='delete-room'),
    re_path(r'^delete-message/(?P<id>[a-f0-9\-]+)/$', api.delete_message, name='delete-message'),
    
    path('create-room/', rooms.create_room, name="create-room"),
    path('update-room/<slug:username>/<slug:room>/', rooms.update_room, name="update-room"),
    path('<slug:username>/', main.user_profile, name="user-profile"),
    path('<slug:username>/<slug:room>/', rooms.room, name="room"),

]
