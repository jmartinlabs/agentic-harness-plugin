# Issue template

Copy the blocks that apply. Keep the Issue self-sufficient: another agent must be able to act
on it without reading a chat. The protocol is [the issue workflow](../methodology/issue-workflow.md);
a trivial correction needs no SPEC and no formal epic.

## Objective

One paragraph: the problem, the intended outcome and why it matters now.

## Requested phase

`Analysis` | `Specification` | `Development` — and what that phase must produce. Do not ask for
development before the scope is authorized; a phase request is not an authorization by itself.

## Scope

- In scope: concrete behaviour, files or surfaces.
- Out of scope: what must not change, and the neighbouring work that stays separate.

## Routing

Optional: one label `agent:opencode`, `agent:hermes`, `agent:codex`, `agent:claude` or `agent:antigravity` to route the Issue to that agent; no label means any compatible agent. A label is routing, never authorization. Never use GitHub assignees (assigning moves `Backlog` → `Todo` and does not revert).

## Linked SPEC

`specs/NN-slug-specification.md` (or `none yet: this Issue needs analysis first`). One SPEC may
produce several executable Issues; link the parent epic or roadmap row when it exists.

## Acceptance checks

- AC-01: action, input and the result that proves it.
- AC-02: the negative or error case that must also hold.

## Dependencies

Native `blocked_by` dependencies (or blocking sub-issues), or `None`. A dependency is satisfied when its status is `Done`, `Not planned`, or `Duplicate`; `Backlog`, `Todo`, `In progress`, and `In review` block.

## Authorization and evidence

- Status: native `planning-statuses` (`Backlog`, `Todo`, `In progress`, `In review`, `Done`, `Not planned`, `Duplicate`). Everything starts in `Backlog`; `Todo` authorizes execution.
- Evidence on delivery: branch and commit, PR, checks (PASS / FAIL / UNRUN) and candidate SHA. Against the default branch, `Closes #N` transitions to `Done` on merge; against `test`, use `Refs #N` and close after promotion or acceptance.
