# Architecture

## Problem

Support and platform tickets often lose time in first-pass routing. The goal is to recommend a
queue and produce enough context for a human to accept or override the recommendation.

## Intended User

The intended user is an internal developer productivity or platform support team.

## Components

- FastAPI app: request validation, optional API key enforcement, health endpoints, and OpenAPI
  docs for non-production use.
- Router: deterministic ML-style queue prediction over ticket text.
- Service layer: coordinates routing, reply generation, and response metadata.
- LLM provider interface: optional summary/reply generation without coupling routing to a
  provider.

## Data Flow

A caller submits a ticket summary and description. The API validates input and checks the API
key when one is configured. The service builds the routing text, the router scores queues, and
the response includes the recommended queue, confidence, review flag, alternatives, and
correlation metadata.

## Design Choices

I kept routing deterministic because queue assignment should be explainable and testable. LLM
output is optional and should not own the final routing decision.

The app separates API, service, router, and provider code so the routing model can evolve
without rewriting endpoint behavior.

Docs are disabled automatically when `ENVIRONMENT=production`. CORS defaults are local-only and
do not allow browser credentials unless explicit origins are configured.

## What Is Not Built

The repo does not integrate with a real ticket tracker, persist feedback, or train on private
ticket data.

## Extension Points

- Add a ticket-system connector.
- Add human override feedback and model retraining.
- Add metrics for confidence distribution and routing quality.
- Add authentication before exposing the API beyond local development.

## Operational Considerations

A production service should log correlation IDs, protect ticket content, measure routing
quality, and keep humans in the loop for low-confidence decisions.

Persisted router files use pickle, so they must be treated as trusted artifacts. A larger
deployment should replace that with a safer model packaging format or signed artifact workflow.

## Testing Strategy

Tests cover API validation, service behavior, routing outputs, config, and provider selection.
The next layer would be contract tests for a real ticket-system adapter.
