#!/bin/bash

source ./scripts/setup.sh

python manage.py test backend/core
