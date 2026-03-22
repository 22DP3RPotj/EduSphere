from .environment import env

DEBUG = False

GIT_SHA = env("GIT_SHA")
APP_VERSION = env("APP_VERSION")

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.sendgrid.net"
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = "apikey"
EMAIL_HOST_PASSWORD = env("SENDGRID_API_KEY")
DEFAULT_FROM_EMAIL = env("FROM_EMAIL")
