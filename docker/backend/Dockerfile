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

# Create runtime directories
RUN mkdir -p /app/staticfiles /app/media/avatars

# Create user and set permissions
RUN useradd -m -s /usr/sbin/nologin appuser && \
    chown -R appuser:appuser /app

RUN chmod +x /app/docker/backend/entrypoint.sh

USER appuser

ENTRYPOINT ["/app/docker/backend/entrypoint.sh"]
CMD ["python", "-m", "backend"]
