# NN — FEATURE: Progress

Specification: SPECIFICATION_PATH

Keep one current summary per task, replaced in place. When GitHub Issues track the work
they are the single current-state surface and this table is history
only: never keep two competing statuses.
Everything below the table is append-only; a correction is a new dated entry, not an edit.

## Current state — only when no Issue tracks the work

If GitHub Issues track the work, do not maintain this table: Issues
hold the current state and this file keeps only the history below.

| Task | State | Owner (start/stop, permission-sensitive operations) | Branch / candidate SHA | Checks last verified | PR / CI / merge | Next action | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| UNDECIDED | UNDECIDED | UNVERIFIED | UNVERIFIED | UNRUN | UNVERIFIED | UNDECIDED | none |

`State` is free text; use `UNVERIFIED` when the evidence cannot decide.

## Verified increments

Append-only. Record commands, working directory, run date, results and commit IDs.
Identify candidate, environment, delta and reasons for repeated checks. Record blocking
intervals and advance notices when relevant; tool/approval envelopes are not CPU time.
Usage requires client telemetry; missing clients/metrics remain unavailable. Do not
claim causal savings from totals.

| Date | Task | What closed | Evidence (command / candidate / PR) |
| --- | --- | --- | --- |
| UNDECIDED | | | |

## Decisions
Link to canonical guidelines; do not duplicate architectural decisions.
## Errors, regressions and blockers
None assessed yet. Distinguish failed, skipped, blocked and unrun checks.
