.PHONY: install backend frontend test lint browser-test format clean

install:
	python -m venv .venv
	. .venv/bin/activate && pip install -e "./backend[dev]"
	cd frontend && npm install

backend:
	cd backend && uvicorn app.main:app --reload --port 8000

frontend:
	cd frontend && npm run dev

test:
	cd backend && pytest -q
	cd backend && python -m eval.run_evaluation
	cd frontend && npm run typecheck

lint:
	cd backend && ruff check app tests eval
	cd backend && ruff format --check app tests eval
	cd frontend && npm run lint

browser-test:
	cd frontend && npm run test:e2e

format:
	cd backend && ruff format app tests eval

clean:
	rm -rf backend/.pytest_cache backend/.ruff_cache backend/pulseresolve.db
	rm -rf frontend/.next frontend/node_modules
