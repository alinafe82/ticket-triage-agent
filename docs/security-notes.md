# Security Notes

## Threat Assumptions

- The default local mode uses the mock LLM provider and requires no API key.
- Non-local deployments may handle sensitive ticket content.
- Optional provider integrations can send ticket text to external services if enabled.

## What It Protects Against

- Oversized request payloads through Pydantic length validation.
- Wildcard CORS with browser credentials through explicit configuration rejection.
- Public API docs exposure in production by disabling docs when `ENVIRONMENT=production`.
- Ticket content leakage in request logs by logging lengths and correlation IDs instead of
  summary text.
- Secret commits through repository secret scanning and local `.env` guidance.

## What It Does Not Protect Against

- Unauthenticated public use. Authentication is not implemented.
- Prompt injection or data leakage if external LLM providers are enabled.
- Unsafe pickle loading from untrusted model files.
- Abuse from high request volume. Rate limiting is not implemented.
- Incorrect routing decisions from demo training data.

## Safe Local Usage

```bash
uv run uvicorn src.app:app --reload
```

Keep `LLM_PROVIDER=mock` unless you intentionally test a provider integration. Do not commit
real API keys, private ticket text, customer names, or employer queue names.

## Known Limitations

`Router.load` uses pickle because it is simple for the demo model. Pickle can execute code
during loading, so only load model files produced by this service from a trusted local path. A
production service should use a signed artifact workflow or safer model serialization format.

Before exposing this API outside a trusted local network, add auth, rate limiting, request-size
controls at the gateway, and a data-handling review for any provider-backed LLM path.
