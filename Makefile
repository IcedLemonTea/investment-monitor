setup:
	python -m pip install -e ".[dev]"

test:
	pytest

lint:
	ruff check src tests

typecheck:
	mypy src

check: lint typecheck test

serve:
	python -m ibkr_monitor dashboard serve --port 8765

refresh-mock:
	python -m ibkr_monitor poll --source mock

refresh-flex:
	python -m ibkr_monitor poll --source flex

refresh-gateway:
	python -m ibkr_monitor poll --source gateway

poll-hourly:
	python -m ibkr_monitor poll-loop --source gateway --interval 3600

inspect-db:
	python scripts/inspect_db.py
