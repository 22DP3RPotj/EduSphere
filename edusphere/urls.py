from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
]

handler400 = "core.views.error_views.custom_400"
handler403 = "core.views.error_views.custom_403"
handler404 = "core.views.error_views.custom_404"
handler500 = "core.views.error_views.custom_500"
