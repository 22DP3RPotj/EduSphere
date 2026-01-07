# docker/backend/Dockerfile
FROM python:3.12-slim

ARG GIT_SHA=unknown
ARG APP_VERSION=unknown

WORKDIR /app

ENV GIT_SHA=${GIT_SHA}
ENV APP_VERSION=${APP_VERSION}

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    libpq-dev \
    postgresql-client \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry (recommended way)
RUN pip install --no-cache-dir pipx && \
    pipx ensurepath && \
    pipx install poetry

ENV PATH="/root/.local/bin:${PATH}"

# Copy project metadata for dependency install
COPY pyproject.toml poetry.lock* ./

# Install Python dependencies (no virtualenvs in Docker)
RUN poetry config virtualenvs.create false && \
    poetry install --no-interaction --no-ansi --no-root

# Copy full project
COPY . .

# Create runtime directories
RUN mkdir -p staticfiles media/avatars logs

# Entrypoint + default command
ENTRYPOINT ["/app/docker/backend/entrypoint.sh"]
CMD ["uvicorn", "backend.config.asgi:application", "--host", "0.0.0.0", "--port", "8000", "--lifespan", "off"]
