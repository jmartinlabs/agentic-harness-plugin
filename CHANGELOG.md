# Changelog

Format: [Keep a Changelog](https://keepachangelog.com/en/1.1.0/); versioning: [SemVer](https://semver.org/), see [RELEASING.md](RELEASING.md).

## [1.1.0] - unreleased

Merge, tag and release need the owner's explicit approval.

### Changed
- Use one `agentic-harness` marketplace and a stable user installation per client, with native update and a tag-based user rollback.
- Readiness reports the installed artifact version and retains the project rules and v2 configuration checks. Project-scoped marketplace declarations are no longer required.
- Claude Code and Codex SessionStart hooks report the effective version. The Claude Code hook retains the existing orchestration context.

## [1.0.0] - 2026-11-25

First release candidate. Merge, tag and release need the owner's explicit approval; none has been done.

### Added
- Skills: `orchestrate`, `task`, `tweak`, `spec`, `dev`, `roadmap`, `handoff`, `init-project`, `adopt-project`, `bootstrap`, `work-issue`, `relay` and `verify-project`.
- Methodology documents, the four role contracts and the document templates, all served from the plugin instead of being copied into projects.
- Claude Code agents (`functional`, `implementation`, `infrastructure`, `qa-review`) and the SessionStart hook.
- Tools with `bin/` shims on PATH (Claude Code only): `agentic-verify-project`, `agentic-work-issue`, `agentic-relay`, `agentic-check-delegation-route`, `agentic-usage-report`, `agentic-usage-auto`.
- `scripts/validate-core` (v2 harness schema checker) and the read-only readiness diagnostic, which also reports `project_pin` and `pin_status` (informational).
- Manifests for Claude Code, Codex and Antigravity; marketplace descriptors for Claude Code and Codex.

### Fixed during release review
- `relay` skill no longer tells to pass repository flags the tool does not accept; `adopt-project` uses the new read-only `verify-project.py --inventory`, which works on a project that lacks the entry files.
- `methodology/dynamic-agents.md` names `validate-core` as the v2 checker.

### Known limitations
Evidence is local and synthetic. Every release must bump `version`: a branch-tracking install does not update at an unchanged `version`.

Codex and Antigravity are only partly verified (Codex desktop and interactive surfaces, upgrade refresh and effective effort when not requested are unrun). See the README sections "Clients" and "Not yet in the plugin" for the exact limits.

Residual risks the owner must accept: no client has loaded 1.0.0 content yet (all evidence is on 0.1.0 content); tag-form pins are untested and Antigravity cannot pin; interactive permission behaviour, project-scope install and the trust dialog are untested; the Read rule contains the versioned install path (re-run `--print-rules` after each update); `init-project`, `adopt-project` and `bootstrap` are not exercised live end to end; GitHub write tools never ran with the plugin installed; Codex desktop, interactive and upgrade refresh are unrun; Antigravity loads only the 13 skills; effort is not verifiable on Claude; uninstall or `marketplace remove` empties the committed `settings.json`; silent first-wins on a name collision; an enabled-but-not-installed plugin fails open; the shorthand tries SSH first; argparse abbreviation such as `--repo-r`; history includes commits with a local-machine email (not rewritten, owner decision); the temporary branch `pilot/version-0.1.1` exists.
