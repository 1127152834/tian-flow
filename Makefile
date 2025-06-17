.PHONY: lint format install-dev serve test coverage help redis celery worker server dev stop status migrate test-text2sql test-basic test-resource-discovery celery-monitor celery-status celery-tasks

# Default target
help:
	@echo "🦌 DeerFlow Development Commands"
	@echo "================================="
	@echo ""
	@echo "📦 Setup Commands:"
	@echo "  install-dev  - Install development dependencies"
	@echo "  migrate      - Run database migrations"
	@echo ""
	@echo "🚀 Development Commands:"
	@echo "  dev          - Start all services (Redis + Celery + Server)"
	@echo "  serve        - Start FastAPI server only"
	@echo "  server       - Start FastAPI server (alias for serve)"
	@echo "  redis        - Start Redis server"
	@echo "  celery       - Start Celery worker"
	@echo "  worker       - Start Celery worker (alias for celery)"
	@echo ""
	@echo "🧪 Testing Commands:"
	@echo "  test                   - Run pytest tests"
	@echo "  coverage               - Run tests with coverage"
	@echo "  test-text2sql          - Test Text2SQL system"
	@echo "  test-basic             - Test basic Text2SQL functionality"
	@echo "  test-resource-discovery - Test Resource Discovery system"
	@echo ""
	@echo "📊 Celery Commands:"
	@echo "  celery-monitor         - Start Celery Flower monitoring"
	@echo "  celery-status          - Show Celery worker status"
	@echo "  celery-tasks           - List available Celery tasks"
	@echo ""
	@echo "🛠️  Utility Commands:"
	@echo "  format                 - Format code with black"
	@echo "  lint                   - Check code formatting"
	@echo "  stop                   - Stop all services"
	@echo "  status                 - Show service status"
	@echo ""

install-dev:
	uv pip install -e ".[dev]" && uv pip install -e ".[test]"

format:
	uv run black --preview .

lint:
	uv run black --check .

serve:
	uv run uvicorn src.app:app --host 0.0.0.0 --port 8000 --reload

server: serve

test:
	uv run pytest tests/

langgraph-dev:
	uvx --refresh --from "langgraph-cli[inmem]" --with-editable . --python 3.12 langgraph dev --allow-blocking

coverage:
	uv run pytest --cov=src tests/ --cov-report=term-missing --cov-report=xml

# Text2SQL specific commands
migrate:
	@echo "🗄️  Running database migrations..."
	python run_migration.py src/database/migrations/001_create_database_management_schema.sql
	python run_migration.py src/database/migrations/002_create_text2sql_schema.sql
	@echo "✅ Database migrations completed"

redis:
	@echo "🔴 Starting Redis server on port 6380..."
	redis-server --port 6380

celery:
	@echo "⚡ Starting Celery worker for all tasks..."
	@echo "📋 Task modules: Text2SQL, Resource Discovery"
	@echo "📋 Queues: celery, text2sql, resource_discovery, database, cleanup"
	celery -A src.celery_app worker --loglevel=info --concurrency=4 --queues=celery,text2sql,resource_discovery,database,cleanup

worker: celery

dev:
	@echo "🚀 Starting all services for development..."
	@echo "Starting Redis in background..."
	@redis-server --port 6380 --daemonize yes
	@sleep 2
	@echo "Starting Celery worker for all tasks in background..."
	@celery -A src.celery_app worker --loglevel=info --concurrency=4 --detach --queues=celery,text2sql,resource_discovery,database,cleanup
	@sleep 2
	@echo "Starting FastAPI server..."
	@echo "📝 Services:"
	@echo "   - Redis: localhost:6380"
	@echo "   - Celery: Background worker (Text2SQL + Resource Discovery)"
	@echo "   - FastAPI: http://localhost:8000"
	@echo "   - API Docs: http://localhost:8000/docs"
	@echo "   - Text2SQL API: http://localhost:8000/api/text2sql"
	@echo "   - Resource Discovery API: http://localhost:8000/api/resource-discovery"
	uv run uvicorn src.app:app --host 0.0.0.0 --port 8000 --reload

stop:
	@echo "🛑 Stopping all services..."
	@pkill -f "redis-server.*6380" || true
	@pkill -f "celery.*src.celery_app" || true
	@pkill -f "uvicorn.*src.app" || true
	@echo "✅ All services stopped"

status:
	@echo "📊 Service Status:"
	@echo "=================="
	@echo -n "Redis (6380): " && (redis-cli -p 6380 ping > /dev/null 2>&1 && echo "✅ Running" || echo "❌ Stopped")
	@echo -n "FastAPI (8000): " && (curl -s http://localhost:8000/api/text2sql/health > /dev/null 2>&1 && echo "✅ Running" || echo "❌ Stopped")
	@echo -n "Celery Worker: " && (pgrep -f "celery.*worker" > /dev/null && echo "✅ Running" || echo "❌ Stopped")

test-text2sql:
	@echo "🧪 Testing Text2SQL system..."
	python test_text2sql_system.py

test-basic:
	@echo "🧪 Testing basic Text2SQL functionality..."
	python test_text2sql_basic.py

test-resource-discovery:
	@echo "🧪 Testing Resource Discovery system..."
	python test_resource_discovery_complete.py

celery-monitor:
	@echo "📊 Starting Celery monitoring..."
	celery -A src.celery_app flower --port=5555

celery-status:
	@echo "📊 Celery Worker Status:"
	@echo "======================="
	celery -A src.celery_app status

celery-tasks:
	@echo "📋 Available Celery Tasks:"
	@echo "=========================="
	celery -A src.celery_app inspect registered
