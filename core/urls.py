from django.urls import path
from .views import room_views, auth_views

urlpatterns = [
    path('', room_views.home, name="home"),
    
    path('profile/<str:id>/', room_views.user_profile, name="user-profile"),
    
    path('login/', auth_views.login_user, name="login"),
    path('register/', auth_views.register_user, name="register"),        
    path('logout/', auth_views.logout_user, name="logout"),
    
    path('room/<uuid:id>/', room_views.room, name="room"),
    path('create-room/', room_views.create_room, name="create-room"),
    path('update-room/<uuid:id>/', room_views.update_room, name="update-room"),
]
