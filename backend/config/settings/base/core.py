import dj_database_url
from ..environment import env, BASE_DIR

SECRET_KEY = env("SECRET_KEY")

DEBUG = False

GIT_SHA = env("GIT_SHA", default="unknown")
APP_VERSION = env("APP_VERSION", default="unknown")

# Application definition
INSTALLED_APPS = [
    # Default Django apps
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.staticfiles",
    # Custom apps
    "backend.account.apps.AccountConfig",
    "backend.core.apps.CoreConfig",
    "backend.room.apps.RoomConfig",
    "backend.messaging.apps.MessagingConfig",
    "backend.access.apps.AccessConfig",
    "backend.moderation.apps.ModerationConfig",
    "backend.invite.apps.InviteConfig",
    "backend.graphql.apps.GraphQLConfig",
    "backend.infra.apps.InfraConfig",
    # Third-party apps
    "graphql_auth",
    "graphql_jwt.refresh_token.apps.RefreshTokenConfig",
    "graphene_django",
    "channels.apps.ChannelsConfig",
    "corsheaders.apps.CorsHeadersAppConfig",
    "pgtrigger",
    "pghistory",
    "rules.apps.AutodiscoverRulesConfig",
    "django_cleanup.apps.CleanupConfig",
    "django_celery_beat",
    "django_prometheus",
    "django_filters",
]

try:
    import django_extensions as _  # noqa

    INSTALLED_APPS += ["django_extensions"]
except ImportError:
    pass

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django_prometheus.middleware.PrometheusBeforeMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "corsheaders.middleware.CorsMiddleware",
]

MIDDLEWARE += ["django_prometheus.middleware.PrometheusAfterMiddleware"]

# Audit log
AUDIT_LOG_RETENTION_DAYS = env.int("AUDIT_LOG_RETENTION_DAYS", default=90)
AUDIT_LOG_BATCH_SIZE = env.int("AUDIT_LOG_BATCH_SIZE", default=2000)

AUDIT_LOGGING_ENABLED = env.bool("AUDIT_LOGGING_ENABLED", default=True)

if AUDIT_LOGGING_ENABLED:
    MIDDLEWARE += ["backend.core.middleware.PgHistoryMiddleware"]

ROOT_URLCONF = "backend.config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

ASGI_APPLICATION = "backend.config.asgi.application"

WSGI_APPLICATION = "backend.config.wsgi.application"

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

DATABASES = {
    "default": dj_database_url.config(
        default=env("DATABASE_URL"),
        conn_max_age=60,
        conn_health_checks=True,
    )
}

# Server
SERVER_PORT = env.int("SERVER_PORT", default=8000)
SERVER_HOST = env("SERVER_HOST", default="127.0.0.1")

# Messaging
MAX_MESSAGES_PER_SEC = 0

# File upload
MAX_FILE_SIZE_MB = 10


# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = "/static/"

# STATICFILES_DIRS = [
#     BASE_DIR / "static",
# ]

STATIC_ROOT = BASE_DIR / "staticfiles"

# Media files (User avatar)

MEDIA_URL = "/media/"

MEDIA_ROOT = BASE_DIR / "media"

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
