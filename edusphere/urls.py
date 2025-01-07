from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('base.urls')),
]

handler400 = "base.views.error_views.custom_400"
handler403 = "base.views.error_views.custom_403"
handler404 = "base.views.error_views.custom_404"
handler500 = "base.views.error_views.custom_500"
