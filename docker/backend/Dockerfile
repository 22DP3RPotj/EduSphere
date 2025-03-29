FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    libpq-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install uvicorn gunicorn psycopg2

# Copy project
COPY . .

# Create directories if they don't exist
RUN mkdir -p staticfiles media

# Command to run the server
ENTRYPOINT ["uvicorn", "backend.config.asgi:application"]
CMD ["--host", "0.0.0.0", "--port", "8000", "--lifespan", "off"]
