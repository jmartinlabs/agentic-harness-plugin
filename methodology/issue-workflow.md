# Issue workflow

Native GitHub workflow for authorized work in Issues, extending [adaptive workflows](workflows.md) and [epic orchestration](epic-orchestration.md). Procedure: [work-issue](../skills/work-issue/SKILL.md). No external Project board or local tracker file is used.

## Native statuses & verified limits

- **Planning statuses:** `Backlog`, `Todo`, `In progress`, `In review`, `Done`, `Not planned`, `Duplicate`.
- **Write:** `gh api -X PATCH repos/{owner}/{repo}/issues/{n} -f status="In progress"` (`gh` has no `--status`).
- **Verified transition limits:**
  - On creation or when marked ready, a ready PR with `Closes` overwrites `Todo`/`In progress` to `In review` (not continuously; a subsequent manual `PATCH` persists). With `Refs`, `Todo`/`In progress` are preserved.
  - A draft PR may not move `Todo` → `In progress`: always reserve manually.
  - Reopening a ready PR forces `In review`: do not close/reopen PRs during ordinary fixes.
  - Submitting a review does not change status; returning to `Todo` is manual.
  - Merge to default branch → `Done` and close; on `test`, use `Refs #N` and close after promotion/acceptance. Reopen → `Backlog`; unplanned → `Not planned`.
- **Fallback:** If `planning-statuses` return 404 or are unavailable, **stop** and require explicit human authorization; never invent local states.

## Adaptive issue structure

| Case | Structure |
| --- | --- |
| Simple | Single Issue |
| With uncertainty | Parent + Analysis + DEV |
| Complex, clear requirements | Parent + SPEC + DEV |
| Complex with uncertainty | Parent + Analysis + SPEC + DEV |

Create sub-issues in `Backlog` with native `blocked_by` dependencies; creating a sub-issue never authorizes it. Move each sub-issue to `Todo` to authorize it, and close the parent only when the global objective is met.

## Queue, concurrency & rejected reviews

- **Continuous queue & authorization:** `Todo` authorizes execution; open `blocked_by` dependencies block start. Process eligible `Todo` Issues sequentially and recompute the queue after each delivery, without duplicate reports.
- **No assignees:** Never use GitHub assignees (assigning moves `Backlog` → `Todo` and does not revert). Route via `agent:<client>` (`claude`, `codex`, `opencode`, `hermes`, `antigravity`); no label means any compatible client.
- **Single coordinator & soft reservation (no CAS):** Concurrent coordinators per repository are unsupported; reservation is soft and the settling window reduces but does not eliminate races. Reserve with `PATCH` `"In progress"` + `Reserva: <agente> · ronda: <enlace al comentario de rechazo | inicial> · <alcance>` (`inicial` or latest authorization comment on reopen; only current-round reservations count). Re-read once after ≈10–15 s (no polling): if another same-round reservation exists, oldest server timestamp wins and the other stops without writing and reports; if order is unclear or two own reservations exist, stop and ask.
- **Rejected review:** Record an identifiable rejection comment (link, opening a new round). With `Closes` + ready PR, move PR to draft (`In review` → `In progress`) then `Todo`; with `Refs`, return to `Todo` directly. Reuse the existing branch/PR, read only pending findings, resume in `In progress`, fix, and return to `In review`.

## Closure, gates & traceability

- **Gates & traceability:** Independent QA/review and explicit merge approval ([approvals](approvals.md)) remain mandatory. Keep single-source traceability across Issue (decisions), PR (diff/QA/review), CI, and candidate SHA without duplicating evidence.
