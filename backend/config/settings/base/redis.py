from ..env import env
from celery.schedules import crontab

# Redis Streams
REDIS_STREAMS = {
    "MAX_STREAM_LENGTH": 10000,
    "MESSAGE_TTL": 86400,
    "CONSUMER_TIMEOUT": 300,
}

REDIS_HOST = env("REDIS_HOST", default="localhost")
REDIS_PORT = env.int("REDIS_PORT", default=6379)
REDIS_DB = env.int("REDIS_DB", default=0)

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [
                (
                    REDIS_HOST,
                    REDIS_PORT,
                )
            ],
        },
    },
}


# Celery
CELERY_BROKER_URL = f"redis://{REDIS_HOST}:{REDIS_PORT}/1"
CELERY_RESULT_BACKEND = f"redis://{REDIS_HOST}:{REDIS_PORT}/1"
CELERY_TIMEZONE = "UTC"
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"

CELERY_BEAT_SCHEDULE = {
    "cleanup_old_audit_logs": {
        "task": "backend.core.tasks.cleanup_old_audit_logs",
        "schedule": crontab(hour=3, minute=0),
    },
    "expire_user_bans": {
        "task": "backend.account.tasks.expire_user_bans",
        "schedule": crontab(minute=0),
    },
}
