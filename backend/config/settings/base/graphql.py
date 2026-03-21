from ..environment import env
from datetime import timedelta

GRAPHENE = {
    "SCHEMA": "backend.graphql.schema.schema",
    "MIDDLEWARE": [
        "graphql_jwt.middleware.JSONWebTokenMiddleware",
        # Custom middleware
        "backend.infra.middleware.GQLPrometheusMiddleware",
        "backend.graphql.error.middleware.InternalErrorMiddleware",
        "backend.graphql.error.middleware.ErrorTransformingMiddleware",
    ],
}

GRAPHQL_MAX_DEPTH = env.int("GRAPHQL_MAX_DEPTH", default=10)

GRAPHQL_JWT = {
    "JWT_VERIFY_EXPIRATION": True,
    "JWT_EXPIRATION_DELTA": timedelta(minutes=10),
    "JWT_REFRESH_EXPIRATION_DELTA": timedelta(days=7),
    "JWT_COOKIE_SECURE": False,  # TODO: HTTPS
    "JWT_COOKIE_HTTPONLY": True,
    "JWT_COOKIE_SAMESITE": "Lax",
    "JWT_BLACKLIST_ENABLED": True,
    "JWT_BLACKLIST_AFTER_ROTATION": True,
}

GRAPHQL_AUTH = {
    "LOGIN_ALLOWED_FIELDS": ["email"],
    "REGISTER_MUTATION_FIELDS": ["username", "name", "email"],
    "UPDATE_MUTATION_FIELDS": ["username", "name"],
    "ALLOW_LOGIN_NOT_VERIFIED": False,
    "USER_NODE_FILTER_FIELDS": {
        "email": ["exact"],
        "username": ["exact"],
        "is_active": ["exact"],
    },
}
