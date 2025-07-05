.PHONY: run run-dev

run:
	set -a && source venv/bin/activate && [ -f .env.prod ] && source .env.prod; set +a && python -m uvicorn main:app --reload

run-dev:
	set -a && source venv/bin/activate && [ -f .env.dev ] && source .env.dev; set +a && python -m uvicorn main:app --reload

test:
	PYTHONPATH=. pytest --trace-config
