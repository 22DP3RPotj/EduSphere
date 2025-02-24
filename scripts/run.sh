#!/bin/bash

# Run the uvicorn server
uvicorn backend.config.asgi:application --host 127.0.0.1 --port 8000 --lifespan=off --reload &
# Run the npm dev server
npm --prefix frontend run dev &

wait
