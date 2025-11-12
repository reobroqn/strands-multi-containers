# FastAPI Agent Chat - Makefile
# Compatible with WSL/Linux environments

.PHONY: start stop restart build logs status test health shell redis ps
.DEFAULT_GOAL := help

# Variables
COMPOSE_FILE := docker-compose.yml
API_BASE := http://localhost

# Colors for output
BLUE := \033[0;34m
GREEN := \033[0;32m
YELLOW := \033[1;33m
RED := \033[0;31m
NC := \033[0m # No Color

start: ## Build and start all services
	@echo "$(BLUE)🚀 Starting FastAPI Agent Chat...$(NC)"
	@UID=$(id -u) GID=$(id -g) docker compose -f $(COMPOSE_FILE) up -d
	@echo ""
	@echo "$(GREEN)✅ Started! Access the app at http://localhost$(NC)"
	@echo "$(YELLOW)Run 'make status' to check health$(NC)"

stop: ## Stop all services
	@echo "$(BLUE)🛑 Stopping FastAPI Agent Chat...$(NC)"
	@docker compose -f $(COMPOSE_FILE) down
	@echo "$(GREEN)✅ Stopped!$(NC)"

restart: ## Restart all services
	@echo "$(BLUE)🔄 Restarting FastAPI Agent Chat...$(NC)"
	@docker compose -f $(COMPOSE_FILE) down
	@UID=$(id -u) GID=$(id -g) docker compose -f $(COMPOSE_FILE) up -d
	@echo "$(GREEN)✅ Restarted!$(NC)"

build: ## Build Docker images
	@echo "$(BLUE)🔨 Building Docker images...$(NC)"
	@UID=$(id -u) GID=$(id -g) docker compose -f $(COMPOSE_FILE) build
	@echo "$(GREEN)✅ Built!$(NC)"

ps: ## List running containers
	@UID=$(id -u) GID=$(id -g) docker compose -f $(COMPOSE_FILE) ps


logs: ## View logs from all services (follow mode)
	@echo "$(BLUE)📜 Viewing logs... (Ctrl+C to exit)$(NC)"
	@docker compose -f $(COMPOSE_FILE) logs -f

logs-backend: ## View logs from backend containers only
	@echo "$(BLUE)📜 Viewing backend logs... (Ctrl+C to exit)$(NC)"
	@docker compose -f $(COMPOSE_FILE) logs -f backend1 backend2 backend3

logs-nginx: ## View Nginx logs
	@echo "$(BLUE)📜 Viewing Nginx logs... (Ctrl+C to exit)$(NC)"
	@docker compose -f $(COMPOSE_FILE) logs -f nginx

logs-redis: ## View Redis logs
	@echo "$(BLUE)📜 Viewing Redis logs... (Ctrl+C to exit)$(NC)"
	@docker compose -f $(COMPOSE_FILE) logs -f redis

shell-backend1: ## Open shell in backend1 container
	@echo "$(BLUE)🔍 Opening shell in backend1...$(NC)"
	@docker compose -f $(COMPOSE_FILE) exec backend1 bash

shell-backend2: ## Open shell in backend2 container
	@echo "$(BLUE)🔍 Opening shell in backend2...$(NC)"
	@docker compose -f $(COMPOSE_FILE) exec backend2 bash

shell-backend3: ## Open shell in backend3 container
	@echo "$(BLUE)🔍 Opening shell in backend3...$(NC)"
	@docker compose -f $(COMPOSE_FILE) exec backend3 bash

shell-nginx: ## Open shell in nginx container
	@echo "$(BLUE)🔍 Opening shell in nginx...$(NC)"
	@docker compose -f $(COMPOSE_FILE) exec nginx bash

redis: ## Open Redis CLI
	@echo "$(BLUE)🔴 Opening Redis CLI... (Ctrl+D to exit)$(NC)"
	@docker compose -f $(COMPOSE_FILE) exec redis redis-cli

redis-monitor: ## Monitor Redis in real-time
	@echo "$(BLUE)📊 Monitoring Redis... (Ctrl+C to exit)$(NC)"
	@docker compose -f $(COMPOSE_FILE) exec redis redis-cli monitor
