#!/bin/bash

source ./scripts/setup.sh

npm --prefix frontend run build

uvicorn backend.config.asgi:application --host 127.0.0.1 --port 8000 --lifespan=off --reload 
