#!/bin/sh
set -e

chown -R appuser:appuser /app/staticfiles /app/media

exec gosu appuser "$@"
