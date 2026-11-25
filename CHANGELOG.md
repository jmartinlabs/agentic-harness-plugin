# Changelog

Format: [Keep a Changelog](https://keepachangelog.com/en/1.1.0/); versioning: [SemVer](https://semver.org/), see [RELEASING.md](RELEASING.md).

## [1.0.0]

First release. Not tagged or released until the owner approves it.

### Added
- Skills: `orchestrate`, `task`, `tweak`, `spec`, `dev`, `roadmap`, `handoff`, `init-project`, `adopt-project`, `bootstrap`, `work-issue`, `relay` and `verify-project`.
- Methodology documents, the four role contracts and the document templates, all served from the plugin instead of being copied into projects.
- Claude Code agents (`functional`, `implementation`, `infrastructure`, `qa-review`) and the SessionStart hook.
- Tools with `bin/` shims on PATH: `agentic-verify-project`, `agentic-work-issue`, `agentic-relay`, `agentic-check-delegation-route`, `agentic-usage-report`, `agentic-usage-auto`.
- `scripts/validate-core` (v2 harness schema checker) and the read-only readiness diagnostic, which also reports `project_pin` and `pin_status` (informational).
- Manifests for Claude Code, Codex and Antigravity; marketplace descriptors for Claude Code and Codex.

### Fixed during release review
- `relay` skill no longer tells to pass repository flags the tool does not accept; `adopt-project` uses the new read-only `verify-project.py --inventory`, which works on a project that lacks the entry files.
- `methodology/dynamic-agents.md` names `validate-core` as the v2 checker.

### Known limitations
Evidence is local and synthetic. Every release must bump `version`: a branch-tracking install does not update at an unchanged `version`.

Codex and Antigravity are only partly verified (Codex desktop and interactive surfaces, upgrade refresh and effective effort when not requested are unrun). See the README sections "Clients" and "Not yet in the plugin" for the exact limits.
