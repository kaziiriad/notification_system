# Makefile for Notification System Docker operations

# Variables
<<<<<<< HEAD
COMPOSE_FILE = docker/docker-compose.yml
=======
COMPOSE_FILE = docker-compose.yml
>>>>>>> a1ecdf7b4d1c4a83234c658db78c8214db5dc0f2
PROJECT_NAME = notification-system

# Colors for output
RED = \033[0;31m
GREEN = \033[0;32m
YELLOW = \033[1;33m
NC = \033[0m # No Color

.PHONY: help build up down restart logs shell migrate test clean

# Default target
help: ## Show this help message
	@echo "$(GREEN)Notification System Docker Commands$(NC)"
	@echo "======================================"
<<<<<<< HEAD
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "$(YELLOW)%-15s$(NC) %s\n", $1, $2}' $(MAKEFILE_LIST)
=======
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "$(YELLOW)%-15s$(NC) %s\n", $$1, $$2}' $(MAKEFILE_LIST)
>>>>>>> a1ecdf7b4d1c4a83234c658db78c8214db5dc0f2

build: ## Build all Docker images
	@echo "$(GREEN)Building Docker images...$(NC)"
	docker-compose -f $(COMPOSE_FILE) build

up: ## Start all services
	@echo "$(GREEN)Starting all services...$(NC)"
	docker-compose -f $(COMPOSE_FILE) up -d
	@echo "$(GREEN)Services started! API available at http://localhost:8000$(NC)"

down: ## Stop all services
	@echo "$(YELLOW)Stopping all services...$(NC)"
	docker-compose -f $(COMPOSE_FILE) down

restart: down up ## Restart all services

logs: ## Show logs for all services
	docker-compose -f $(COMPOSE_FILE) logs -f

logs-app: ## Show logs for app service only
	docker-compose -f $(COMPOSE_FILE) logs -f app

logs-db: ## Show logs for database service only
	docker-compose -f $(COMPOSE_FILE) logs -f db

shell: ## Open shell in app container
	docker-compose -f $(COMPOSE_FILE) exec app bash

shell-db: ## Open PostgreSQL shell
	docker-compose -f $(COMPOSE_FILE) exec db psql -U postgres -d notification_system

migrate: ## Run database migrations
	@echo "$(GREEN)Running database migrations...$(NC)"
<<<<<<< HEAD
	docker-compose -f $(COMPOSE_FILE) run --rm app sh -c "cd migration && alembic upgrade head"

migrate-create: ## Create a new migration (usage: make migrate-create MESSAGE="your message")
	@echo "$(GREEN)Creating new migration...$(NC)"
	docker-compose -f $(COMPOSE_FILE) run --rm app sh -c "cd migration && alembic revision --autogenerate -m '$(MESSAGE)'"
=======
	docker-compose -f $(COMPOSE_FILE) run --rm migrate

migrate-create: ## Create a new migration (usage: make migrate-create MESSAGE="your message")
	@echo "$(GREEN)Creating new migration...$(NC)"
	docker-compose -f $(COMPOSE_FILE) run --rm app sh -c "cd /app/migrations && python migrate.py create '$(MESSAGE)'"
>>>>>>> a1ecdf7b4d1c4a83234c658db78c8214db5dc0f2

test: ## Run tests
	@echo "$(GREEN)Running tests...$(NC)"
	docker-compose -f $(COMPOSE_FILE) run --rm app pytest

dev: ## Start in development mode with hot reload
	@echo "$(GREEN)Starting in development mode...$(NC)"
	docker-compose -f $(COMPOSE_FILE) -f docker-compose.dev.yml up

prod: ## Start in production mode
	@echo "$(GREEN)Starting in production mode...$(NC)"
	docker-compose -f $(COMPOSE_FILE) -f docker-compose.prod.yml up -d

clean: ## Clean up Docker resources
	@echo "$(YELLOW)Cleaning up Docker resources...$(NC)"
	docker-compose -f $(COMPOSE_FILE) down -v --remove-orphans
	docker system prune -f

clean-all: ## Clean up everything including images
	@echo "$(RED)Cleaning up everything...$(NC)"
	docker-compose -f $(COMPOSE_FILE) down -v --remove-orphans --rmi all
	docker system prune -af

status: ## Show status of all services
	@echo "$(GREEN)Service Status:$(NC)"
	docker-compose -f $(COMPOSE_FILE) ps

health: ## Check health of all services
	@echo "$(GREEN)Health Check:$(NC)"
	@curl -f http://localhost:8000/health || echo "$(RED)API is not healthy$(NC)"

backup-db: ## Backup database
	@echo "$(GREEN)Creating database backup...$(NC)"
	docker-compose -f $(COMPOSE_FILE) exec db pg_dump -U postgres notification_system > backup_$(shell date +%Y%m%d_%H%M%S).sql

restore-db: ## Restore database (usage: make restore-db FILE=backup.sql)
	@echo "$(GREEN)Restoring database from $(FILE)...$(NC)"
	docker-compose -f $(COMPOSE_FILE) exec -T db psql -U postgres notification_system < $(FILE)

setup: ## Initial setup - build, start services, and run migrations
	@echo "$(GREEN)Setting up the project...$(NC)"
	make build
	make up
	sleep 10
	make migrate
<<<<<<< HEAD
	@echo "$(GREEN)Setup complete! API available at http://localhost:8000/docs$(NC)"
	
=======
	@echo "$(GREEN)Setup complete! API available at http://localhost:8000/docs$(NC)"
>>>>>>> a1ecdf7b4d1c4a83234c658db78c8214db5dc0f2
