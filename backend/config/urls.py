from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.decorators.csrf import csrf_exempt
from graphene_file_upload.django import FileUploadGraphQLView


urlpatterns = [
    path('admin/', admin.site.urls),
    path("graphql/", csrf_exempt(FileUploadGraphQLView.as_view(graphiql=settings.DEBUG))),
    path('', include('backend.core.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler400 = "backend.core.views.errors.custom_400"
handler403 = "backend.core.views.errors.custom_403"
handler404 = "backend.core.views.errors.custom_404"
handler500 = "backend.core.views.errors.custom_500"
