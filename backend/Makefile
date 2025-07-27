.PHONY: run run-dev test coverage

run:
	set -a && source venv/bin/activate && [ -f .env.prod ] && source .env.prod; set +a && python -m uvicorn main:app --reload

run-dev:
	set -a && source venv/bin/activate && [ -f .env.dev ] && source .env.dev; set +a && python -m uvicorn main:app --reload

test:
	PYTHONPATH=. pytest --trace-config

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
