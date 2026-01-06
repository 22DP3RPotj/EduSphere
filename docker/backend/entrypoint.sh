#!/bin/sh
set -e
until pg_isready -h "$POSTGRES_HOST" -U "$POSTGRES_USER" -d "$POSTGRES_DB"; do sleep 1; done

if ! python manage.py migrate --check; then
    python manage.py migrate --noinput
fi

exec "$@"
