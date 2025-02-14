from django.urls import path
from .views import rooms, auth, main

urlpatterns = [
    path('', main.home, name="home"),
    path('update-user/', main.update_user, name="update-user"),
    
    path('login/', auth.login_user, name="login"),
    path('register/', auth.register_user, name="register"),        
    path('logout/', auth.logout_user, name="logout"),
    
    path('create-room/', rooms.create_room, name="create-room"),
    
    path('topics/', rooms.topics, name="topics"),
    path('activity/', rooms.activity, name="activity"),
    path('update-room/<slug:username>/<slug:room>/', rooms.update_room, name="update-room"),
    path('<slug:username>/', main.user_profile, name="user-profile"),
    path('<slug:username>/<slug:room>/', rooms.room, name="room")
]
