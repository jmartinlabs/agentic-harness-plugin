# Issue workflow

Native GitHub workflow for authorized work in Issues, extending [adaptive workflows](workflows.md) and [epic orchestration](epic-orchestration.md). Procedure: [work-issue](../skills/work-issue/SKILL.md). No external Project board or local tracker file is used.

## Native statuses & transitions

- **Planning statuses:** `Backlog`, `Todo`, `In progress`, `In review`, `Done`, `Not planned`, `Duplicate`.
- **Write:** `gh api -X PATCH repos/{owner}/{repo}/issues/{n} -f status="In progress"` (`gh` has no `--status`).
- **Auto-transitions:** draft PR → `In progress`; PR ready → `In review`; merge → `Done` and close; reopen → `Backlog`; unplanned → `Not planned`.
- **Fallback:** If `planning-statuses` return 404 or are unavailable, **stop** and require explicit human authorization; never invent local states.

## Adaptive issue structure

| Case | Structure |
| --- | --- |
| Simple | Single Issue |
| With uncertainty | Parent + Analysis + DEV |
| Complex, clear requirements | Parent + SPEC + DEV |
| Complex with uncertainty | Parent + Analysis + SPEC + DEV |

Create sub-issues in `Backlog` with native `blocked_by` dependencies; creating a sub-issue never authorizes it. Move each sub-issue to `Todo` to authorize it, and close the parent only when the global objective is met.

## Authorization, reservation & routing

- **Authorization:** `Todo` authorizes execution; open `blocked_by` dependencies block start.
- **No assignees:** Never use GitHub assignees (assigning moves `Backlog` → `Todo` and does not revert on unassign). Route via `agent:<client>` (`claude`, `codex`, `opencode`, `hermes`, `antigravity`); no label means any compatible client.
- **Soft reservation (no CAS, last-write-wins):** Verify `Todo` and clear dependencies, `PATCH` status to `"In progress"`, post 1 brief start comment with agent identity, and re-read to confirm.

## Closure, gates & traceability

- **PR linkage:** Use `Closes #N` against the default branch; against an integration branch (`test`), use `Refs #N` and close after promotion or human acceptance.
- **Gates & traceability:** Independent QA/review and explicit merge approval ([approvals](approvals.md)) remain mandatory. Keep single-source traceability across Issue (decisions), PR (diff/QA/review), CI, and candidate SHA without duplicating evidence.
