# Linting and Testing Standards

These standards define the checks expected before a pull request is marked ready. Run the sections for the
languages touched by the change.

## Required Gates

- Start from the default branch and keep the PR focused on one reviewable change.
- Run `git diff --check` and `git diff --cached --check` before committing.
- Run `repowave scan .` when `repowave.toml` is present.
- Run every applicable language command below. If a command needs credentials, a live service, or unavailable
  platform tooling, state that in the PR and run the closest local gate.
- Add or update tests for behavior changes. Documentation-only changes still need the diff and repository gates.

## Python

- Use `uv` with the checked-in lockfile.
- Run Ruff for linting and formatting checks.
- Run Pytest for routing, prioritization, parsing, and failure handling.
- Keep ticket data anonymized in fixtures and avoid live issue tracker calls in unit tests.

## Current Command Map

- Install: `uv sync --extra dev --locked`.
- Lint: `uv run ruff check .` and `uv run mypy src`.
- Tests: `uv run make test` or `uv run make test-v` when debugging.
- Coverage: `uv run make test-cov`; use `make coverage` only to open an already generated report.
- Local automation gate: `uv run make pre-commit-run` when pre-commit hooks change.
