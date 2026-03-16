# Rowan

Rowan is a gardening assistant that combines:
- ChromaDB vector search for semantic retrieval
- Ollama (Mistral) for query-to-filter extraction
- Metadata filtering plus vector ranking for final results

## Current Status

- Core retrieval pipeline is working end-to-end in Docker.
- LLM filter extraction is working for sun/water/zone style queries.
- Filtered search fallback is enabled: if metadata filter returns no hits, query retries as vector-only.
- Integration tests are passing in the containerized workflow.

## Project Structure

- app/vectordb/db.py: Vector DB manager, LLM filter extraction, and query orchestration
- data/plants.json: Seed plant data and metadata
- tests/test_hybrid_search_integration.py: Integration tests for key query behavior
- docker-compose.yaml: Service orchestration (app, vectordb, ollama)

## Architecture

1. User query is sent to LLM for metadata filter extraction.
2. Extracted filters become a ChromaDB where clause.
3. ChromaDB query runs with:
	 - query_texts for vector similarity
	 - where metadata filters when present
4. If filtered result is empty or fails, query retries without filters.
5. Similarity is computed from returned distances.

## Run

### Start services

docker compose up --build

### Start infra only (for repeated test runs)

docker compose up -d ollama vectordb

## Test

### Integration tests in Docker (recommended)

docker compose run --rm app uv run pytest -q tests/test_hybrid_search_integration.py -m integration

### Integration tests locally

uv run pytest -q tests/test_hybrid_search_integration.py -m integration

## Notes

- First Ollama query after startup may be slower because the model loads into memory.
- Chroma telemetry may emit deprecation warnings from dependencies; these are non-blocking.
- Metadata operators matter:
	- sun_requirement and water_needs are exact categorical fields
	- hardiness_zones supports contains-style matching for zone text/range patterns

## Next Recommended Steps

1. Add API endpoints for runtime query requests (instead of startup-only flow).
2. Expand plant dataset and add more metadata fields.
3. Add unit tests for filter extraction edge cases.
4. Add CI job to run integration tests automatically.
