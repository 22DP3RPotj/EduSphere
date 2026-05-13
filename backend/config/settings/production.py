from .environment import env

DEBUG = False

# Django needs to know requests arrive over HTTPS even though nginx is the SSL terminator.
# Do NOT set SECURE_SSL_REDIRECT — nginx handles the HTTP→HTTPS redirect; Django only
# ever sees internal HTTP traffic from nginx and would loop if it tried to redirect too.
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

EMAIL_BACKEND = "anymail.backends.resend.EmailBackend"

ANYMAIL = {
    "RESEND_API_KEY": env("RESEND_API_KEY"),
}

DEFAULT_FROM_EMAIL = env("FROM_EMAIL")
