# from django.conf import settings
# from django.views.decorators.csrf import csrf_protect
# from django.urls import include

from django.urls import path
from django.contrib import admin
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_exempt
from graphql_jwt.decorators import jwt_cookie
from graphene_file_upload.django import FileUploadGraphQLView


urlpatterns = [
    path('admin/', admin.site.urls),
    path("graphql/", jwt_cookie(
        csrf_exempt(ensure_csrf_cookie(
            FileUploadGraphQLView.as_view(graphiql=True)
        ))
    )),
    # Csrf token endpoint
    # TODO: Come up with a better way to handle this
    # path("api/", include("backend.api.urls")),
]

