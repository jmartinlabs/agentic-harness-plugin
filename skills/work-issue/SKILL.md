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
- **Closure & gates:** Merge to default branch → `Done`/close; on `test`, `Refs #N` + close after promotion/acceptance. Keep independent QA/review, merge approval ([approvals](../../methodology/approvals.md)), [coordinator main checkout](../../methodology/dynamic-agents.md#coordinator-main-checkout), and Issue+PR+CI+SHA traceability intact.

## PR watch

- **Link & watch once:** Activate watching once when delivering the PR (draft or ready depending on the gate) and when the next step is waiting for checks or review—never before the PR exists or after QA. Use the host's native capability (`link_pull_request` and `watch_pull_request({ until: "checks" })`; use `until: "merged"` only when authorized to act after approval). While the watch is active, do not manually query CI—the watch replaces `gh pr checks` / `gh pr view` (no `gh pr view`/`checks`/`diff` loops, `sleep`, or timer loops).
- **On wakeup:** Run **one** consolidated read `pull_request_read({ include: ["checks", "threads", "comments"] })`; on failure, run `ci_logs` once; act or report and end the turn.
- **Wake vs. end of watch:** A wakeup is not the end of the watch. Do not call `unwatch_pull_request` on every wakeup or while CI or review remains pending. Call `unwatch_pull_request` only when watching ends permanently (final handback with no further waiting) or to stop a watch that is no longer needed; if the watch already ended via merge or close, no `unwatch_pull_request` is needed.
- **No merge on wakeup:** A wakeup never authorizes merge. Keep explicit human merge approval, `expectedHeadSha`, final CI verification, and independent QA/review intact; never auto-merge.
- **Fallback:** Without host watch support or PR tools, fall back to spaced queries with no loops. If a watch cuts off, perform one point-in-time read and mark state as unverified (do not invent state or blindly re-watch). When a delegated worker cannot watch, the parent coordinator watches.
- **Keep gates in `gh`:** Keep only governance gates in `gh`: `planning-statuses`, Issue state transitions, reservation, `blocked_by`, explicit merge approval, final SHA, and final CI verification.
- **Measurement (no new instrumentation):** Measure using existing telemetry (T3 Usage + thread activity): compare a 5-PR baseline without watch against a 5-PR pilot with watch across medians of coordinator turns, GitHub operations, wakeups, and ready→merge time, and record false negatives.
