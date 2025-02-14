from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),
    
    path('api/', include('api.urls')),
    path('', include('core.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler400 = "core.views.errors.custom_400"
handler403 = "core.views.errors.custom_403"
handler404 = "core.views.errors.custom_404"
handler500 = "core.views.errors.custom_500"
