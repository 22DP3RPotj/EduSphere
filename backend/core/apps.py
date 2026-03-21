from typing import Optional

import redis.asyncio as aioredis
from django.conf import settings
from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "backend.core"
    label = "core"
    verbose_name = "Core"

    # Shared Redis client for the whole app, lazily initialized on first use.
    _redis_client: Optional[aioredis.Redis] = None

    @classmethod
    def get_redis_client(cls) -> aioredis.Redis:
        if cls._redis_client is None:
            cls._redis_client = aioredis.Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                db=settings.REDIS_DB,
                decode_responses=True,
                max_connections=20,
                socket_timeout=5.0,
            )
        return cls._redis_client
