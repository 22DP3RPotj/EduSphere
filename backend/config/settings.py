import environ
import dj_database_url
from pathlib import Path
from datetime import timedelta


# Initialize environment variables
env = environ.Env(
    DEBUG=(bool, False)
)

# Build paths inside the project like this: BASE_DIR / "subdir".
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# .env file path
ENV_PATH = BASE_DIR / ".env"

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# Read .env file if it exists
environ.Env.read_env(ENV_PATH)

SECRET_KEY = env("SECRET_KEY")

DEBUG = env("DEBUG")

ALLOWED_HOSTS = [
    "localhost",
    "127.0.0.1",
]

# User Authentication

AUTH_USER_MODEL = "core.User"

# Application definition

INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.staticfiles",
    "backend.core.apps.CoreConfig",
    "backend.access.apps.AccessConfig",
    "backend.room.apps.RoomConfig",
    "backend.graphql.apps.GraphQLConfig",
    "graphql_jwt.refresh_token",
    "channels",
    "corsheaders",
    "graphene_django",
    "django_cleanup.apps.CleanupConfig",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "corsheaders.middleware.CorsMiddleware",
]

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

ROOT_URLCONF = "backend.config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            BASE_DIR / "templates"
        ],
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

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'graphql_file': {
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'graphql.log',
            'formatter': 'verbose',
        },
        'root_file': {
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'general.log',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'backend.graphql.middleware': {
            'handlers': ['graphql_file'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
    'root': {
        'handlers': ['root_file'],
        'level': 'WARNING',
    },
}

ASGI_APPLICATION = "backend.config.asgi.application"

WSGI_APPLICATION = "backend.config.wsgi.application"

GRAPHENE = {
    "SCHEMA": "backend.graphql.schema.schema",
    "MIDDLEWARE": [
        "graphql_jwt.middleware.JSONWebTokenMiddleware",
        # "backend.graphql.middleware.ValidationMiddleware",
    ],
}

GRAPHQL_JWT = {
    "JWT_VERIFY_EXPIRATION": True,
    "JWT_EXPIRATION_DELTA": timedelta(minutes=10),
    "JWT_REFRESH_EXPIRATION_DELTA": timedelta(days=7),
    "JWT_COOKIE_SECURE": False,  # TODO: HTTPS
    "JWT_COOKIE_HTTPONLY": True,
    "JWT_COOKIE_SAMESITE": "Lax",
    "JWT_BLACKLIST_ENABLED": True,
    "JWT_BLACKLIST_AFTER_ROTATION": True,
    "JWT_CSRF_ROTATION": True,
}

SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax" # TODO: "Strict"

CSRF_COOKIE_HTTPONLY = False
CSRF_COOKIE_SAMESITE = "Lax" # TODO: "Strict"

CSRF_TRUSTED_ORIGINS = [
    "http://localhost",
    "http://127.0.0.1",
]

CORS_ALLOW_CREDENTIALS = True

CORS_ALLOWED_ORIGINS = [
    "http://localhost",
    "http://127.0.0.1",
]


AUTHENTICATION_BACKENDS = [
    "graphql_jwt.backends.JSONWebTokenBackend",
    "django.contrib.auth.backends.ModelBackend",
]

# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

DATABASES = {
    "default": dj_database_url.config(
        default=env("DATABASE_URL"),
        conn_max_age=60,
        conn_health_checks=True,
    )
}

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [(
                env("REDIS_HOST", default="localhost"),
                env("REDIS_PORT", default="6379")
            )],
        },
    },
}


REDIS_HOST = env("REDIS_HOST", default="localhost")
REDIS_PORT = env.int("REDIS_PORT", default=6379)
REDIS_DB = env.int("REDIS_DB", default=0)

REDIS_STREAMS = {
    'MAX_STREAM_LENGTH': 10000,
    'MESSAGE_TTL': 86400,
    'CONSUMER_TIMEOUT': 300,
}

# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


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
