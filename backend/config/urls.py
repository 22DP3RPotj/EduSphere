from django.urls import include, path
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from graphql_jwt.decorators import jwt_cookie
from graphene_file_upload.django import FileUploadGraphQLView
from backend.graphql.security import get_validation_rules

urlpatterns = [
    path(
        "graphql/",
        jwt_cookie(
            csrf_exempt(
                FileUploadGraphQLView.as_view(
                    graphiql=settings.DEBUG, validation_rules=get_validation_rules()
                )
            )
        ),
    ),
    path("infra/", include("backend.infra.urls")),
]
