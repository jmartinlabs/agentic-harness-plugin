# Agentic Harness plugin — repository instructions

This repository is the plugin itself. These are instructions, not enforcement.

## Before coordinating or delegating

1. Load the `orchestrate` skill.
2. Read the active coordinator configuration from the main project root, never a worktree:
   - T3 host: `t3.local.json` if present, otherwise `t3.json`.
   - Standalone: `.agents/harnesses/<coordinator>.json` (`claude`, `codex`, `opencode`, `hermes`).
3. Validate it (`scripts/validate-core --project <project> --harness-file <file>`) and
   dispatch only the exact provider and model it resolves. An unavailable route stops
   dispatch; never substitute ([policy](methodology/dynamic-agents.md#host-worker-configuration)).

Missing means attempted and absent: native delegation then keeps its existing rules.
An unreadable or invalid file, or a T3 role with no profile and no same-file default,
stops dispatch. Workers executing a packet ignore this section: they never read
coordinator configuration, delegate or approve.

## Rules

The common contract is the plugin's methodology; this file does not restate it.