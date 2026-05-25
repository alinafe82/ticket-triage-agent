# ADR 0001: Keep Routing Deterministic and Provider Output Optional

## Status

Accepted

## Context

Ticket triage needs predictable behavior. Generated text can help summarize a recommendation,
but queue assignment should be easy to test and audit.

## Decision

The routing path is deterministic and tested directly. Provider-backed generated output is kept
behind a separate interface and is not required for the core triage decision.

## Consequences

The service is easier to run locally and safer to review. The tradeoff is that the demo model
is simple and would need real feedback data before production use.
