# Issue workflow

Native GitHub workflow for authorized work in Issues, extending [adaptive workflows](workflows.md) and [epic orchestration](epic-orchestration.md). Procedure: [work-issue](../skills/work-issue/SKILL.md). No external Project board or local tracker file is used.

## Native statuses & verified limits

- **Planning statuses:** `Backlog`, `Todo`, `In progress`, `In review`, `Done`, `Not planned`, `Duplicate`.
- **Write:** `gh api -X PATCH repos/{owner}/{repo}/issues/{n} -f status="In progress"` (`gh` has no `--status`).
- **Verified transition limits:** `Todo` and `In progress` are preserved even with a ready PR (manual transitions are not overwritten); a draft PR may not move `Todo` → `In progress` (always reserve manually); reopening a ready PR forces `In review` (do not close/reopen PRs during ordinary fixes); submitting a review does not change status (returning to `Todo` is manual); merge to default branch → `Done` and close (on `test`, use `Refs #N` and close after promotion/acceptance); reopen → `Backlog`; unplanned → `Not planned`.
- **Fallback:** If `planning-statuses` return 404 or are unavailable, **stop** and require explicit human authorization; never invent local states.

## Adaptive issue structure

| Case | Structure |
| --- | --- |
| Simple | Single Issue |
| With uncertainty | Parent + Analysis + DEV |
| Complex, clear requirements | Parent + SPEC + DEV |
| Complex with uncertainty | Parent + Analysis + SPEC + DEV |

Create sub-issues in `Backlog` with native `blocked_by` dependencies; creating a sub-issue never authorizes it. Move each sub-issue to `Todo` to authorize it, and close the parent only when the global objective is met.

## Queue, reservation & rejected reviews

- **Continuous queue & authorization:** `Todo` authorizes execution; open `blocked_by` dependencies block start. Process eligible `Todo` Issues sequentially and recompute the queue after each delivery, without receipts or duplicate reports.
- **No assignees:** Never use GitHub assignees (assigning moves `Backlog` → `Todo` and does not revert). Route via `agent:<client>` (`claude`, `codex`, `opencode`, `hermes`, `antigravity`); no label means any compatible client.
- **Soft reservation (no CAS, last-write-wins):** Verify `Todo` and clear dependencies, `PATCH` status to `"In progress"`, post 1 brief start comment with agent identity, and re-read to confirm.
- **Rejected review:** Owner/reviewer returns the Issue to `Todo` manually. Reuse the existing branch and PR, read only pending findings, move `Todo` → `In progress` on resume and back to `In review` on re-review; never open new issues, branches, or PRs for ordinary fixes.

## Closure, gates & traceability

- **Gates & traceability:** Independent QA/review and explicit merge approval ([approvals](approvals.md)) remain mandatory. Keep single-source traceability across Issue (decisions), PR (diff/QA/review), CI, and candidate SHA without duplicating evidence.
