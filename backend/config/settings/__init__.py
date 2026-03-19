from .env import env

from .base import *  # noqa F401, F403

DJANGO_ENV = env("DJANGO_ENV").lower()

match DJANGO_ENV:
    case "production":
        from .production import *  # noqa F401, F403
    case "staging":
        from .staging import *  # noqa F401, F403
    case "development":
        from .development import *  # noqa F401, F403
    case _:
        raise ValueError(f"Invalid DJANGO_ENV: {DJANGO_ENV}")
