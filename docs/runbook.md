# Runbook

## Run Locally

```bash
uv venv
source .venv/bin/activate
uv pip install -e .[dev]
uv run uvicorn src.app:app --reload
```

Health check:

```bash
curl http://127.0.0.1:8000/health
```

Example triage request:

```bash
curl -X POST http://127.0.0.1:8000/triage \
  -H 'content-type: application/json' \
  -d '{"summary":"VPN issue","description":"VPN connection fails on Mac after password reset"}'
```

## Test

```bash
uv run --extra dev pytest
uv run --extra dev ruff check .
```

## Common Failure Modes

- `Service not initialized`: startup failed or tests did not initialize the app lifespan.
- `OpenAI API key not configured` or `Anthropic API key not configured`: provider mode was
  enabled without `LLM_API_KEY`.
- CORS configuration error: do not combine `CORS_ORIGINS=["*"]` with
  `CORS_ALLOW_CREDENTIALS=true`.
- 422 validation response: summary and description are required and length-limited.

## Troubleshooting

- Start with `LLM_PROVIDER=mock` to verify the API without external services.
- Check `/ready` after startup before testing `/triage`.
- Use the response `correlation_id` to match API errors with logs.
- Keep `ENVIRONMENT=development` if you need interactive docs locally.

## Safe Cleanup

Remove local generated files if needed:

```bash
rm -rf .pytest_cache htmlcov coverage.xml .coverage models/router.pkl
```

Only remove generated artifacts. Do not delete source files or test fixtures.

## Known Limitations

The default model uses demo training data. The service is useful as an API and architecture
example, not as a real routing model without evaluation data and authentication.
