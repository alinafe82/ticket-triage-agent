# Linting and Testing Standards

These standards define the checks expected before a pull request is marked ready. Run the sections for the
languages touched by the change.

## Required Gates

- Start from the default branch and keep the PR focused on one reviewable change.
- Run `git diff --check` before committing.
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

- Install: `uv sync`.
- Lint: `make lint`.
- Tests: `make test` or `make test-v` when debugging.
- Coverage: `make test-cov` or `make coverage`.
- Local automation gate: `make pre-commit-run` when pre-commit hooks change.
