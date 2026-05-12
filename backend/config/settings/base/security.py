from ..environment import env

SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"

CORS_ALLOW_CREDENTIALS = False

DEFAULT_CORS_ALLOWED_ORIGINS = [
    "http://localhost",
    "http://localhost:80",
    "http://localhost:3000",
    "http://localhost:8000",
    "http://127.0.0.1",
    "http://127.0.0.1:80",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:8000",
]

CORS_ALLOWED_ORIGINS = env.list(
    "CORS_ALLOWED_ORIGINS", default=DEFAULT_CORS_ALLOWED_ORIGINS
)

DEFAULT_ALLOWED_HOSTS = [
    "localhost",
    "127.0.0.1",
    # Docker internal hostname
    "backend",
]

ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=DEFAULT_ALLOWED_HOSTS)
