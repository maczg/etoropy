.PHONY: lint format typecheck test check

lint:
	uv run ruff check .

format:
	uv run ruff format --check .

typecheck:
	uv run mypy etoropy/

test:
	uv run pytest

check: lint format typecheck test