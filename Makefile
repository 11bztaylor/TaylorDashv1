# TaylorDash Makefile

.PHONY: up down ps logs health build clean test

# Default environment
ENV ?= development

# Start all services
up:
	docker-compose up -d
	@echo "TaylorDash started. Check health with: make health"

# Stop all services
down:
	docker-compose down

# Show service status
ps:
	docker-compose ps

# Show logs for specific service (usage: make logs S=backend)
logs:
ifdef S
	docker-compose logs -f $(S)
else
	docker-compose logs -f
endif

# Check health of all services
health:
	@echo "Checking service health..."
	@docker-compose ps --format "table {{.Name}}\t{{.Status}}\t{{.Health}}"

# Build services
build:
	docker-compose build

# Clean up everything (containers, volumes, networks)
clean:
	docker-compose down -v --remove-orphans
	docker system prune -f

# Run tests
test:
	cd backend && python -m pytest tests/ -v

# Validate system (run validation script)
validate:
	./ops/validate_p1.sh

# Development helpers
dev-up:
	docker-compose --profile timescale up -d

dev-logs:
	docker-compose logs -f backend postgres mosquitto

dev-shell:
	docker-compose exec backend bash

# MQTT testing
mqtt-test:
	mosquitto_pub -h localhost -p 1883 -u taylordash -P taylordash -t "tracker/events/test/test" -m '{"trace_id":"test-123","ts":"2024-01-01T00:00:00Z","kind":"test.message","idempotency_key":"test-123","payload":{"test":"data"}}'

mqtt-listen:
	mosquitto_sub -h localhost -p 1883 -u taylordash -P taylordash -t "tracker/events/#" -v

# Database helpers
db-shell:
	docker-compose exec postgres psql -U taylordash -d taylordash

db-migrate:
	docker-compose exec backend python -c "from app.database import run_migrations; import asyncio; asyncio.run(run_migrations())"