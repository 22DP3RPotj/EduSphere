from django.urls import include, path
from django.views.decorators.csrf import csrf_exempt
from graphql_jwt.decorators import jwt_cookie
from backend.graphql.views import GraphqlView

urlpatterns = [
    path(
        "graphql/",
        jwt_cookie(csrf_exempt(GraphqlView.as_view())),
    ),
    path("infra/", include("backend.infra.urls")),
]
