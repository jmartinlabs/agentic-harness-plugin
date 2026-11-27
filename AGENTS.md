# Agentic Harness plugin — repository instructions

This repository is the plugin itself. These instructions are not enforcement and
do not restate the methodology.

## Coordinator only

1. Load the `orchestrate` skill.
2. Read the active coordinator configuration from the main project root, never a worktree:
   - T3 host: `.agents/harnesses/t3.local.json` if present, otherwise `.agents/harnesses/t3.json`.
   - Standalone: `.agents/harnesses/<coordinator>.json`.
3. Validate it (`scripts/validate-core --project <project> --harness-file <file>`) and
   apply `orchestrate` step 4 before each dispatch: dispatch the exact provider and model
   the file selects and never substitute; where the policy permits, an absent value keeps
   native inheritance.

Missing means attempted and absent: native delegation then keeps its existing rules.
An unreadable or invalid file, or a T3 role with no profile and no same-file default
(absent an authorized explicit selection), stops dispatch.

Workers executing a packet ignore this section: they never read coordinator
configuration, delegate or approve.