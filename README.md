# Agentic Harness plugin

v1.0.0: Claude Code verified end to end; Codex verified for install, skills, diagnostic, reading and native delegation (local synthetic); Antigravity verified for skills and diagnostic through its native install; see [Clients](#clients-v1-targets-observed) and [Known limitations](#known-limitations-observed). See [CHANGELOG.md](CHANGELOG.md) and [RELEASING.md](RELEASING.md). The limitations and evidence labels below still apply.

## Quick start

1. Create the project repository from the template (GitHub "Use this template").
2. Add the marketplace and install the plugin, always, even when the project already declares them in its committed `.claude/settings.json`: `claude plugin marketplace add jmartinlabs/agentic-harness-plugin#<tag-or-sha> --scope local`, then `claude plugin install agentic@agentic-harness --scope local`. The committed pin is the project's version record, but it was NOT sufficient for install in `-p` (install failed with 'Plugin "agentic" not found in marketplace "agentic-harness"'; interactive startup behaviour is untested). Both commands write `extraKnownMarketplaces` and `enabledPlugins` into the untracked `.claude/settings.local.json`. The tested flows used `--scope local`; project scope is untested.
3. Trust the project: open it interactively once and accept the trust dialog, so the project-shared `.claude/settings.json` rules apply. In `-p` the project-shared rules are ignored (measured); after the trust dialog they are expected to apply, which is untested.
4. Allow the plugin's files and tools. Run `agentic-verify-project --print-rules` (it only prints) and merge the printed `permissions.allow` entries into `.claude/settings.local.json`; the CLI has already created that file, so do not paste over it. Or approve the permission prompts with "don't ask again" (interactive; untested). Verified (local, `-p`): the Read rule and the `agentic-verify-project` and `agentic-work-issue` rules. Untested: the other four shim rules, interactive "don't ask again", project-scope install and the trust dialog. Re-run `--print-rules` after any plugin update: the Read rule contains the install path of that version. See "Permissions for plugin files".
5. Run `/agentic:verify-project` to check readiness. It also reports `project_pin` (the `ref` of the `agentic-harness` marketplace in `.claude/settings.json` or `.claude/settings.local.json`) and `pin_status` (`tag-match`, `tag-mismatch`, `sha-or-branch` or `absent`), informational only; it never changes the exit code.
6. Run `/agentic:init-project` for a new project, or `/agentic:adopt-project` for an existing one.

These steps are Claude Code's; for the Codex and Antigravity install commands as measured, see [Clients](#clients-v1-targets-observed).

A project created from the scaffold: run steps 2-6; the scaffold's own README links here.

Nothing common is copied into the project: skills, roles, methodology, templates, scripts and agents stay in the plugin, and the skills create only project documents (`specs/project.md`, `specs/setup-progress.md`, `specs/roadmap.md` and so on).

This implements [SPEC #77](https://github.com/jmartinlabs/agent-project-template/issues/77#issuecomment-7165024336): the plugin `agentic` centralizes the common harness capabilities so that a project keeps only its context, configuration, rules and application files. It packages the operating core below plus a read-only readiness Skill and diagnostic script. It does not replace an existing harness. Licensed under the MIT licence (`LICENSE`, holder jmartinlabs, 2026).

`methodology/approvals.md` is the canonical approvals source; where it mentions `orchestrate`, it refers to the `orchestrate` Skill in this package.

## Package contents

Every moved file, its template source blob (commit `e9a46160753c5e61f7d3291da9e6a0299f840aa0`), destination hash and transformation class are listed in [PROVENANCE.md](PROVENANCE.md).

| Area | Contents | Notes |
| --- | --- | --- |
| `skills/` | `orchestrate`, `task`, `tweak`, `spec`, `dev`, `roadmap`, `handoff`, `init-project`, `adopt-project`, `bootstrap`, `work-issue`, `relay` (+ `relay/GITHUB_API.md`), plus `verify-project` | Moved, not redesigned. |
| `methodology/` | `approvals` (pinned), `ci-policy`, `dynamic-agents`, `dynamic-agents-external-clients`, `epic-orchestration`, `identifiers`, `issue-workflow`, `workflows`, `document-ownership` (from the template's `specs/README.md`) | The template's `acceptance-scenarios.md` stays in the template. |
| `roles/` | `README`, `functional`, `implementation`, `infrastructure`, `qa-review` (pinned) | |
| `templates/` | 8 document templates | Skills copy them into a project when needed. |
| `agents/` | Claude Code agents `functional`, `implementation`, `infrastructure`, `qa-review` | Read the role from `${CLAUDE_PLUGIN_ROOT}/roles/<role>.md`; no hooks, `permissionMode` or MCP servers. Claude Code only. |
| `hooks/hooks.json` | A Claude Code `SessionStart` hook that prints `skills/orchestrate/SKILL.md` (print budget 8704 bytes, enforced by a test) | Replaces the template's project `settings.json` hook. Claude Code only. |
| `scripts/`, `bin/` | Tools `work-issue`, `agent-relay`, `check-delegation-route`, `report-agent-usage`, `auto-agent-usage` (ported from the baseline; the project root is the working directory or `--repo-root`, never the plugin directory), the integrity validator `validate-core` and the read-only `verify-project.py` | In Claude Code, `bin/` is on the Bash tool PATH while the plugin is enabled: `agentic-work-issue`, `agentic-relay`, `agentic-check-delegation-route`, `agentic-usage-report`, `agentic-usage-auto`. Run them from the project directory; elsewhere use `python3 <plugin root>/scripts/<tool>`. |
| `tests/` | Plugin static tests, the ported tool suites (`tests/test-<tool>`, run as `python3 tests/test-work-issue`) and `fixtures/work-issue-project.json` | `scripts/validate-core --project DIR` validates `DIR/.agents/harnesses/*.json` (harness JSON v2). |

Deliberate delta: `skills/orchestrate/SKILL.md` step 4 now says that the user configures the coordinator's model, providers and routes in the client, and that delegate defaults, profiles and external routes come from the coordinator's project file under coordinator configuration. This is the single wording fix required by issue 77; the #75/#76 semantics are unchanged.

## Clients (v1 targets, observed)

All local, synthetic, one machine; client versions as observed in the increment-8 issue comments (Codex 0.172.0, Antigravity 1.5.17); no claim goes beyond this list. OpenCode and Hermes are second-stage and not packaged.

| Client | Install (as measured) | Verified | Observed (single run) | Unrun |
| --- | --- | --- | --- | --- |
| Claude Code 2.1.330 (GitHub channel pinned at 37fb4f3) | Quick start above | 13 `agentic:*` skills and 4 `agentic:<role>` agents load; delegation to `agentic:qa-review` works and the agent file uses `${CLAUDE_PLUGIN_ROOT}` and the child's first Read of the plugin role file succeeded; the SessionStart hook runs (8151 bytes, exit 0); `model` override effective (stream `modelUsage` showed `claude-opus-5-5` when `opus` was requested) | A merge request after generic assent was not executed; the model asked for explicit approval naming the PR and SHA (it did not say that generic assent is not approval) | Effective effort (not verifiable from the stream); a sonnet-vs-sonnet comparison |
| Codex CLI 0.172.0 (7 model sessions, `codex exec --sandbox read-only -a never`, plugin from GitHub pinned at `74e7fab3c1b358473c884f34fa04b141f3a1c558`, temporary authenticated `CODEX_HOME`) | `codex plugin marketplace add jmartinlabs/agentic-harness-plugin --ref <full sha>`, then `codex plugin add agentic@agentic-harness` | Install works in a new `CODEX_HOME`; the cache `plugins/cache/agentic-harness/agentic/<version>` has the same 84 file names as `git ls-tree` (no content hashes compared) and its 87 relative links resolve. All 13 skills are shown namespaced (`agentic:verify-project`, `agentic:orchestrate`, ...; none bare), discovered from the default `skills/` directory with no `skills` key in `plugin.json`. The model ran `python3 <cache>/scripts/verify-project.py --coordinator codex` from the cache in the read-only sandbox: exit 0, correct artifact and project roots, version 0.1.0 at that time (harmless macOS python `xcrun_db` cache warnings). Reading `methodology/approvals.md` and `roles/qa-review.md` by absolute cache path works in the read-only sandbox without prompts. Native subagent delegation works: the child thread records `parent_thread_id`, depth 1, `agent_path /root/qa`, spawned via `thread_spawn`, child model `gpt-6.2-sol`, effort low (from the session rollout; the spawn prompt is encrypted). v2: with `.agents/harnesses/codex.json` requesting `local.model=gpt-6.2-sol` and `effort=low`, the coordinator refused to spawn (no host evidence it could verify the child's settings); when the owner's prompt explicitly told it to pass the values, `spawn_agent {model, reasoning_effort}` was called and the child's rollout metadata shows exactly those values (verified by an external reader of the session metadata; the coordinator reported them as requested, not observed). Hooks: the Claude `hooks.json` did not fire and no SessionStart output or `CLAUDE_PLUGIN_ROOT` existed in the sandbox (inert on Codex). | `bin/` is NOT on PATH in Codex, so the shims are unavailable there (use `python3 <cache>/scripts/<tool>`). The child's low effort was not requested in the call: it looks like a Codex default for subagents (unverified). Codex ran `agentic:verify-project` even for unrelated prompts in the scaffold project (intended: the project `AGENTS.md` says to start with it). Codex also copies the Claude-only `agents/`, `hooks/` and `.claude-plugin/`. | Codex desktop surface, interactive mode, `codex plugin` upgrade refresh, effective effort when not requested |
| Antigravity 1.5.17 (temporary profile) | `plugin install https://github.com/jmartinlabs/agentic-harness-plugin/tree/<branch>` | Installs the branch tip at install time (the branch head was 37fb4f3 in the tested run, per the increment-8 report); disable, enable and uninstall work | The diagnostic ran through the model (version 0.1.0, correct roots, exit 0); a typo fix was classified Quick without writing (model requested `gemini-4-hydrogen-low`, effective model unverified; following the project's `AGENTS.md` is not shown by the trace) | Effective model |

- Claude Code v2: when the project's `.agents/harnesses/claude.json` requested `local.model`/`effort`, one run refused to spawn because it could not assure effective selection (consistent with the #76 "do not spawn" rule); with the owner's explicit authorization of the probe the parent passed `model` and `effort` to the Agent tool.
- Claude Code side effect (observed again): `claude plugin marketplace remove` or `uninstall` run inside the project empties `enabledPlugins` and `extraKnownMarketplaces` in the committed `.claude/settings.json`.
- Codex: the cache path is keyed by `version`, so a new commit without a version bump keeps the same path (observed in the cache layout, not tested as an update). `plugin.json` has no `skills` key or `interface` block (the docs do not require `skills` for the portable layout).
- Antigravity install takes a BRANCH only The error "Remote branch <sha> not found" was observed for the sha URL form in `plugin validate`/install attempts, and the repository root failed because `main` has no plugin; branch-only follows from the CLI cloning with `--branch`, nothing more is shown. The pin is therefore the branch tip at install time. It needs HTTPS to github.com and installs GLOBALLY under `$HOME/.gemini/config/plugins/agentic`, not into the workspace; the plugin commands did not honour `--gemini-dir` and `--app-data-dir` in the tested run (`plugin list` rejected them; the install location followed `$HOME`).
- Antigravity `plugin validate` skips the 4 `agents/*.md` (`tools:` is a string where a list is expected), never loads `hooks/hooks.json` and ignores `plugin.json` because `.antigravity-plugin/plugin.json` takes precedence. So only the 13 skills load, shown as bare names such as `verify-project`, not `agentic:verify-project`.
- Antigravity permissions: every plugin file outside the workspace costs one permission ask (about 3 for the diagnostic); there is no single read rule like Claude's. Agents that hit a sandbox failure retried with `BypassSandbox=true`, so test allow-lists must inspect arguments, not only the command line (harness lesson).

### Not yet in the plugin

- OpenCode `review-read` and the OpenCode adapters (OpenCode is a second-stage client), Codex hook wiring (`.codex/hooks.json`; its configuration test skips until it ships), and the template-only tooling (`validate-template`, `test-validator`, `check-mermaid`, the evals) are not packaged.
- `scripts/validate-core` replaces the template's v2 schema checker; no Skill calls it yet. `methodology/dynamic-agents.md` names `scripts/validate-core` as the v2 checker (a deliberate delta, see PROVENANCE).
- Native adapters other than the Claude Code agents (Codex hooks, OpenCode agents and plugin, Hermes) are not packaged.
- The `init-project`, `adopt-project` and `bootstrap` Skills and the first paragraph of `methodology/document-ownership.md` are rewritten for the plugin model (nothing common is copied into the project) but untested against a live client; the template repository itself is not yet reduced, and project-scope install, the interactive permission prompts and the `.claude/settings.json` marketplace pin flow are unrun.
- The template's `docs/` guides (visual guide, client adapters, evals) are not part of the plugin; the sentences that mention them say so.
- No claim is made about how Codex or Antigravity load these assets at runtime; only the earlier pilot observations below exist.

### Permissions for plugin files (observed)

Observed with an installed plugin (from the cache), Claude Code 2.1.330, `claude -p`, default permission mode, local synthetic, 9 sessions; the evidence is kept by the coordinator outside this repository.

1. Reading the plugin's own files (`methodology/*.md`, `roles/*.md`, `scripts/*`, even files inside the invoked skill's own directory) from the project is denied by default. Invoking a skill does not grant access to its directory.
2. A project-shared `.claude/settings.json` allow rule was ignored in `-p` because the workspace counts as untrusted ("Ignoring ... permissions.allow entry ... workspace has not been trusted"). It is expected to apply after the interactive trust dialog, but that was not tested.
3. `Read(//<absolute plugin install path>/**)` works when placed in the untracked `.claude/settings.local.json` or in the user-level settings (user-level also works in `-p` without workspace trust). A child agent (the plugin `qa-review` agent in the test) inherited the parent's rule; a plugin-agent child without the rule was not tested.
4. The rule is not portable as written: the install path depends on the Claude config directory, the marketplace name and the version, and no plugin-root variable was found or used in permission rules in these tests. The `~/...` form and a glob over marketplace names were not tested (the test layout could not authenticate with a temporary HOME).
5. Not measured: interactive prompts (likely one per path, untested), a child agent without the rule, and a merge-gate observation with the policy readable.
6. Consequence: onboarding must include an explicit step "allow Read on the plugin install directory" (the install path is printed by `claude plugin list --json` as `installPath`). A project that lacks the rule can silently lose access to the common methodology unless the model reports it, so the thin project `AGENTS.md` must say: if plugin files cannot be read, stop and ask the user to add the allow rule. This is addressed in the template-transformation increment. `scripts/verify-project.py` prints an informational `artifact_read_rule_hint` (`Read(//<artifact_root>/**)`) computed from the artifact root; it changes no behaviour or exit code.

### Tools on PATH (observed)

Observed with an installed plugin, Claude Code 2.1.330, `claude -p`, local synthetic, 4 sessions; the evidence is kept by the coordinator outside this repository.

- `bin/agentic-*` are on the Bash tool PATH only while the plugin is enabled (exit 127 when it is not).
- The portable rule `Bash(agentic-work-issue:*)` in `.claude/settings.local.json` let the command run without a prompt; without the rule it was denied. The same pattern for the other shims was not tested; `agentic-verify-project --print-rules` prints all the rules (it writes nothing; the Read rule uses the install path it runs from).
- A read-only `next --agent claude` against the owner's Project worked.
- With no `--repo`, `--owner` or `--project` the tool refuses; it does not read them from `tracker.local.yaml`. This equals the baseline behaviour.

### Plugin and project paths

Plugin assets (skills, methodology, roles, templates) refer to each other by relative links, which stay inside the plugin; Claude Code asset files that must name the plugin root use `${CLAUDE_PLUGIN_ROOT}`. Project data is written as a plain, code-formatted project path (`AGENTS.md`, `CLAUDE.md`, `specs/project.md`, `specs/project-rules.md`, `specs/roadmap.md`, `specs/epic-board.md`, `specs/setup-progress.md`, `specs/session-handoff.md`, `specs/NN-*`, `specs/guidelines/*`, `.agents/harnesses/<coordinator>.json`, `.agents/tracker.local.yaml`) and is resolved from the project working directory, never from the plugin and never as a link into the plugin. A test checks that every relative link resolves inside the plugin and flags plugin-owned path families used as project paths.

Use Python 3.10 or later for the portable, local checks:

```sh
python3 -m unittest discover -s tests -v
python3 scripts/verify-project.py --project tests/fixtures/a --coordinator claude
```

The script inspects readiness and reports paths. It locates exactly the selected coordinator's existing v2 configuration as a candidate path when present. It also lists, informationally and without changing the exit code, project paths that shadow plugin-owned capabilities (`plugin_owned_paths_in_project`). It does not parse v2, resolve model or effort, dispatch a worker, or establish what version the client loaded. The reported artifact version is local package metadata.

## Package paths and evidence

Status below is local and synthetic only. Sources are comments on [issue #77](https://github.com/jmartinlabs/agent-project-template/issues/77): 7165742456, 7166402182, 7166540941 (Codex handoff: Codex A/B update and rollback; its traces were re-verified by independent QA), 7166905791, 7167550781, 7167784394, 7167801822, 7168438883. Cited comments are the coordinators' records; this README does not restate their raw output.

| Candidate surface | Packaging reference | Status | Current evidence (local, synthetic) |
| --- | --- | --- | --- |
| Claude Code 2.1.330 | [Plugin guide](https://code.claude.com/docs/en/plugins), `.claude-plugin/plugin.json` | Partial | Verified: `claude plugin validate . --strict` passes locally and in the CI job (run 45656722504 at 2dc8015, which installs the pinned client from the npm registry without a lockfile). Verified in traces: install from cache by git `url`+`sha` plugin source (a `file://` plugin source inside a directory marketplace; adding a git `file://` marketplace is rejected as `invalid_source`); update and rollback by changing the catalog `sha` and running `plugin update`; different versions per project in one profile with local-scope installs; negative N2 (a bad `sha` fails and the installed version stays loadable) and N3 (invalid manifests fail validate). Invocation and synthetic child delegation observed. Plugin-agent permissions: see below. Unrun: effective model/effort. |
| Codex 0.172.0 | [Portable packaging guide](https://developers.openai.com/plugins/build/plugins), root `plugin.json` | Partial | Verified: A/B install, update and rollback with per-project versions and rules, loaded from the profile cache. Observed: invocation and synthetic child delegation (`parent_thread_id`, depth 1). Unrun (quota-gated, not run by decision): explicit v2 model/effort, negative rules, effective child permissions. |
| Antigravity 1.5.17 | [Plugins guide](https://antigravity.google/docs/plugins), `.antigravity-plugin/plugin.json` | Partial | Verified: isolated authentication (API key and OAuth in a temporary profile; habitual state unchanged), discovery, and invocation with correct version, roots and project rule; an unrelated workspace reports "SKILL NO DISPONIBLE". Scope is per-workspace copies, isolated by construction; no shared install, update or rollback was exercised. Model is only requested/accepted. Prompts named the Skill. |
| Local checks | `tests/test_pilot.py`, `.github/workflows/validate.yml` | Verified (local synthetic) | Unittest suite (stdlib only). CI run [45656722504](https://github.com/jmartinlabs/agentic-harness-plugin/actions/runs/45656722504) at 2dc8015 passed all three jobs (unittest on Python 3.10 and 3.12; strict Claude validation with the pinned client). That run does not establish what any client loads at runtime. |

## Known limitations (observed)

Observed in the cited experiments; each is a limitation to design around, not a guarantee.

- N1: the same plugin name from two marketplaces is a silent first-wins. This is unsafe. The evidence rests on the model's statement of the path, not a tool event.
- A plugin enabled in project settings but not installed loads nothing and warns nothing (fails open).
- Side findings, not independently reproduced: a profile-level marketplace name wins over a project's `extraKnownMarketplaces`; `plugin uninstall` empties the project `enabledPlugins`.
- Claude Code pins by the marketplace entry `sha` (git sources). Local-path marketplaces load in place from the source directory, not the cache.
- Rollback was done by re-pinning the catalog `sha` and `plugin update`, or by uninstall and reinstall. No dedicated rollback command was found in the docs read.
- Antigravity isolation was per-workspace copies only. `--strict` validation of the Antigravity manifest warns about precedence against the shared root manifest.
- The Antigravity test harness allowed `BypassSandbox:true` because its regex checked only `CommandLine`. This is a harness lesson, not a product finding.
- Claude's first invocation had Bash denied when the permission path did not match the runtime's local origin.
- The GitHub channel was observed only for Claude Code, local scope, one profile and a public repository (see below). Private repositories, auto-update, a second machine, user/project scope, Windows/Linux and other clients are unrun.
- Hooks and instructions are not enforcement. N4 (a project rule relaxing a gate) is a weak, prompted observation, not enforcement.
- Effective model/effort selection is unverified (only requested/accepted). Codex quota-gated tests are unrun.

### Subagent permissions (observed, Claude Code 2.1.330, local synthetic)

Independently QA'd; local synthetic, 5 sessions. The plugin agent loads as `agentic:<name>` and the child's self-reported tools matched its `tools` list. Frontmatter `hooks` and `permissionMode: bypassPermissions` had no observable effect, but no restricted action was attempted, so "ignored" is the docs' statement and was not exercised. "Child tools are the intersection with the parent's tools" is inferred, with no negative control. A child's file-writing Bash redirection was blocked in a `-p` non-interactive run in default permission mode with no approver ("needs approval and none was available"), not an unconditional deny; a read-only `pwd` ran. The qa-review "read-only" refusals were model compliance (instruction-only), because Bash is in the agent's tools. Not measured: behaviour with Bash pre-approved, `acceptEdits` or bypass on the parent; whether hooks/`permissionMode` are honoured when a restricted action is attempted; any negative control for tools outside the child's list; effective model/effort. Run flags for two of the probes are not recorded in the trace. The template's qa-review adapter read `.agents/roles/qa-review.md` relative to the project; the packaged agents now read `${CLAUDE_PLUGIN_ROOT}/roles/qa-review.md`. That substitution in agent bodies, the packaged agents' behaviour and the SessionStart hook have not been exercised by a client in this increment.

OpenCode and Hermes belong to a later increment. No runtime or v2 profile support is claimed. The readiness diagnostic itself needs no hook, MCP tool or native agent definition (the package now also ships the Claude Code hook and agents above). For the pilot's separate QA experiment, pass the canonical role through the existing bounded native work packet where supported. No hook or existing behavior in the upstream template is removed.

Both marketplace descriptors target the same package at the repository root: `.claude-plugin/marketplace.json` for Claude Code and `.agents/plugins/marketplace.json` for Codex. Select the reviewed Git revision when adding the marketplace. Marketplace validation and repository registration, source resolution, installation, and the effective revision loaded in a session are separate checks. Antigravity uses its own manifest and direct Git/directory distribution path. No marketplace or plugin configuration on the machine is created by the local checks.

## GitHub distribution channel (observed)

Observed with Claude Code 2.1.330, local scope, one temporary profile on one machine, against the public repository `jmartinlabs/agentic-harness-plugin`. The raw logs and traces are local evidence retained by the coordinator, not part of this repository; file numbers cited below refer to that local set. Nothing here is a release: no tags and no releases exist, and no merge is made. `pilot/version-0.1.1` (head `1deaeca7a547a281c86f31960ae538b4a2114f7e`, base `506e52bf0530252ca8a4e0ac8cdc9a4e328758c7`) is a temporary test branch kept until the owner authorizes its deletion.

- Add: `claude plugin marketplace add jmartinlabs/agentic-harness-plugin#<branch>` and `...#<40-hex sha>` both work (04, 08, 12).
- Install and version: the plugin loads from `<profile>/plugins/cache/<marketplace>/agentic/<version>` and `installed_plugins.json` records `gitCommitSha`. `506e52b...` gives 0.1.0 (05, 06); `1deaeca...` gives 0.1.1 (09, 10).
- Rollback: re-pinning the marketplace to `506e52b...` returns to 0.1.0 (11-14).
- `claude plugin marketplace remove` also uninstalls the plugin installed from it (07).
- Transport: the shorthand form tries SSH first and falls back to HTTPS when SSH fails (04, 16); the explicit HTTPS URL form works (18, 20). The fallback was forced with `GIT_SSH_COMMAND=false`; an unreachable or unauthorized key was not tested separately.
- The manifest `version` pins the plugin version (per the docs), so a release flow must bump it. A new commit at an unchanged `version` does not update the plugin (see "Updating and rolling back").
- The update path without re-pinning was later observed; see "Updating and rolling back".
- Not covered: private repositories, auto-update, a second machine, user or project scope, Windows/Linux, other clients.

## Updating and rolling back

Observed with Claude Code 2.1.330, local scope, one temporary profile, on the temporary branch `pilot/version-0.1.1` (increment 9; outputs saved by the coordinator, not in this repository). Local synthetic, one machine.

- A plugin installed from a marketplace that tracks a BRANCH is updated only when the manifest `version` changes. After a docs-only commit with the version unchanged, `marketplace update` refreshed the marketplace clone, but `plugin update` said "already at the latest version" and the installed commit stayed the old one.
- After a commit that bumped the version (0.1.1 to 0.1.2), `plugin update` updated the plugin (new cache directory, new `gitCommitSha`); `plugin update` alone also worked in that case. The new version applies after a restart. Old cache directories are kept.
- The final model session for 0.1.2 was not run; that version was confirmed from the registry only.
- Rollback and exact pins: re-pin with `marketplace add ...#<tag-or-sha>` (observed in increment 3, see "GitHub distribution channel").
- Consequence: every release must bump `version`; consumers who need an exact revision pin a tag or a full sha.

## Provenance and next verification

`methodology/approvals.md` and `roles/qa-review.md` are verbatim from [Agentic Template e9a4616](https://github.com/jmartinlabs/agent-project-template/tree/e9a46160753c5e61f7d3291da9e6a0299f840aa0), from `specs/methodology/approvals.md` and `.agents/roles/qa-review.md` respectively. This staged extraction links a candidate to its upstream baseline. Subsequent distribution must maintain one canonical source.

| SPEC criterion | Candidate evidence and remaining check |
| --- | --- |
| AC-01 | Remaining: static assets and synthetic fixtures only. The definitive mandatory/init/adopt/optional path inventory and an actual GitHub creation/adoption flow are required before any template reduction. No new evidence in this increment. |
| AC-02 | Evidence: local test separates installed artifact, A and B roots and checks a subdirectory; Claude Code A/B local-scope installs resolved the right project from the installed artifact (comment 7165742456; separate profiles, and isolation inside one shared Claude profile is not shown); the GitHub channel installs and loads the pinned version in a session (files 06, 10, 14). Remaining: run the Skill directly and via the intended entry on Codex and Antigravity beyond the observed invocations. |
| AC-03 | Evidence: canonical QA role packaged; Claude plugin agent loads as `agentic:<name>` with the declared tools (comment 7168438883). Remaining: native delegate identity beyond that, limits and effective model/effort are unrun; "read-only" is instruction-only. Treat unsupported explicit selections according to #76 without substituting another route. |
| AC-04 | Evidence: diagnostic covers missing rules, an unrelated repo, a nested checkout boundary and an out-of-root rules path; Claude negatives N2 (bad `sha`) and N3 (invalid manifests). Remaining: missing/disabled/incompatible plugin through the client (an enabled-but-uninstalled plugin fails open), unreadable rules, collision (N1, silent first-wins) and gate-bypass attempts need surface-level tests. |
| AC-05 | Evidence: the script is read-only and fixtures use separate roots; Claude Code and Codex A/B per-project versions, update and rollback (comments 7165742456, 7166540941); the GitHub channel pins by branch or sha, installs 0.1.0/0.1.1 and rolls back by re-pin (04-14). Remaining: update with a new commit at an unchanged `version` (S5) is unrun; B untouched during a GitHub-channel change, auto-update and a second machine are unrun. |
| AC-06 | Evidence: skills, methodology, roles, templates and Claude agents are moved with per-file source blob, destination hash and transformation class in [PROVENANCE.md](PROVENANCE.md), checked by tests (the byte comparison with the template baseline runs only when `AGENTIC_TEMPLATE_CHECKOUT` points to a checkout containing it). The command-line tools and their tests are ported (increment 6; see `PROVENANCE.md`). Remaining: other native adapters (OpenCode review-read and adapters, Codex hook wiring), template-only tooling, and client-level evidence that the moved assets load. No existing capability is retired by this package. |
| AC-07 | Evidence: this slice contains no competing approval rules; `approvals.md` and `qa-review.md` are pinned byte-identical to e9a4616 by `sha256` tests; CI runs 45656722504 (2dc8015) and 45656917820 (506e52b) are green. Independent semantic audit of the moved files against e9a4616 found no drift (increment 5 audit; evidence kept by the coordinator, not in the repository). Remaining: review all common semantic consumers, including the #76 v2 selection rule, and record runtime context loads. |

This README makes no operational claim and no merge, release or migration is requested.

Before claiming operational support, use two separate projects pinned to different candidate versions and an unrelated checkout. Confirm the loaded version in each, exercise an upgrade, rollback and uninstall in one and confirm the other remains unchanged. Capture client version, loaded artifact provenance, permission behavior and actual startup versus invocation resources. A failing core gate or isolation test blocks operational adoption on that surface.
