---
name: handoff
description: Stop or transfer an active session safely with a selective, verifiable current-state checkpoint.
---

# handoff

Adaptive checkpointing: recommend a new session on context saturation or phase change, never impose it. Read `specs/project-rules.md` (when present) and current Git/PR/approval state. Never merge or bypass gates.

## Procedure

1. **Freeze & stop:** Stop new execution or delegation. Record controlled workers as `stopped`, `stop requested`, or `unconfirmed`; never claim control over external/uncontrolled sessions.
2. **Inventory:** Inspect `git status`, branch/HEAD SHA, worktrees, and PR state without destroying or stashing unclear-ownership files. Commit an owned WIP checkpoint on the existing branch only if safe and authorized.
3. **Write selective state:** Reuse the existing progress file; use `specs/session-handoff.md` only when no other support exists. Include **only current state**:
   - `STOP REQUESTED — NO AUTO-RESUME`
   - Authorized scope, branch, HEAD, and PR
   - Links (never copies) to Issue, PR, SPEC, and evidence
   - Valid vs pending approvals, checks (`PASS`/`FAIL`/`UNRUN`), blockers, and **one next safe action**
   - Exclude execution history, obsolete decisions, and rules already in the plugin.
4. **Verify persistence:** Re-read the written checkpoint to confirm path, HEAD, and links; if unpersisted, mark `not persisted`.

## Next session and checkpoint retirement

A checkpoint grants **no** auto-resume authority. On resume, verify Git/PR/approval drift, consolidate durable state into existing progress/Issue/SPEC docs, and remove `specs/session-handoff.md` in the same task branch (never a standalone PR) once consolidated.
