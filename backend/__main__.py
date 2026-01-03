import uvicorn


def main():
    uvicorn.run(
        "backend.config.asgi:application",
        port=8000,
        reload=True, 
        lifespan="off",
    )

if __name__ == "__main__":
    main()