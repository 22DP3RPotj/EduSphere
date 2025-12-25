.PHONY: help setup run unit-test report clean clean-logs

help:
	@echo "EduSphere Development Commands"
	@echo "================================"
	@echo "make setup      - Initialize environment and services"
	@echo "make run        - Build frontend and run development server"
	@echo "make test       - Run unit tests"
	@echo "make report     - Run tests with coverage report"
	@echo "make clean      - Clean generated files and caches"
	@echo "make clean-logs - Clear log files"

setup:
	sudo service postgresql start; \
	sudo service nginx start; \
	mkdir -p logs; \
	mkdir -p media/avatars; \
	python manage.py collectstatic --noinput; \

run: setup
	pnpm --prefix frontend run build
	DJANGO_SETTINGS_MODULE=backend.config.settings uvicorn backend.config.asgi:application --host 127.0.0.1 --port 8000 --lifespan=off --reload

unit-test: setup
	DJANGO_SETTINGS_MODULE=backend.config.settings python manage.py test backend/core core.tests.unit

report: setup
	DJANGO_SETTINGS_MODULE=backend.config.settings coverage run --source='backend.core' -m django test backend/core/tests/unit
	coverage report --skip-empty

clean:
	find . -type f -name '*.pyc' -delete
	rm -rf .coverage

clean-logs:
	rm -rf logs/*
