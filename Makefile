# Makefile for messenger backend infrastructure management

# Variables
DOCKER_COMPOSE = docker-compose
POETRY_RUN = poetry run

# Default target
.PHONY: help
help:
	@echo "Available commands:"
	@echo "  make up          - Start main infrastructure"
	@echo "  make down        - Stop main infrastructure and remove volumes"
	@echo "  make logs        - View main infrastructure logs"
	@echo "  make status      - Check status of main infrastructure"
	@echo "  make restart     - Restart main infrastructure"
	@echo ""
	@echo "  make migrate-up  - Run migrations on main database"
	@echo "  make migrate-down - Rollback last migration on main database"
	@echo ""
	@echo "  make lint        - Run code linting"
	@echo "  make typecheck   - Run static type checking with mypy"
	@echo "  make format      - Format code"
	@echo "  make test        - Run tests"
	@echo "  make test-coverage - Run tests with coverage"

# Infrastructure targets
.PHONY: up
up:
	$(DOCKER_COMPOSE) up -d

.PHONY: down
down:
	$(DOCKER_COMPOSE) down -v

.PHONY: logs
logs:
	$(DOCKER_COMPOSE) logs -f

.PHONY: status
status:
	$(DOCKER_COMPOSE) ps

.PHONY: restart
restart:
	$(DOCKER_COMPOSE) restart

# Migration targets
.PHONY: migrate-up
migrate-up:
	$(POETRY_RUN) alembic upgrade head

.PHONY: migrate-down
migrate-down:
	$(POETRY_RUN) alembic downgrade -1

# Development targets
.PHONY: lint
lint:
	$(POETRY_RUN) ruff check .
	$(POETRY_RUN) ruff format --check .

.PHONY: typecheck
typecheck:
	$(POETRY_RUN) mypy src/

.PHONY: format
format:
	$(POETRY_RUN) ruff format .

.PHONY: test
test:
	$(POETRY_RUN) pytest tests/ -v

.PHONY: test-coverage
test-coverage:
	$(POETRY_RUN) pytest tests/ -v --cov=src --cov-report=term-missing