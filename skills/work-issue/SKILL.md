---
name: work-issue
description: Take authorized work from GitHub Issues using native planning-statuses, dependencies, and sub-issues without extra scripts.
---

# work-issue

On-demand procedure for taking authorized Issues via native GitHub workflow (`gh` / REST). Only the coordinator runs it; delegates never reserve or transition Issues. Read `AGENTS.md` and `specs/project-rules.md` (when present) before acting on any gate, and follow [orchestrate](../orchestrate/SKILL.md) and [issue-workflow](../../methodology/issue-workflow.md).

## Native statuses & reservation

- **Authorization:** `Todo` authorizes execution. Open dependencies (`blocked_by`) or open blocking sub-issues block start. Never infer authorization from comments, labels, or `Backlog`.
- **Fallback (404 / unavailable):** If native `planning-statuses` return 404 or are unavailable, **stop immediately** and require explicit human authorization before any write or work; never invent local states.
- **Routing:** Optional `agent:<client>` label (`claude`, `codex`, `opencode`, `hermes`, `antigravity`); no label means any compatible client. **Never use GitHub assignees** (assigning moves `Backlog` → `Todo` and does not revert on unassign).
- **Reserve (soft lock, last-write-wins):** Re-read the Issue, verify `Todo` and no open `blocked_by`, then:
  1. `gh api -X PATCH repos/{owner}/{repo}/issues/{n} -f status="In progress"` (`gh` has no `--status`).
  2. Post 1 brief start comment (agent identity + scope).
  3. Re-read the Issue to confirm `In progress` and no concurrent reservation.

## Execution, closure & gates

- **Execute & deliver:** Delegate technical work under [orchestrate](../orchestrate/SKILL.md). Keep independent QA/review and merge approval gates intact ([approvals](../../methodology/approvals.md)).
- **PR linkage & closure:** Against the default branch, link with `Closes #N` (merge auto-transitions to `Done` and closes). Against an integration branch (`test`), use `Refs #N` and close only after promotion or explicit human acceptance.
- **Traceability:** Record Issue, PR, CI status, and candidate SHA; never merge, deploy, or mark `Done` without human approval.
