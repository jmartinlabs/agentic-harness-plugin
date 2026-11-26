---
name: verify-project
description: Inspect a synthetic Agentic project and report the applicable approval and project rules before acting.
---

# Verify project readiness

This pilot is a read-only diagnostic. It authorizes no action and performs no dispatch. If the requested action needs an operational harness, use the project's approved workflow.

1. Resolve the installed Skill file and derive the artifact root from it (two directories above the Skill directory). Do not substitute the project's checkout for the artifact root.
2. In Claude Code run the shim `agentic-verify-project` (on PATH while the plugin is enabled); other clients run `python3 <artifact-root>/scripts/verify-project.py`. Run it from the current project directory. Optionally pass `--project <path>` to identify the intended project instead. For a known canonical coordinator, pass `--coordinator claude` or `--coordinator codex` (the diagnostic also recognizes the other existing v2 identities). Use no coordinator flag when the identity is uncertain or when testing Antigravity.
   If plugin files or tools are denied, run `agentic-verify-project --print-rules` (it only prints) and offer its JSON for the user to merge into that project's untracked `.claude/settings.local.json` if explicitly approved; do not edit permissions yourself.
3. If the script fails, report its reason and the remedy. Do not proceed past the affected readiness step. An unrelated checkout is outside this pilot.
4. On success, report the effective `artifact_version`, then read the reported artifact approvals policy and the active project's reported rules. Check applicability and report which requirements apply. A readiness result is not approval to develop, delegate, alter permissions, publish, or merge.
5. For a separately authorized native QA experiment, provide the installed canonical QA role reported by the diagnostic through the client's existing work packet. Record actual permissions and observed provenance. This Skill does not launch a worker. Do not claim v2 selection support without effective model and effort evidence.
