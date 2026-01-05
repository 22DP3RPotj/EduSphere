.PHONY: help setup run unit-test report clean clean-logs clean-migrations typecheck lint format docker-compose-up docker-compose-down

PY = poetry run python
PX = poetry run

export DJANGO_SETTINGS_MODULE=backend.config.settings

all: help

help:
	@echo "EduSphere Development Commands"
	@echo "================================"
	@echo "make setup      - Initialize environment and services"
	@echo "make run        - Build frontend and run development server"
	@echo "make test       - Run all tests (pytest)"
	@echo "make report     - Run tests with coverage report"
	@echo "make clean      - Clean generated files and caches"
	@echo "make clean-logs - Clear log files"
	@echo "make clean-migrations - Remove Django migration files"
	@echo "make typecheck  - Run mypy type checks"
	@echo "make lint       - Run ruff linter checks"
	@echo "make docker-compose-up   - Start services with Docker Compose"
	@echo "make docker-compose-down - Stop services with Docker Compose"

setup:
	sudo service postgresql start; \
	sudo service nginx start; \
	mkdir -p logs; \
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

lint:
	$(PX) ruff check backend

format:
	$(PX) ruff format --check backend

clean:
	find . -type f -name '*.pyc' -delete
	rm -rf .coverage

clean-logs:
	rm -rf logs/*

clean-migrations:
	find backend -path "*/migrations/*.py" -not -name "__init__.py" -delete

docker-compose-up:
	docker-compose --env-file ./docker.env up -d --build

docker-compose-down:
	docker-compose --env-file ./docker.env down -v
