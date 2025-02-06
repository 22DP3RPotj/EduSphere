from .base import *

STATICFILES_STORAGE = 'servestatic.storage.CompressedManifestStaticFilesStorage'

MIDDLEWARE += 'servestatic.middleware.ServeStaticMiddleware'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels.layers.InMemoryChannelLayer',
    }
}