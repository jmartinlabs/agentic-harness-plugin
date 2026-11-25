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

### Known limitations
Evidence is local and synthetic; Codex and Antigravity are only partly verified. See the README sections "Clients" and "Not yet in the plugin" for the exact limits.
