.PHONY: help up down logs shell test clean ps status

help:
	@echo "PostgreSQL + pgvector Docker Compose - Available Commands"
	@echo ""
	@echo "  make up          - Start the PostgreSQL container"
	@echo "  make down        - Stop the container (keeps data)"
	@echo "  make ps          - Show container status"
	@echo "  make logs        - View container logs"
	@echo "  make shell       - Open PostgreSQL shell (psql)"
	@echo "  make test        - Run Python test script"
	@echo "  make clean       - Stop and remove all data"
	@echo "  make restart     - Restart the container"
	@echo "  make backup      - Backup database to backup.sql"
	@echo "  make restore     - Restore from backup.sql"
	@echo ""

up:
	docker compose up -d
	@echo "✓ PostgreSQL + pgvector is starting..."
	@echo "  Waiting for health check..."
	@sleep 3
	@docker compose ps

down:
	docker compose down
	@echo "✓ Container stopped"

ps:
	docker compose ps

status:
	@docker compose ps
	@echo ""
	@echo "Port Status:"
	@lsof -i :5432 2>/dev/null || echo "Port 5432 is free"

logs:
	docker compose logs -f postgres

shell:
	docker compose exec postgres psql -U postgres -d vectordb

test:
	python test_pgvector.py

clean:
	docker compose down -v
	@echo "✓ Container and data removed"

restart:
	docker compose restart postgres
	@echo "✓ Container restarted"

backup:
	docker compose exec postgres pg_dump -U postgres vectordb > backup.sql
	@echo "✓ Database backed up to backup.sql"

restore:
	@if [ ! -f backup.sql ]; then \
		echo "✗ backup.sql not found"; \
		exit 1; \
	fi
	docker compose exec -T postgres psql -U postgres vectordb < backup.sql
	@echo "✓ Database restored from backup.sql"

install-python-deps:
	pip install -r requirements.txt

requirements:
	@echo "psycopg2-binary==2.9.9" > requirements.txt
	@echo "numpy==1.24.3" >> requirements.txt
	@echo "psycopg-binary" >> requirements.txt
	@echo "✓ requirements.txt created"

db-info:
	@docker compose exec postgres psql -U postgres -d vectordb -c "\dt"
	@echo ""
	@docker compose exec postgres psql -U postgres -d vectordb -c "SELECT count(*) as total_documents FROM documents;"

db-clear:
	docker compose exec postgres psql -U postgres -d vectordb -c "TRUNCATE documents RESTART IDENTITY;"
	@echo "✓ All documents cleared"