from django.urls import path
from .views import rooms, auth, main

urlpatterns = [
    path('', main.home, name="home"),
    path('profile/<str:id>/', main.user_profile, name="user-profile"),
    path('update-user/', main.update_user, name="update-user"),
    
    path('login/', auth.login_user, name="login"),
    path('register/', auth.register_user, name="register"),        
    path('logout/', auth.logout_user, name="logout"),
    
    path('room/<uuid:id>/', rooms.room, name="room"),
    path('create-room/', rooms.create_room, name="create-room"),
    path('update-room/<uuid:id>/', rooms.update_room, name="update-room"),
    
    path('topics/', rooms.topics, name="topics"),
    path('activity/', rooms.activity, name="activity"),
]
