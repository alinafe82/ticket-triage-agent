# Production Readiness

## Current State

What works:

- The FastAPI app exposes health, readiness, queue listing, and triage endpoints.
- Request models validate summary and description length.
- Service logic is separated from API handlers.
- Router, service, config, API behavior, LLM mock, and persistence paths are covered by tests.
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

What is missing:

- Authentication and authorization for non-local deployments.
- Real ticket-system connector.
- Human override feedback and routing-quality evaluation.
- Safer model artifact format or signed model artifact workflow.
- Provider contract tests for live LLM integrations.

What is risky:

- Pickle model loading is unsafe for untrusted files.
- Ticket content sent to an external LLM can expose sensitive data if the provider path is
  enabled without a data-handling review.

## Readiness Scores

| Area | Before | Current | Notes |
| --- | ---: | ---: | --- |
| correctness | 7 | 8 | API and service paths are tested; routing quality is demo-only. |
| test coverage | 7 | 8 | 54 tests cover API, router, service, config, LLM mock, and persistence. |
| architecture clarity | 7 | 8 | API, service, router, and provider boundaries are clear. |
| maintainability | 7 | 8 | Small modules and explicit settings. |
| security | 5 | 7 | CORS/docs/logging defaults improved; auth and model artifact safety remain. |
| dependency hygiene | 6 | 7 | Dependency set is reasonable for FastAPI plus scikit-learn. |
| configuration | 6 | 8 | Environment-driven settings and safer defaults. |
| error handling | 7 | 8 | Validation, service, and unexpected errors return predictable responses. |
| logging | 6 | 7 | Correlation IDs and structured logs exist; request body content is not logged. |
| observability | 5 | 6 | Health/readiness exist; metrics are not implemented. |
| documentation | 6 | 8 | Architecture, runbook, security, ADR, and interview notes are present. |
| CI/CD | 7 | 8 | CI runs lint, mypy, tests, coverage, and secret scanning. |
| local developer experience | 7 | 8 | Mock mode works without secrets. |

## Top Issues Blocking Interview Readiness

P0:

- None known in the local mock workflow.

P1:

- No auth for a real deployment.
- Pickle loading must not accept untrusted files.
- Demo training data should not be described as production-quality routing.

P2:

- Add live-provider contract tests behind opt-in secrets.
- Add routing quality metrics once realistic labeled data exists.
- Add a ticket-system adapter only after the local API contract is stable.

## Recommended Productionization Path

Keep the local mock flow as the default. The next practical steps are authentication, a safer
model artifact strategy, and real evaluation data. Do not add queues, Kubernetes, or tracing
until there is a deployment environment that needs them.
