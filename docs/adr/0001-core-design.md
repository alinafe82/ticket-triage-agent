# ADR 0001: Keep Routing Deterministic And LLM Output Optional

## Context

Ticket routing should be explainable enough for a support or platform team to override it.
Generated text can help with response drafting, but it should not own the queue decision.

## Decision

Use a deterministic router for queue prediction and keep LLM providers behind a small interface.
The API layer handles request validation and response shape, while the service coordinates
routing and reply generation.

## Alternatives Considered

- Use an LLM directly for routing decisions.
- Build a ticket-system connector before stabilizing the API.
- Store demo tickets and model artifacts as if they were production data.

## Why This Design Was Selected

I chose this design because deterministic routing is easier to test and defend. The optional
LLM interface keeps provider concerns out of the routing decision.

## Tradeoffs

The tradeoff is that the local model is simple and trained on demo data. It gives a useful
architecture story, but it is not evidence of production routing quality.

## Consequences

- The app runs locally without secrets in mock mode.
- Provider integrations can be tested separately.
- Real deployments still need auth, feedback loops, and model evaluation.

## What Would Change At Larger Scale

At larger scale, I would add authentication, a real ticket connector, human override feedback,
offline evaluation, rate limiting, and a safer model artifact pipeline. I would not make LLM
output the source of truth for routing without measurement.
