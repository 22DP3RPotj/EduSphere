from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name="home"),
    
    path('login/', views.login_user, name="login"),
    path('logout/', views.logout_user, name="logout"),
    
    path('room/<uuid:id>/', views.room, name="room"),
    path('create-room/', views.create_room, name="create-room"),
    path('update-room/<uuid:id>/', views.update_room, name="update-room"),
    path('delete-room/<uuid:id>/', views.delete_room, name="delete-room"),
]
