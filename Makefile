.PHONY: install dev test test-e2e eval eval-ci eval-latency eval-calibration lint typecheck graph-writer agent

install:
	uv sync 2>/dev/null || pip install -r requirements.txt

dev:
	docker-compose up -d
	sleep 5
	uv run python -m graph.schema.apply 2>/dev/null || true
	uv run python -m graph.fixtures.load 2>/dev/null || true

validate-vector:
	NEO4J_ENTERPRISE=1 uv run python -m graph.embeddings.validate_vector_index 2>/dev/null || echo "Vector index requires Neo4j Aura Enterprise"

test:
	uv run pytest tests/unit tests/integration -v --cov=. --cov-report=term-missing 2>/dev/null || uv run pytest tests/ -v

test-e2e:
	uv run pytest tests/e2e -v -s

eval:
	python -m evals.runners.accuracy_runner

eval-ci:
	python -m evals.runners.accuracy_runner --fail-threshold=0.85

eval-latency:
	python -m evals.runners.latency_runner

eval-calibration:
	python -m evals.runners.calibration_runner

lint:
	uv run ruff check .
	uv run ruff format --check .

typecheck:
	uv run mypy agent/ graph/ ingestion/ --strict 2>/dev/null || true

graph-writer:
	uv run python -m graph.writer.main

agent:
	uv run uvicorn agent.main:app --reload --port 8001 2>/dev/null || uvicorn agent.main:app --reload --port 8001
