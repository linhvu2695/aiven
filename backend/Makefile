.PHONY: run

run:
	source venv/bin/activate && python -m uvicorn main:app --reload

test:
	PYTHONPATH=. pytest --trace-config
