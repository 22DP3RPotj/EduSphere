#!/bin/bash


if [ -z "$DJANGO_SETTINGS_MODULE" ]; then
  export DJANGO_SETTINGS_MODULE=backend.config.settings

  sudo service postgresql start
  sudo service nginx start

  mkdir -p logs
  mkdir -p media/avatars

  python manage.py collectstatic --noinput
fi
