.PHONY: run run-dev run-mcp run-mcp-dev test test-worker coverage ngrok tun worker

run:
	set -a && source venv/bin/activate && [ -f .env.prod ] && source .env.prod; set +a && python -m uvicorn main:app --reload

run-dev:
	set -a && source venv/bin/activate && [ -f .env.dev ] && source .env.dev; set +a && python -m uvicorn main:app --reload

run-mcp:
	@echo "🚀 Starting Aiven MCP Server..."
	@echo "This exposes your APIs as MCP tools for AI agents."
	@echo "Make sure your FastAPI server is running on http://localhost:8000"
	source venv/bin/activate && python -m mcp_server.server

run-mcp-dev:
	@echo "🚀 Starting Aiven MCP Server in development mode..."
	@echo "This exposes your APIs as MCP tools for AI agents."
	@echo "Make sure your FastAPI server is running on http://localhost:8000"
	source venv/bin/activate && python -c "import subprocess; subprocess.run(['uv', 'run', 'mcp', 'dev', 'mcp_server/server.py'])"

test:
	PYTHONPATH=. pytest --trace-config

test-worker:
	@echo "🧪 Running tests with real Celery worker..."
	@echo "⚠️  Make sure worker is running: make worker"
	@echo ""
	PYTHONPATH=. pytest tests/tasks/ --celery-worker -v

coverage:
	@echo "Running test coverage analysis..."
	@if [ "$(TARGET)" ] && [ "$(MODULE)" ]; then \
		echo "Targeted coverage - Tests: $(TARGET) → Module: $(MODULE)"; \
		PYTHONPATH=. pytest $(TARGET) --cov=$(MODULE) --cov-report=term-missing --cov-report=html:htmlcov -v; \
	elif [ "$(TARGET)" ]; then \
		echo "Broad coverage - Tests: $(TARGET) → Entire app"; \
		PYTHONPATH=. pytest $(TARGET) --cov=app --cov-report=term-missing --cov-report=html:htmlcov -v; \
	else \
		echo "Broad coverage - All tests → Entire app"; \
		PYTHONPATH=. pytest tests/ --cov=app --cov-report=term-missing --cov-report=html:htmlcov -v; \
	fi
	@if [ "$(OPEN)" = "no" ] || [ "$(OPEN)" = "false" ]; then \
		echo "HTML coverage report generated at htmlcov/index.html"; \
	else \
		echo "Opening HTML coverage report..."; \
		open htmlcov/index.html; \
	fi

worker:
	@echo "🔧 Starting Celery worker..."
	@echo "Make sure Redis is running (docker-compose up -d)"
	source venv/bin/activate && celery -A background:background_app worker --loglevel=info

ngrok:
	@echo "🌐 Starting ngrok tunnel to localhost:3000..."
	@if command -v ngrok >/dev/null 2>&1; then \
		ngrok http 3000; \
	else \
		echo "❌ ngrok not found. Install it from https://ngrok.com/download"; \
		exit 1; \
	fi
