import uvicorn
from django.conf import settings


def main():
    uvicorn.run(
        "backend.config.asgi:application",
        host=settings.SERVER_HOST,
        port=settings.SERVER_PORT,
        reload=settings.DEBUG,
        lifespan="auto",
        log_level="warning",
    )


if __name__ == "__main__":
    main()
