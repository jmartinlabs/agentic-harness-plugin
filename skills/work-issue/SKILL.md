---
name: work-issue
description: Take authorized work from GitHub Issues using native planning-statuses, dependencies, and sub-issues without extra scripts.
---

# work-issue

On-demand procedure for taking authorized Issues via native GitHub workflow (`gh` / REST). Only the coordinator runs it; delegates never reserve or transition Issues. Read `AGENTS.md` and `specs/project-rules.md` (when present) before acting on any gate, and follow [orchestrate](../orchestrate/SKILL.md) and [issue-workflow](../../methodology/issue-workflow.md).

## Queue, reservation & concurrency

- **Continuous queue:** Process `Todo` Issues sequentially until authorized work is exhausted or a real blocker remains; after delivering one, recompute the queue. No duplicate reports.
- **Authorization & blockers:** `Todo` authorizes execution. Check `gh api repos/{owner}/{repo}/issues/{n}/dependencies/blocked_by` and require zero open blockers (including blocking sub-issues) before reserving. Never infer authorization from comments, labels, or `Backlog`.
- **Fallback (404 / unavailable):** If native `planning-statuses` return 404 or are unavailable, **stop immediately** and require explicit human authorization; never invent local states.
- **Routing:** Optional `agent:<client>` label (`claude`, `codex`, `opencode`, `hermes`, `antigravity`); no label means any compatible client. **Never use GitHub assignees** (assigning moves `Backlog` → `Todo` and does not revert).
- **Reserve & concurrency (no CAS):** Always reserve manually (draft PRs may not transition `Todo`):
  1. `gh api -X PATCH repos/{owner}/{repo}/issues/{n} -f status="In progress"` (`gh` has no `--status`).
  2. Post 1 brief start comment (agent identity + scope).
  3. Re-read status **and comments** (status alone does not detect concurrency): if another agent's start comment exists, oldest wins and the other stops without further writes and reports; if order is unclear or two own reservations exist, stop and ask.

## Delivery, rejected reviews & gates

- **First delivery to review:** Open/ready the PR under [orchestrate](../orchestrate/SKILL.md). With `Closes #N` and a ready PR, GitHub moves the Issue to `In review`; with `Refs #N`, set `In review` manually. Delivery ends in `In review`.
- **Rejected review (same branch & PR):** With `Closes #N` and a ready PR, convert PR to draft (`In review` → `In progress`), then set `Todo` (persists); with `Refs #N`, return to `Todo` directly. Never close/reopen the PR or open new issues/branches/PRs for ordinary fixes. On resume: `In progress`, read only pending findings, fix, and mark ready (`Closes`) or set `In review` (`Refs`).
- **Closure & gates:** Merge to default branch → `Done`/close; on `test`, `Refs #N` + close after promotion/acceptance. Keep independent QA/review, merge approval ([approvals](../../methodology/approvals.md)), and Issue+PR+CI+SHA traceability intact.
