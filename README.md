# Ticket Triage Agent

Internal ticket triage API for routing support or platform tickets to the most likely queue.

The service combines deterministic text routing with optional generated summaries. The routing
path works locally with a small model and mock data; LLM providers are optional and isolated
behind an interface.
Protected endpoints can require an `X-API-Key` header when `API_KEY` is configured.

## Why It Exists

Ticket queues are a common source of developer productivity drag. A useful triage tool should
make first-pass routing faster while keeping enough confidence and explanation for humans to
override it.

## Quickstart

```bash
uv venv && source .venv/bin/activate
uv pip install -e .[dev]
uv run uvicorn src.app:app --reload
```

Run tests and linting:

```bash
uv run --extra dev pytest
uv run --extra dev ruff check .
```

Example request:

```bash
curl -X POST http://127.0.0.1:8000/triage \
  -H 'content-type: application/json' \
  -d '{"summary":"Build cache misses on main","description":"CI jobs are slower after dependency updates"}'
```

If `API_KEY` is set, include `-H "X-API-Key: $API_KEY"` on `/triage` and `/queues`.

## Architecture Overview

- `src.app` exposes health, queue, and triage endpoints.
- `src.router` owns deterministic queue prediction.
- `src.service` coordinates validation, routing, and response shaping.
- `src.llm` isolates optional provider-backed summary generation.

See [docs/architecture.md](docs/architecture.md) for design details.
See [docs/runbook.md](docs/runbook.md), [docs/security-notes.md](docs/security-notes.md),
and [docs/production-readiness.md](docs/production-readiness.md) for operational notes.

## Limitations

- Training data is local demo data.
- The default LLM path is a mock provider.
- It routes tickets; it does not file or mutate tickets in an external tracker.
- Production deployments should set explicit CORS origins, keep docs behind an internal
  boundary, configure `API_KEY`, and load persisted model files only from trusted paths.

## Future Improvements

- Add connectors for GitHub Issues, Jira, or an internal ticket system.
- Persist feedback when humans override a route.
- Track precision/recall by queue before using recommendations automatically.

## Interview Notes

See [docs/interview-notes.md](docs/interview-notes.md).
