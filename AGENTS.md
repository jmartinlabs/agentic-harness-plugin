# Agentic Harness plugin — repository instructions

This repository is the plugin itself. These instructions are not enforcement and
do not restate the methodology.

## Coordinator only

Workers executing a packet ignore this section: they never read coordinator
configuration, delegate or approve.

Before the first delegation of any kind (subagent, delegate task, worker) or before
taking an Issue (`work-issue`), you are the coordinator for the rest of the session.
Without asking for confirmation:

1. Load the `orchestrate` skill if it is not already in context.
2. Read the active coordinator configuration from the main project root, never a worktree:
   - T3 host: `.agents/harnesses/t3.local.json` if present, otherwise `.agents/harnesses/t3.json`.
   - Standalone: `.agents/harnesses/<coordinator>.json`.
3. Validate it (`scripts/validate-core --project <project> --harness-file <file>`) and
   apply `orchestrate` step 4 before each dispatch. In T3, dispatch the exact provider and
   model the file selects and never substitute. In standalone, a configured profile or
   default is a request: if the client cannot apply or confirm it, fall back to native
   inheritance and report it unapplied or unverified.

Missing means attempted and absent: native delegation then keeps its existing rules.
An unreadable or invalid file, or a T3 role with no profile and no same-file default
(absent an authorized explicit selection), stops dispatch.

Conversations that do not delegate or take Issues need none of this.
