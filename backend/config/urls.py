from django.urls import include, path
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from graphql_jwt.decorators import jwt_cookie
from graphene_file_upload.django import FileUploadGraphQLView


urlpatterns = [
    path(
        "graphql/",
        jwt_cookie(csrf_exempt(FileUploadGraphQLView.as_view(graphiql=settings.DEBUG))),
    ),
    path("infra/", include("backend.infra.urls")),
]
