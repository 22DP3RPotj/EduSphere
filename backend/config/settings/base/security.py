from ..environment import env

# TODO: When moving to production with HTTPS
# SECURE_SETTINGS = {
# "SECURE_SSL_REDIRECT": True,  # Redirect all HTTP to HTTPS
# "SECURE_HSTS_SECONDS": 31536000,  # 1 year
# "SECURE_HSTS_INCLUDE_SUBDOMAINS": True,
# "SECURE_HSTS_PRELOAD": True,
# "SECURE_CONTENT_TYPE_NOSNIFF": True,
# "SECURE_BROWSER_XSS_FILTER": True,
# "SECURE_PROXY_SSL_HEADER": ("HTTP_X_FORWARDED_PROTO", "https"),
# }

SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"  # TODO: "Strict"

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
