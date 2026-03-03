FROM python:3.12-slim

ARG GIT_SHA=unknown
ARG APP_VERSION=unknown

WORKDIR /app

ENV GIT_SHA=${GIT_SHA}
ENV APP_VERSION=${APP_VERSION}

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    libpq-dev \
    postgresql-client \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pipx && \
    pipx ensurepath && \
    pipx install poetry

ENV PATH="/root/.local/bin:${PATH}"

COPY pyproject.toml poetry.lock* ./

RUN poetry config virtualenvs.create false && \
    poetry install --no-interaction --no-ansi --no-root

COPY . .

# Create runtime directories, user and set permissions
RUN mkdir -p /app/staticfiles /app/media/avatars && \
    useradd -m appuser && \
    chown -R appuser:appuser /app && \
    chmod -R 775 /app/media

USER appuser

ENTRYPOINT ["/app/docker/backend/entrypoint.sh"]
CMD ["python", "-m", "backend"]
