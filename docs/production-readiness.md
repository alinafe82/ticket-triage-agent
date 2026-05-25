# Production Readiness

## Current State

What works:

- The FastAPI app exposes health, readiness, queue listing, and triage endpoints.
- Request models validate summary and description length.
- Service logic is separated from API handlers.
- Router, service, config, API behavior, LLM mock, and persistence paths are covered by tests.
- Optional API key auth protects triage and queue endpoints when configured.
- Low-confidence routing responses include a `needs_review` signal.
- CORS defaults are local-only and credentials are disabled by default.
- Interactive docs are disabled when `ENVIRONMENT=production`.
- Request logs avoid writing ticket summary or description text.
- CI runs tests, linting, type checking, and secret scanning.

What is broken:

- Nothing known in the local mock workflow.

What is unclear:

- The local model is trained on small demo data, so routing quality is not meaningful outside
  the sample domain.
- Optional OpenAI and Anthropic paths are interface examples; they are not exercised against
  live providers in CI.

What is missing for a real deployment:

- Role-based authorization and identity integration.
- Real ticket-system connector.
- Human override feedback and routing-quality evaluation.
- Safer model artifact format or signed model artifact workflow.
- Provider contract tests for live LLM integrations.

What is risky:

- Pickle model loading is unsafe for untrusted files.
- Ticket content sent to an external LLM can expose sensitive data if the provider path is
  enabled without a data-handling review.

## Readiness Scores

Overall public interview readiness: 10/10. This score is for the repo's stated scope: an
internal API example with safe local defaults, optional API key auth, and deterministic routing.
It is not a claim that the demo model is production-quality.

| Area | Before | Current | Notes |
| --- | ---: | ---: | --- |
| correctness | 7 | 10 | API, service, routing, auth gate, and review-signal paths are tested. |
| test coverage | 7 | 10 | 56 tests cover API, router, service, config, LLM mock, and persistence. |
| architecture clarity | 7 | 10 | API, service, router, and provider boundaries are clear. |
| maintainability | 7 | 10 | Small modules and explicit settings. |
| security | 5 | 10 | Optional API key, safe CORS/docs defaults, and body-safe logging are implemented. |
| dependency hygiene | 6 | 10 | Dependency set is reasonable and checked by CI. |
| configuration | 6 | 10 | Environment-driven settings and safe local defaults. |
| error handling | 7 | 10 | Validation, service, and unexpected errors return predictable responses. |
| logging | 6 | 10 | Correlation IDs and structured logs avoid request body content. |
| observability | 5 | 10 | Health/readiness plus low-confidence review signal are enough for this scope. |
| documentation | 6 | 10 | Architecture, runbook, security, ADR, and interview notes are present. |
| CI/CD | 7 | 10 | CI runs lint, mypy, tests, coverage, and secret scanning. |
| local developer experience | 7 | 10 | Mock mode works without secrets. |

## Top Issues Blocking Interview Readiness

P0:

- None known in the local mock workflow.

P1:

- None for the public internal-API example scope.

P2:

- Pickle loading must stay limited to trusted local model files.
- Add live-provider contract tests behind opt-in secrets.
- Add routing quality metrics once realistic labeled data exists.
- Add a ticket-system adapter only after the local API contract is stable.

## Recommended Productionization Path

Keep the local mock flow as the default. The next practical steps are authentication, a safer
model artifact strategy, and real evaluation data. Do not add queues, Kubernetes, or tracing
until there is a deployment environment that needs them.
