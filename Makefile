.PHONY: install backend frontend test lint format clean

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
	cd frontend && npm run typecheck

lint:
	cd backend && ruff check app tests eval
	cd frontend && npm run lint

format:
	cd backend && ruff format app tests eval

clean:
	rm -rf backend/.pytest_cache backend/.ruff_cache backend/pulseresolve.db
	rm -rf frontend/.next frontend/node_modules
