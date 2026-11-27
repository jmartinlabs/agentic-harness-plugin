# Changelog

Format: [Keep a Changelog](https://keepachangelog.com/en/1.1.0/); versioning: [SemVer](https://semver.org/), see [RELEASING.md](RELEASING.md).

## [2.1.0] - 2026-11-27

### Added
- T3 host worker configuration schema (`t3.json` / `t3.local.json`), `--harness-file` single-file validation in `scripts/validate-core`, and initial `.agents/harnesses/t3.json` for this repository (#42, #45).
- Documentation for T3 host worker configuration, local exclusivity, atomic precedence, unsupported-effort `UNVERIFIED` fallback (keeping provider/model exact), requested/observed metadata in `templates/agent-work-packet.md`, and autonomous coordinator context renewal (#42, #45).

## [2.0.0] - 2026-11-27

Release candidate. Merge, tag and release need the owner's explicit approval.

### Breaking
- Retired the `scripts/work-issue` script (and its tests), the `agentic-work-issue` shim, `epic-board`, `tracker.local` support, and the 12-state / receipt model. The `$work-issue` skill is **preserved** with a minimal surface (#39, #40, PR #41).

### Changed
- Adopted the native GitHub workflow: `planning-statuses` preflight, native issue types, sub-issues, `blocked_by` dependencies (satisfied only by `Done`), soft reservation, and PR-driven issue closure (#39, #40, PR #41).
- Simplified `$work-issue` to a minimal surface and made `$handoff` adaptive/selective (#40, PR #41).
- Added Hermes profile detection for profiles without plugin skills in `scripts/update-agentic` (#36, PR #37).

### Adoption note (MAJOR)
- Existing projects upgrading to `2.0.0` must stop using `work-issue` / GitHub Project boards for workflow state and switch to `Todo` / native GitHub issue statuses, types, sub-issues, and dependencies. No automatic migration is provided.

## [1.2.2] - 2026-11-26

### Added
- Added `scripts/update-agentic`, a stdlib-only multi-harness updater and read-only `--check` mode across all five harnesses, with single shared-repo pull, timeouts, local Codex `config.toml`/cache detection, and strict version verification (#31, PR #32).

### Changed
- Simplified `README.md` user guide and Antigravity Desktop documentation (#9, PR #30).

## [1.2.1] - 2026-11-26

### Changed
- Coordinator exclusively coordinates across all five harnesses: delegates all technical work including Quick tasks (using one bounded worker with a compact packet), preserves proactive look-ahead, required independent QA, approvals, and v2 configuration, and reports a blocker instead of falling back to coordinator technical execution when no authorized usable worker is available (#22, PR #28).
- Added static consistency checks (`CoordinatorDelegationTests`) in `tests/test_plugin.py` and kept `skills/orchestrate/SKILL.md` within the 8704-byte hook budget (8679 bytes).

### Known limitations
- Live end-to-end client behavioral traces across Antigravity, Claude Code, Codex, OpenCode, and Hermes remain unrun due to quota restrictions.

## [1.2.0] - 2026-11-26

Release candidate. Merge, tag and release need the owner's explicit approval.

### Added
- Antigravity coordinator support: `work-issue`, v2 `antigravity.json`, `verify-project.py` support and global installation docs (#7).
- OpenCode global per-user adapter (`adapters/opencode/`) with `review-read` scoped by `cwd` (#4).
- Hermes global per-user adapter (`adapters/hermes/`) (#5).
- Codex `auto-agent-usage` lifecycle hooks (`Stop`, `SubagentStop`, `SessionEnd`) in `hooks/codex.json` (#6).
- `validate-core` guards for secrets, neutrality, `git diff` and required phrases (#8).

### Fixed
- Operational skills now reference `specs/project-rules.md`; native model/effort fallback behavior clarified; `Standard`/`$task` aligned in `roles/implementation.md`; granular methodology check added in `verify-project.py` (#8).

### Known limitations
- Quota-gated live checks for Claude Code and Codex are deferred.

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
