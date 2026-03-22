from django.urls import include, path
from graphql_jwt.decorators import jwt_cookie
from backend.graphql.views import GraphqlView

urlpatterns = [
    path(
        "graphql/",
        jwt_cookie(GraphqlView.as_view()),
    ),
    path("infra/", include("backend.infra.urls")),
]
