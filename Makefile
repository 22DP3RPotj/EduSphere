.PHONY: all help \
        setup run \
        unit-test integration-test test coverage report \
        typecheck check fix format-check format lint ci \
        up down ps logs shell migrate restart \
        deploy rollback cert-init cert-renew \
        clean clean-migrations

PY := poetry run python
PX := poetry run
DC := docker compose --env-file docker.env

# Evaluated once at Make startup — used for local dev builds
GIT_SHA     := $(shell git rev-parse --short HEAD 2>/dev/null || echo unknown)
APP_VERSION := $(shell git describe --tags --dirty --always 2>/dev/null || echo unknown)

export DJANGO_SETTINGS_MODULE=backend.config.settings
export GIT_SHA
export APP_VERSION

all: help

help:
	@echo "EduSphere Commands"
	@echo "======================================================================="
	@echo "Development"
	@echo "  setup                - Initialize local services and static files"
	@echo "  run                  - Build frontend and start development server"
	@echo ""
	@echo "Testing"
	@echo "  test                 - Run all tests"
	@echo "  unit-test            - Run unit tests only"
	@echo "  integration-test     - Run integration tests only"
	@echo "  coverage             - Run tests with coverage measurement"
	@echo "  report               - Print coverage report (runs coverage if needed)"
	@echo ""
	@echo "Code Quality"
	@echo "  typecheck            - Run mypy type checks"
	@echo "  check                - Run ruff linter checks"
	@echo "  fix                  - Auto-fix ruff lint issues"
	@echo "  format               - Format code with ruff"
	@echo "  format-check         - Check formatting without applying changes"
	@echo "  lint                 - Run all linters (ruff + eslint)"
	@echo "  ci                   - Full CI suite: typecheck + lint + test"
	@echo ""
	@echo "Docker"
	@echo "  up                   - Build images and start all services"
	@echo "  down                 - Stop and remove containers (volumes preserved)"
	@echo "  ps                   - Show running service status"
	@echo "  logs                 - Follow logs for all services (tail=100)"
	@echo "  shell                - Open a shell in the backend container"
	@echo "  migrate              - Run database migrations and collectstatic"
	@echo "  restart SERVICE=x    - Restart a specific service"
	@echo ""
	@echo "Deployment  (run on the production server)"
	@echo "  deploy  TAG=v1.0.0   - Pull and deploy a tagged release"
	@echo "  rollback TAG=v1.0.0  - Roll back to a previously deployed tag"
	@echo "  cert-init            - Issue Let's Encrypt cert (run once after first deploy)"
	@echo "  cert-renew           - Renew certificates and reload nginx"
	@echo ""
	@echo "Cleanup"
	@echo "  clean                - Remove .pyc files and .coverage"
	@echo "  clean-migrations     - Remove all migration files (keep __init__.py)"

# ---------------------------------------------------------------------------
# Development
# ---------------------------------------------------------------------------

setup:
	sudo service postgresql start
	sudo service nginx start
	mkdir -p media/avatars
	$(PY) manage.py collectstatic --noinput

run: setup
	pnpm --prefix frontend run build
	$(PY) -m backend

# ---------------------------------------------------------------------------
# Testing
# ---------------------------------------------------------------------------

unit-test:
	$(PX) pytest -q -m unit

integration-test: setup
	$(PX) pytest -q -m integration

test:
	$(PX) pytest -q

coverage:
	$(PX) coverage run --source='backend' -m pytest -q

report:
	if [ ! -f .coverage ]; then $(MAKE) coverage; fi
	$(PX) coverage report --skip-empty

# ---------------------------------------------------------------------------
# Code Quality
# ---------------------------------------------------------------------------

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

lint:
	$(PX) ruff check backend
	$(PX) ruff format --check backend
	pnpm --prefix frontend exec eslint .

ci: typecheck lint test

# ---------------------------------------------------------------------------
# Docker
# ---------------------------------------------------------------------------

up:
	$(DC) up -d --build

down:
	$(DC) down

ps:
	$(DC) ps

logs:
	$(DC) logs -f --tail=100

shell:
	$(DC) exec backend bash

migrate:
	$(DC) run --rm migrate

restart:
	@if [ -z "$(SERVICE)" ]; then \
		echo "Error: SERVICE is required. Usage: make restart SERVICE=backend"; \
		exit 1; \
	fi
	$(DC) restart $(SERVICE)

# ---------------------------------------------------------------------------
# Deployment  (intended to run on the production server)
# ---------------------------------------------------------------------------

deploy rollback:
	@if [ -z "$(TAG)" ]; then \
		echo "Error: TAG is required. Usage: make $@ TAG=v1.0.0"; \
		exit 1; \
	fi
	git fetch origin tag $(TAG)
	git -c advice.detachedHead=false checkout tags/$(TAG)
	APP_VERSION=$(TAG) $(DC) pull backend nginx
	APP_VERSION=$(TAG) $(DC) run --rm migrate
	APP_VERSION=$(TAG) $(DC) up -d
	docker image prune -f

# Obtain a Let's Encrypt certificate via Cloudflare DNS-01 challenge.
# Run once before starting nginx. Requires secrets/cf.ini, NGINX_HOST and
# CERTBOT_EMAIL in docker.env. nginx does not need to be running.
cert-init:
	mkdir -p certbot/conf
	$(DC) run --rm certbot certonly \
		--dns-cloudflare \
		--dns-cloudflare-credentials /run/secrets/cf.ini \
		--email $$(grep '^CERTBOT_EMAIL=' docker.env | cut -d= -f2) \
		--agree-tos \
		--no-eff-email \
		-d $$(grep '^NGINX_HOST=' docker.env | cut -d= -f2)

# Renew certificates (run from cron weekly, e.g.):
#   0 3 * * 1 cd /opt/edusphere && make cert-renew >> /var/log/certbot-renew.log 2>&1
cert-renew:
	$(DC) run --rm certbot renew
	$(DC) exec nginx nginx -s reload

# ---------------------------------------------------------------------------
# Cleanup
# ---------------------------------------------------------------------------

clean:
	find . -type f -name '*.pyc' -delete
	rm -rf .coverage

clean-migrations:
	find backend -path "*/migrations/*.py" -not -name "__init__.py" -delete
