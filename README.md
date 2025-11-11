# Ticket Triage Agent (Hybrid ML + LLM)

**uv-native + GitLab CI** demo combining deterministic ML routing with an LLM reply.

## Dev
```bash
uv venv && source .venv/bin/activate
uv pip install -e .[dev]
uv run uvicorn src.app:app --reload
```
