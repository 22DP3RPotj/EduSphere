from ..environment import env, BASE_DIR


LOG_THRESHOLD = env.int("LOG_THRESHOLD", default=30)

LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
        "root_file": {
            "class": "logging.handlers.TimedRotatingFileHandler",
            "filename": LOG_DIR / "general.log",
            "when": "midnight",
            "backupCount": LOG_THRESHOLD,
            "encoding": "utf-8",
            "delay": True,
            "utc": True,
            "formatter": "verbose",
        },
    },
    "root": {
        "handlers": ["console", "root_file"],
        "level": "WARNING",
    },
    "loggers": {
        "uvicorn.access": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
        "backend": {
            "handlers": ["console", "root_file"],
            "level": "INFO",
            "propagate": False,
        },
        "backend.account.tasks": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
        "backend.core.tasks": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
    },
}
