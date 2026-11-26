---
name: work-issue
description: Take authorized work from GitHub Issues using native planning-statuses, dependencies, and sub-issues without extra scripts.
---

# work-issue

On-demand procedure for taking authorized Issues via native GitHub workflow (`gh` / REST). Only the coordinator runs it; delegates never reserve or transition Issues. Read `AGENTS.md` and `specs/project-rules.md` (when present) before acting on any gate, and follow [orchestrate](../orchestrate/SKILL.md) and [issue-workflow](../../methodology/issue-workflow.md).

## Queue, reservation & rejected reviews

- **Continuous queue:** Process `Todo` Issues one after another until authorized work is exhausted or a real blocker remains; after delivering one, recompute the queue. No receipts or duplicate reports.
- **Authorization & blockers:** `Todo` authorizes execution. Check `gh api repos/{owner}/{repo}/issues/{n}/dependencies/blocked_by` and require zero open blockers (including blocking sub-issues) before reserving. Never infer authorization from comments, labels, or `Backlog`.
- **Fallback (404 / unavailable):** If native `planning-statuses` return 404 or are unavailable, **stop immediately** and require explicit human authorization; never invent local states.
- **Routing:** Optional `agent:<client>` label (`claude`, `codex`, `opencode`, `hermes`, `antigravity`); no label means any compatible client. **Never use GitHub assignees** (assigning moves `Backlog` → `Todo` and does not revert).
- **Reserve (soft lock, last-write-wins):** Always reserve manually (a draft PR may not transition `Todo`):
  1. `gh api -X PATCH repos/{owner}/{repo}/issues/{n} -f status="In progress"` (`gh` has no `--status`).
  2. Post 1 brief start comment (agent identity + scope).
  3. Re-read the Issue to confirm `In progress` and no concurrent reservation.
- **Rejected review:** Reviewer/owner returns the Issue to `Todo` manually. On pickup: reuse the existing branch and PR (do not close/reopen the PR or create new issues/branches/PRs for ordinary fixes), read only pending findings, reserve (`In progress`), fix, and set `In review` for re-review.

## Execution, closure & gates

- **Execute & deliver:** Delegate technical work under [orchestrate](../orchestrate/SKILL.md). Keep independent QA/review and merge approval gates intact ([approvals](../../methodology/approvals.md)).
- **PR linkage & closure:** Against the default branch, link with `Closes #N` (merge → `Done` and closes). Against `test`, use `Refs #N` and close only after promotion or human acceptance.
- **Traceability:** Record Issue, PR, CI status, and candidate SHA; never merge, deploy, or mark `Done` without human approval.
