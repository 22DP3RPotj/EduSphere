.PHONY: help setup run unit-test integration-test test coverage report clean clean-migrations typecheck check fix format format-check docker-compose-build docker-compose-remove

PY = poetry run python
PX = poetry run
DJANGO = $(PY) manage.py
DC = docker compose --env-file docker.env

export DJANGO_SETTINGS_MODULE=backend.config.settings

all: help

help:
	@echo "EduSphere Development Commands"
	@echo "====================================================================="
	@echo "setup                  - Initialize environment and services"
	@echo "run                    - Build frontend and run development server"
	@echo "test                   - Run all tests (pytest)"
	@echo "unit-test              - Run unit tests only"
	@echo "integration-test       - Run integration tests only"
	@echo "coverage               - Run tests with coverage measurement"
	@echo "report                 - Run tests with coverage report"
	@echo "clean                  - Clean generated files and caches"
	@echo "clean-migrations       - Remove Django migration files"
	@echo "typecheck              - Run mypy type checks"
	@echo "check                  - Run ruff linter checks"
	@echo "fix                    - Run ruff to fix issues"
	@echo "format-check           - Check code formatting with ruff"
	@echo "format                 - Format code with ruff"
	@echo "docker-compose-build   - Build and start services with Docker Compose"
	@echo "docker-compose-remove  - Stop and remove services with Docker Compose"

setup:
	sudo service postgresql start; \
	sudo service nginx start; \
	mkdir -p media/avatars; \
	$(PY) manage.py collectstatic --noinput; \

run: setup
	pnpm --prefix frontend run build
	$(PY) -m backend

unit-test:
	$(PX) pytest -q -m unit

integration-test: setup
	$(PX) pytest -q -m integration

test:
	$(PX) pytest -q

coverage:
	$(PX) coverage run --source='backend' -m pytest -q

report:
	if [ ! -f .coverage ]; then \
		$(MAKE) coverage; \
	fi
	$(PX) coverage report --skip-empty


typecheck:
	$(PX) mypy backend

check:
	$(PX) ruff check backend

fix:
	$(PX) ruff check --fix backend

format-check:
	$(PX) ruff format --check backend

format:
	$(PX) ruff format backend

clean:
	find . -type f -name '*.pyc' -delete
	rm -rf .coverage

clean-migrations:
	find backend -path "*/migrations/*.py" -not -name "__init__.py" -delete

docker-compose-build:
	GIT_SHA=$$(git rev-parse --short HEAD 2>/dev/null || echo unknown) \
	APP_VERSION=$$(git describe --tags --dirty --always 2>/dev/null || echo unknown) \
	$(DC) up -d --build

docker-compose-remove:
	$(DC) down -v
