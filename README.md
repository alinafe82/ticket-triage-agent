# Ticket Triage Agent

A small FastAPI service that routes incoming tickets to the most likely queue, attaches a confidence score, and surfaces the cases where a human should look. Deterministic routing is the core. The LLM-generated summary is optional and is layered on top of the routing decision, not behind it.

This repo is internal-platform tooling, not a chatbot. The point is to remove the daily 15 minutes that a senior engineer spends rerouting tickets that someone else mis-filed.

## What the service is actually doing

1. Receive a ticket payload (summary + description).
2. Run a deterministic router over the text. The router returns a queue and a confidence score in [0, 1].
3. If `confidence < router_confidence_threshold` (default `0.5`, configurable in `src.config`), mark the response `needs_review` so a human handles it. The routing decision is still returned, but with the flag set.
4. Call the LLM provider to generate a short summary of the ticket. This is currently in the request path: if the provider is configured and fails, the request returns 500. The mock provider is the default and never fails.
5. Return queue, confidence, summary, `needs_review`, and a correlation ID.

Step 3 is the part that makes this useful in practice. Wrong-confidence-1.0 is what destroys trust in an automation tool. The threshold is a flat floor over the top-class confidence, not a margin between the top two classes.

The LLM step is not currently optional in the same way the deterministic routing is. The right next change is to make it best-effort: the routing decision is returned regardless of provider failures, and the summary is null on failure. That belongs to a follow-up PR.

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

## Service layout

- `src.router` — deterministic queue prediction. This is the only place that decides a queue.
- `src.service` — validation, routing, response shaping, correlation IDs.
- `src.llm` — optional provider-backed summary generation. Mock backend is default.
- `src.app` — FastAPI endpoints: `/health`, `/ready`, `/queues`, `/triage`.

Design notes: [docs/architecture.md](docs/architecture.md). Operator flow: [docs/runbook.md](docs/runbook.md).

## Why deterministic-first

Three reasons this repo leads with deterministic routing instead of an LLM call:

- A reviewer needs to understand what the service does without running it. A deterministic function over text is readable. A prompt is not.
- Latency. The deterministic path returns in single-digit milliseconds. An LLM call does not.
- The cases where LLMs are wrong tend to be confidently wrong. The deterministic router is wrong too, but it knows when it is uncertain, which is what `needs_review` is built on.

The LLM is still useful, just not for the routing decision itself. It is for the summary that a human reads before clicking "approve" or "reroute". The summary's failure mode is currently coupled to the response — see "What the service is actually doing" above.

## What the tests prove

- `/health` and `/ready` behave separately (`/ready` reflects model load state).
- `/triage` returns a queue and a confidence score for sample tickets.
- when API key auth is enabled, requests without the header are rejected.
- when API key auth is disabled, requests are accepted without the header.
- low-confidence predictions return `needs_review` instead of routing.
- the correlation ID survives across the request lifecycle and shows up in logs.
- request validation errors return structured 4xx responses.
- routing evaluation on local sample data exercises the queue predictions end-to-end.

## Adapter work left before this would run against a real ticket system

- Connectors for the actual ticket source (GitHub Issues, Jira, Linear).
- A feedback loop that records the queue a human chose when they override the recommendation. That is the data the next router iteration needs.
- A per-queue precision/recall artefact updated on a schedule. Recommendation systems that nobody is measuring drift on stop being useful within a quarter.

## Operational notes

- [docs/runbook.md](docs/runbook.md)
- [docs/security-notes.md](docs/security-notes.md)
- [docs/production-readiness.md](docs/production-readiness.md)
- [docs/interview-notes.md](docs/interview-notes.md)
