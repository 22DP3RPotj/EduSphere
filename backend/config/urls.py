from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_protect, csrf_exempt
from graphql_jwt.decorators import jwt_cookie
from graphene_file_upload.django import FileUploadGraphQLView


urlpatterns = [
    path('admin/', admin.site.urls),
    path("graphql/", jwt_cookie(
        csrf_exempt(ensure_csrf_cookie(
            FileUploadGraphQLView.as_view(graphiql=True)
        ))
    )),
    path("api/", include("backend.api.urls")),
]

# from django.conf.urls.static import static

# if settings.DEBUG:
#     urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
#     urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

