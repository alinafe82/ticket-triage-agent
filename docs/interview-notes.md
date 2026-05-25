# Interview Notes

## 60-Second Explanation

This is an internal ticket triage API. It accepts a ticket summary and description, predicts
the best queue, returns confidence and alternatives, and keeps generated summaries optional.
The core routing path is deterministic and covered by tests.

## Decisions I Can Defend

- Routing is deterministic so recommendations can be tested and explained.
- Generated summaries are optional because provider failures should not break triage.
- The service returns correlation metadata for operational debugging.

## Tradeoffs

The current model uses demo data. That keeps the repo public and safe, but production use would
need real labeled data, privacy review, and feedback loops.

## Fixes Made During Portfolio Hardening

- Removed inflated package description language.
- Added GitHub Actions CI.
- Added architecture notes, ADR, and interview notes.
- Verified the existing test suite: 50 tests pass locally.

## Fixes Made During Productionization

- Tightened CORS defaults and rejected wildcard origins with browser credentials.
- Disabled public docs automatically when `ENVIRONMENT=production`.
- Stopped request logging from writing ticket summary text.
- Added provider-specific default model handling and valid JSON structured logs.
- Documented pickle model-file risk and added production-readiness, security, runbook, and core
  design ADR docs.

## Likely Questions

**Why use deterministic routing instead of only an LLM?**
Queue assignment should be measurable and debuggable. I would use an LLM only for summaries or
assistive context, not as the only decision path.

**How would you improve accuracy?**
Collect labeled tickets, measure precision and recall per queue, add human override feedback,
and retrain only when metrics justify it.

**What does this show for Engineering Productivity?**
It shows internal workflow automation with test coverage, clear service boundaries, and a
human-reviewable decision path.
