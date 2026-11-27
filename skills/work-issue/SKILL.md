---
name: work-issue
description: Take authorized work from GitHub Issues using native planning-statuses, dependencies, and sub-issues without extra scripts.
---

# work-issue

On-demand procedure for taking authorized Issues via native GitHub workflow (`gh` / REST). Single coordinator per repository; delegates never reserve or transition Issues. Read `AGENTS.md` and `specs/project-rules.md` (when present) before acting on any gate, and follow [orchestrate](../orchestrate/SKILL.md) and [issue-workflow](../../methodology/issue-workflow.md).

## Queue, reservation & concurrency

- **Preflight & continuous queue:** Run in order: (1) `gh api repos/{owner}/{repo}/planning-statuses` must return 200 (if 404 or unavailable, **stop immediately** and require explicit human authorization; never list, infer empty queue, or invent local states); (2) list `Todo` via `gh api --paginate "repos/{owner}/{repo}/issues?state=open&per_page=100" --jq '.[] | select(.status.name=="Todo" and (.pull_request|not)) | .number'`; (3) if empty, check `status==null` via `gh api --paginate "repos/{owner}/{repo}/issues?state=open&per_page=100" --jq '.[] | select((.pull_request|not) and .status==null) | .number'` and report any as unset (not empty queue); only if none exist, conclude "no authorized work". For each `Todo` number, check dependencies and agent label before reserving; recompute after each delivery. No duplicate reports.
- **Authorization & blockers:** `Todo` authorizes execution. Check `gh api --paginate repos/{owner}/{repo}/issues/{n}/dependencies/blocked_by` and require all dependencies satisfied per [issue-workflow](../../methodology/issue-workflow.md#queue-concurrency--rejected-reviews) before reserving. Never infer authorization from comments, labels, or `Backlog`.
- **Routing:** Optional `agent:<client>` label (`claude`, `codex`, `opencode`, `hermes`, `antigravity`); no label means any compatible client. **Never use GitHub assignees** (assigning moves `Backlog` → `Todo` and does not revert).
- **Reserve & concurrency (soft, no CAS; concurrent coordinators unsupported):** Always reserve manually (draft PRs may not transition `Todo`):
  1. `gh api -X PATCH repos/{owner}/{repo}/issues/{n} -f status="In progress"` (`gh` has no `--status`).
  2. Post 1 reservation comment: `Reserva: <agente> · ronda: <enlace al comentario de rechazo | inicial> · <alcance>` (`inicial`, or the latest authorization comment if reopened; rejections open a new round, earlier rounds are ignored).
  3. After a brief settling margin (≈10–15 s, single re-read, no polling), re-read status and comments: if another reservation for the same round exists, oldest server timestamp wins and the other stops without additional writes and reports; if order is unclear or two own reservations exist, stop and ask.

## Delivery, rejected reviews & gates

- **First delivery to review:** Open/ready the PR under [orchestrate](../orchestrate/SKILL.md). With `Closes #N` and a ready PR, GitHub moves the Issue to `In review`; with `Refs #N`, set `In review` manually. Delivery ends in `In review`.
- **Rejected review (same branch & PR):** Reviewer/owner records an identifiable rejection comment (link, opening the new round) and returns the Issue to `Todo` (with `Closes #N` + ready PR, convert PR to draft → `In progress`, then `Todo`; with `Refs #N`, directly). Never close/reopen the PR or open new issues/branches/PRs for ordinary fixes. On resume: `In progress`, read only pending findings, fix, and mark ready (`Closes`) or set `In review` (`Refs`).
- **Phases without a PR:** `Analysis`/`SPEC`/documentary phases deliver a brief report in the Issue and close on owner acceptance (`Done`) per [issue-workflow](../../methodology/issue-workflow.md#closure-gates--traceability).
- **Closure & gates:** Merge to default branch → `Done`/close; on `test`, `Refs #N` + close after promotion/acceptance. Keep independent QA/review, merge approval ([approvals](../../methodology/approvals.md)), and Issue+PR+CI+SHA traceability intact.
