import uvicorn
from django.conf import settings


def main():
    uvicorn.run(
        "backend.config.asgi:application",
        port=8000,
        reload=settings.DEBUG,
        lifespan="off",
    )


if __name__ == "__main__":
    main()
