from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
    path('', include('core.urls')),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler400 = "core.views.error_views.custom_400"
handler403 = "core.views.error_views.custom_403"
handler404 = "core.views.error_views.custom_404"
handler500 = "core.views.error_views.custom_500"
