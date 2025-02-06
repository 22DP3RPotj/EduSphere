import environ

env = environ.Env()

if env('ENVIRONMENT') == 'production':
    from .production import *
else:
    from .development import *
