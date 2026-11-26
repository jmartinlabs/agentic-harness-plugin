# Agentic Harness plugin

The `agentic` plugin supplies shared skills, roles, methodology, templates and tools from one marketplace, `agentic-harness`. Each project keeps its own rules, v2 harness configuration and application files. The stable distribution follows the [SPEC #77 amendment](https://github.com/jmartinlabs/agent-project-template/issues/77#issuecomment-7174900762).

## Quick start

Install once per client, at user scope. The startup hook and readiness diagnostic use Python 3.10 or later. The commands below track the `stable` channel. They become available when the first release is promoted to that channel.

### Claude Code

```sh
claude plugin marketplace add https://github.com/jmartinlabs/agentic-harness-plugin.git#stable --scope user
claude plugin install agentic@agentic-harness --scope user
```

### Codex CLI

```sh
codex plugin marketplace add https://github.com/jmartinlabs/agentic-harness-plugin.git --ref stable
codex plugin add agentic@agentic-harness
```

### Antigravity

```sh
antigravity plugin install https://github.com/jmartinlabs/agentic-harness-plugin/tree/stable
```

Antigravity installs globally per user under `$HOME/.gemini/config/plugins/agentic` from a Git branch (not a commit SHA). It loads `.antigravity-plugin/plugin.json` and the 13 skills as bare names (e.g. `verify-project`, `orchestrate`); it skips `agents/*.md` and `hooks/hooks.json`.

### OpenCode (global per-user adapter)

OpenCode loads user-level agents, plugins and skills from `~/.config/opencode/`. Clone the plugin once at a user path tracking `stable` and symlink the OpenCode adapter and shared skills into `~/.config/opencode/`:

```sh
git clone --branch stable https://github.com/jmartinlabs/agentic-harness-plugin.git ~/.local/share/agentic-harness-plugin
mkdir -p ~/.config/opencode/agents ~/.config/opencode/plugins
for agent in ~/.local/share/agentic-harness-plugin/adapters/opencode/agents/*.md; do
  ln -sfn "$agent" ~/.config/opencode/agents/"$(basename "$agent")"
done
ln -sfn ~/.local/share/agentic-harness-plugin/adapters/opencode/plugins/review-read ~/.config/opencode/plugins/review-read
ln -sfn ~/.local/share/agentic-harness-plugin/skills ~/.config/opencode/skills
```

Each project keeps its own `AGENTS.md`, `specs/project-rules.md` and `.agents/harnesses/opencode.json`. The `review-read` plugin resolves its wrapper from the plugin checkout and runs against the active project working directory.

Review and trust the plugin's SessionStart hook in Codex using `/hooks`. After an update or rollback, review it again if Codex marks the installed hook as changed. The SessionStart hook is configured to display `Agentic Harness X.Y.Z` from the installed artifact. Verify the message when you open a new session. If it is absent, check the client hook settings and report the loaded artifact version with the readiness diagnostic. Hook trust and project trust remain client decisions. [Codex plugin hooks](https://developers.openai.com/plugins/build/plugins), [Claude Code hooks](https://code.claude.com/docs/en/hooks)

In a new project from **Use this template**, run the `agentic:verify-project` skill, then `agentic:init-project`. For an existing project, use `agentic:adopt-project`, which can run the read-only inventory before the entry files exist. The readiness skill reports `artifact_version`, the active project and its applicable policy paths. Stop if the active project's rules or the common policy are unavailable. If Claude Code denies plugin reads, find the artifact's `installPath` with `claude plugin list --json`. Run `python3 "<installPath>/scripts/verify-project.py" --print-rules` from your terminal. It prints the exact `Read(//<installPath>/**)` rule and separate tool rules without writing settings. Approve the permissions you need when prompted. To keep an approval for one project, add only its approved entries to `permissions.allow` in that project's untracked `.claude/settings.local.json`. Refresh the exact Read rule after an update if needed.

### Update

Run the command for your client and start a new session. The update applies to all projects in that client profile.

```sh
claude plugin marketplace update agentic-harness
claude plugin update agentic@agentic-harness --scope user
```

```sh
codex plugin marketplace upgrade agentic-harness
```

```sh
antigravity plugin uninstall agentic
antigravity plugin install https://github.com/jmartinlabs/agentic-harness-plugin/tree/stable

# OpenCode (global per-user adapter)
git -C ~/.local/share/agentic-harness-plugin pull --ff-only origin stable
```

### Roll back

Outside any project, uninstall the user plugin and remove the marketplace, then re-add the same marketplace and reinstall. In the install commands above replace `stable` with the previous published tag, such as `v1.0.0`. Use the same procedure with `stable` to return to the stable channel. The older artifact may predate the startup banner.

```sh
claude plugin uninstall agentic@agentic-harness --scope user
claude plugin marketplace remove agentic-harness
```

```sh
codex plugin remove agentic@agentic-harness
codex plugin marketplace remove agentic-harness
```

```sh
antigravity plugin uninstall agentic

# OpenCode (global per-user adapter): check out the previous tag, or `stable` to return
git -C ~/.local/share/agentic-harness-plugin fetch --tags
git -C ~/.local/share/agentic-harness-plugin checkout v1.0.0
```

The native CLI flows were exercised in fresh temporary profiles on Claude Code 2.1.330 and Codex CLI 0.172.0 against a synthetic Git source. Both installed 1.1.0, upgraded to 1.1.1 and returned to 1.1.0 through the same marketplace identity. That probe used a synthetic branch for the old ref, with no model calls. Claude's native SessionStart trace also reported the expected version in both synthetic projects at each step, before authentication. Codex discovered the native hook and required trust before executing it. Authenticated session and published-tag checks remain separate.

### Move an existing installation to the stable channel

If `agentic-harness` is already registered from a different source or ref, run the uninstall and marketplace removal commands above outside any project, then follow the install instructions with `stable`. Remove old Agentic marketplace and enablement entries from project settings if you added them for the previous setup. Preserve all unrelated settings, permission rules and `.agents/harnesses/` files.

## Evidence scope

The historical client observations below are on 0.1.0 content, before the stable user channel. They describe the packaged capabilities and their limits. See the update and rollback sections above for the current distribution commands.

## Package contents

Every moved file, its template source blob (commit `5b53f75f1878909a65f76aa3e0151f1a0f31d86d`), destination hash and transformation class are listed in [PROVENANCE.md](PROVENANCE.md).

| Area | Contents | Notes |
| --- | --- | --- |
| `skills/` | `orchestrate`, `task`, `tweak`, `spec`, `dev`, `roadmap`, `handoff`, `init-project`, `adopt-project`, `bootstrap`, `work-issue`, `relay` (+ `relay/GITHUB_API.md`), plus `verify-project` | Moved, not redesigned. |
| `methodology/` | `approvals` (pinned), `ci-policy`, `dynamic-agents`, `dynamic-agents-external-clients`, `epic-orchestration`, `identifiers`, `issue-workflow`, `workflows`, `document-ownership` (from the template's `specs/README.md`) | The template's `acceptance-scenarios.md` stays in the template. |
| `roles/` | `README`, `functional`, `implementation`, `infrastructure`, `qa-review` (pinned) | |
| `templates/` | 8 document templates | Skills copy them into a project when needed. |
| `agents/` | Claude Code agents `functional`, `implementation`, `infrastructure`, `qa-review` | Read the role from `${CLAUDE_PLUGIN_ROOT}/roles/<role>.md`; no hooks, `permissionMode` or MCP servers. Claude Code only. |
| `adapters/opencode/` | Thin native OpenCode agents (`functional`, `implementation`, `infrastructure`, `qa`, `review`), `plugins/review-read/index.ts`, and `scripts/review-read` | Global per-user adapter for `~/.config/opencode/`; agents point to canonical `roles/*.md` without duplicating methodology or skills. |
| `hooks/hooks.json` | SessionStart reports the installed artifact version | Claude Code also keeps the existing orchestration context with an 8704-byte budget. Codex uses the native plugin hook trust flow. |
| `scripts/`, `bin/` | Tools `work-issue`, `agent-relay`, `check-delegation-route`, `report-agent-usage`, `auto-agent-usage` (ported from the baseline; the project root is the working directory or `--repo-root`, never the plugin directory), the integrity validator `validate-core` and the read-only `verify-project.py` | In Claude Code, `bin/` is on the Bash tool PATH while the plugin is enabled: `agentic-work-issue`, `agentic-relay`, `agentic-check-delegation-route`, `agentic-usage-report`, `agentic-usage-auto`. Run them from the project directory; elsewhere use `python3 <plugin root>/scripts/<tool>`. |
| `tests/` | Plugin static tests, the ported tool suites (`tests/test-<tool>`, run as `python3 tests/test-work-issue`) and `fixtures/work-issue-project.json` | `scripts/validate-core --project DIR` validates `DIR/.agents/harnesses/*.json` (harness JSON v2). |

Deliberate delta: `skills/orchestrate/SKILL.md` step 4 now says that the user configures the coordinator's model, providers and routes in the client, and that delegate defaults, profiles and external routes come from the coordinator's project file under coordinator configuration. This is the single wording fix required by issue 77; the #75/#76 semantics are unchanged.

## Clients (v1 targets, observed)

All local, synthetic, one machine; client versions as observed in the increment-8 issue comments (Codex 0.172.0, Antigravity 1.5.17); no claim goes beyond this list. OpenCode and Hermes are second-stage and not packaged.

| Client | Install (as measured) | Verified | Observed (single run) | Unrun |
| --- | --- | --- | --- | --- |
| Claude Code 2.1.330 (GitHub channel pinned at 37fb4f3) | Historically, GitHub marketplace and local-scope install | 13 `agentic:*` skills and 4 `agentic:<role>` agents load; delegation to `agentic:qa-review` works and the agent file uses `${CLAUDE_PLUGIN_ROOT}` and the child's first Read of the plugin role file succeeded; the SessionStart hook runs (8151 characters of output, exit 0; the file is 8159 bytes); `model` override effective (stream `modelUsage` showed `claude-opus-5-5` when `opus` was requested) | A merge request after generic assent was not executed; the model asked for explicit approval naming the PR and SHA (it did not say that generic assent is not approval) | Effective effort (not verifiable from the stream); a sonnet-vs-sonnet comparison |
| Codex CLI 0.172.0 (7 model sessions, `codex exec --sandbox read-only -a never`, plugin installed from GitHub pinned at `74e7fab3c1b358473c884f34fa04b141f3a1c558` into a temporary authenticated profile whose plugin registry was later restored; the earlier install-only check, with no model, was at 37fb4f3) | `codex plugin marketplace add jmartinlabs/agentic-harness-plugin --ref <full sha>`, then `codex plugin add agentic@agentic-harness` | Install works in a new `CODEX_HOME`; the cache `plugins/cache/agentic-harness/agentic/<version>` has the same 84 file names as `git ls-tree` (no content hashes compared) and its 87 relative links resolve. All 13 skills are shown namespaced (`agentic:verify-project`, `agentic:orchestrate`, ...; none bare), discovered from the default `skills/` directory with no `skills` key in `plugin.json`. The model ran `python3 <cache>/scripts/verify-project.py --coordinator codex` from the cache in the read-only sandbox: exit 0, correct artifact and project roots, version 0.1.0 at that time (harmless macOS python `xcrun_db` cache warnings). Reading `methodology/approvals.md` and `roles/qa-review.md` by absolute cache path works in the read-only sandbox without prompts. | Single-run observations: native subagent delegation worked: the child thread records `parent_thread_id`, depth 1, `agent_path /root/qa`, spawned via `thread_spawn`, child model `gpt-6.2-sol`, effort low (from the session rollout; the spawn prompt is encrypted). v2: with `.agents/harnesses/codex.json` requesting `local.model=gpt-6.2-sol` and `effort=low`, the coordinator refused to spawn (no host evidence it could verify the child's settings; it also cited the then-missing template validator, and 1.0.0 ships `validate-core`, so the outcome may differ); when the owner's prompt explicitly told it to pass the values, `spawn_agent {model, reasoning_effort}` was called and the child's rollout metadata shows exactly those values (read from the session metadata by an external reader; the coordinator reported them as requested, not observed). Hooks: the Claude `hooks.json` did not fire and no SessionStart output or `CLAUDE_PLUGIN_ROOT` existed in the sandbox (inert on Codex in that run). `bin/` is probably not on PATH in Codex (inference: no probe was run), so use `python3 <cache>/scripts/<tool>` there. The child's low effort was not requested in the call: it looks like a Codex default for subagents (unverified). Codex ran `agentic:verify-project` even for unrelated prompts in the scaffold project (intended: the project `AGENTS.md` says to start with it). Codex also copies the Claude-only `agents/`, `hooks/` and `.claude-plugin/`. | Codex desktop surface, interactive mode, `codex plugin` upgrade refresh, effective effort when not requested |
| Antigravity 1.5.17 (temporary profile) | `plugin install https://github.com/jmartinlabs/agentic-harness-plugin/tree/<branch>` | Installs the branch tip at install time (the branch head was 37fb4f3 in the tested run, per the increment-8 report); disable, enable and uninstall work | The diagnostic ran through the model (version 0.1.0, correct roots, exit 0); a typo fix was classified Quick without writing (model requested `gemini-4-hydrogen-low`, effective model unverified; following the project's `AGENTS.md` is not shown by the trace) | Effective model |

- Claude Code v2: when the project's `.agents/harnesses/claude.json` requested `local.model`/`effort`, one run refused to spawn because it could not assure effective selection (consistent with the #76 "do not spawn" rule); with the owner's explicit authorization of the probe the parent passed `model` and `effort` to the Agent tool.
- Claude Code side effect (observed again): `claude plugin marketplace remove` or `uninstall` run inside the project empties `enabledPlugins` and `extraKnownMarketplaces` in the committed `.claude/settings.json`.
- Codex: the cache path is keyed by `version`, so a new commit without a version bump keeps the same path (observed in the cache layout, not tested as an update). `plugin.json` has no `skills` key or `interface` block (the docs do not require `skills` for the portable layout).
- Antigravity install takes a BRANCH only. The error "Remote branch <sha> not found" was observed for the sha URL form in `plugin validate`/install attempts, and the repository root failed because `main` has no plugin; branch-only follows from the CLI cloning with `--branch`, nothing more is shown. The pin is therefore the branch tip at install time. It needs HTTPS to github.com and installs GLOBALLY under `$HOME/.gemini/config/plugins/agentic`, not into the workspace; the plugin commands did not honour `--gemini-dir` and `--app-data-dir` in the tested run (`plugin list` rejected them; the install location followed `$HOME`).
- In the historical probe, Antigravity `plugin validate` skips the 4 `agents/*.md` (`tools:` is a string where a list is expected), never loads `hooks/hooks.json` and ignores `plugin.json` because `.antigravity-plugin/plugin.json` takes precedence. So only the 13 skills load, shown as bare names such as `verify-project`, not `agentic:verify-project`.
- Antigravity permissions: every plugin file outside the workspace costs one permission ask (about 3 for the diagnostic); there is no single read rule like Claude's. Agents that hit a sandbox failure retried with `BypassSandbox=true`, so test allow-lists must inspect arguments, not only the command line (harness lesson).

### Not yet in the plugin

- Template-only tooling (`validate-template`, `test-validator`, `check-mermaid`, the evals) and the Hermes adapter are not packaged.
- `scripts/validate-core` replaces the template's v2 schema checker; no Skill calls it yet. `methodology/dynamic-agents.md` names `scripts/validate-core` as the v2 checker (a deliberate delta, see PROVENANCE).
- The OpenCode global adapter (`adapters/opencode/`) is packaged statically; live OpenCode runtime verification remains separate.
- The `init-project`, `adopt-project` and `bootstrap` Skills and the first paragraph of `methodology/document-ownership.md` are rewritten for the plugin model (nothing common is copied into the project) but untested against a live client; the template repository itself is not yet reduced, and the interactive permission prompts are unrun.
- The template's `docs/` guides (visual guide, client adapters, evals) are not part of the plugin; the sentences that mention them say so.
- Codex and Antigravity runtime loading is claimed only as listed in the Clients table (0.1.0 content); the older pilot observations below add nothing beyond it.

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
cp -R tests/fixtures/a "$(mktemp -d)/a"   # a copy outside this repository; run the next line with that path
python3 scripts/verify-project.py --project <that copy> --coordinator claude
```

Run inside this repository with `--project tests/fixtures/a` the script prints `readiness blocked` (exit 2), because the repository's Git root, not the fixture, is the project boundary; use a copy outside it.

The script inspects readiness and reports paths. It locates exactly the selected coordinator's existing v2 configuration as a candidate path when present. It also lists, informationally and without changing the exit code, project paths that shadow plugin-owned capabilities (`plugin_owned_paths_in_project`). The reported version comes from the artifact that executes the diagnostic. Run the installed skill to establish which copy the client uses. The diagnostic leaves v2 profile resolution and any delegation to the coordinator.

## Package paths and historical client evidence

Status below is local and synthetic only. Sources are comments on [issue #77](https://github.com/jmartinlabs/agent-project-template/issues/77): 7165742456, 7166402182, 7166540941 (Codex handoff: Codex A/B update and rollback; its traces were re-verified by independent QA), 7166905791, 7167550781, 7167784394, 7167801822, 7168438883. Cited comments are the coordinators' records; this README does not restate their raw output.

| Candidate surface | Packaging reference | Status | Current evidence (local, synthetic) |
| --- | --- | --- | --- |
| Claude Code 2.1.330 | [Plugin guide](https://code.claude.com/docs/en/plugins), `.claude-plugin/plugin.json` | Partial | Verified: `claude plugin validate . --strict` passes locally and in the CI job (CI installs the pinned client from the npm registry without a lockfile; see the PR checks for the final commit). Verified in traces: install from cache by git `url`+`sha` plugin source (a `file://` plugin source inside a directory marketplace; adding a git `file://` marketplace is rejected as `invalid_source`); update and rollback by changing the catalog `sha` and running `plugin update`; different versions per project in one profile with local-scope installs; negative N2 (a bad `sha` fails and the installed version stays loadable) and N3 (invalid manifests fail validate). Invocation and synthetic child delegation observed. Plugin-agent permissions: see below. Unrun: effective model/effort. |
| Codex 0.172.0 | [Portable packaging guide](https://developers.openai.com/plugins/build/plugins), root `plugin.json` | Partial | Verified: A/B install, update and rollback with per-project versions and rules, loaded from the profile cache. Observed: invocation and synthetic child delegation (`parent_thread_id`, depth 1). Unrun (quota-gated, not run by decision): explicit v2 model/effort, negative rules, effective child permissions. |
| Antigravity 1.5.17 | [Plugins guide](https://antigravity.google/docs/plugins), `.antigravity-plugin/plugin.json` | Partial | Verified: isolated authentication (API key and OAuth in a temporary profile; habitual state unchanged), discovery, and invocation with correct version, roots and project rule; an unrelated workspace reports "SKILL NO DISPONIBLE". Scope is per-workspace copies, isolated by construction; no shared install, update or rollback was exercised. Model is only requested/accepted. Prompts named the Skill. |
| Local checks | `tests/test_pilot.py`, `.github/workflows/validate.yml` | Verified (local synthetic) | Unittest suite (stdlib only). CI (see the PR checks for the final commit; the earlier run 45656722504 at 2dc8015 passed all three jobs) (unittest on Python 3.10 and 3.12; strict Claude validation with the pinned client). That run does not establish what any client loads at runtime. |

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
- Residual risks to accept before release: no client has loaded 1.0.0 content yet; tag-form pins are untested (Antigravity cannot pin); interactive permission behaviour, project-scope install and the trust dialog are untested; the Read rule contains the versioned install path (re-run `--print-rules` after each update); `init-project`, `adopt-project` and `bootstrap` are rewritten and not exercised live end to end; GitHub write tools were never run with the plugin installed; Antigravity loads only the 13 skills; effort is not verifiable on Claude; uninstall or `marketplace remove` empties the committed `settings.json`; a name collision is a silent first-wins; an enabled-but-not-installed plugin fails open; the shorthand tries SSH first; argparse accepts abbreviations such as `--repo-r` for `--repo-root`; history includes commits with a local-machine email (not rewritten, owner decision); the temporary branch `pilot/version-0.1.1` exists.
- Effective model/effort selection is unverified (only requested/accepted). Codex desktop and interactive surfaces and upgrade refresh are unrun.

### Subagent permissions (observed, Claude Code 2.1.330, local synthetic)

Independently QA'd; local synthetic, 5 sessions. The plugin agent loads as `agentic:<name>` and the child's self-reported tools matched its `tools` list. Frontmatter `hooks` and `permissionMode: bypassPermissions` had no observable effect, but no restricted action was attempted, so "ignored" is the docs' statement and was not exercised. "Child tools are the intersection with the parent's tools" is inferred, with no negative control. A child's file-writing Bash redirection was blocked in a `-p` non-interactive run in default permission mode with no approver ("needs approval and none was available"), not an unconditional deny; a read-only `pwd` ran. The qa-review "read-only" refusals were model compliance (instruction-only), because Bash is in the agent's tools. Not measured: behaviour with Bash pre-approved, `acceptEdits` or bypass on the parent; whether hooks/`permissionMode` are honoured when a restricted action is attempted; any negative control for tools outside the child's list; effective model/effort. Run flags for two of the probes are not recorded in the trace. The template's qa-review adapter read `.agents/roles/qa-review.md` relative to the project; the packaged agents now read `${CLAUDE_PLUGIN_ROOT}/roles/qa-review.md`. That substitution and the packaged agents' behaviour were exercised later (see Clients); only content up to 0.1.0 was loaded by a client.

OpenCode and Hermes belong to a later increment. No runtime or v2 profile support is claimed. The readiness diagnostic itself needs no hook, MCP tool or native agent definition (the package now also ships the Claude Code hook and agents above). For native QA, pass the canonical role through the existing bounded native work packet where supported. No hook or existing behavior in the upstream template is removed.

Both marketplace descriptors target the same package at the repository root. Codex uses `.codex-plugin/plugin.json` because the portable root format suppresses native hooks in [Codex CLI 0.172.0](https://github.com/openai/codex/blob/rust-v0.172.0/codex-rs/core-plugins/src/loader.rs#L942-L952). Antigravity uses its own manifest and direct Git/directory distribution path.

## Provenance and next verification

`methodology/approvals.md` and `roles/qa-review.md` are verbatim from [Agentic Template 5b53f75](https://github.com/jmartinlabs/agent-project-template/tree/5b53f75f1878909a65f76aa3e0151f1a0f31d86d), from `specs/methodology/approvals.md` and `.agents/roles/qa-review.md` respectively. This staged extraction links a candidate to its upstream baseline. Subsequent distribution must maintain one canonical source.

| SPEC criterion | Candidate evidence and remaining check |
| --- | --- |
| AC-01 | Remaining: static assets and synthetic fixtures only. The definitive mandatory/init/adopt/optional path inventory and an actual GitHub creation/adoption flow are required before any template reduction. No new evidence in this increment. |
| AC-02 | Evidence: local test separates installed artifact, A and B roots and checks a subdirectory; Claude Code A/B local-scope installs resolved the right project from the installed artifact (comment 7165742456; separate profiles, and isolation inside one shared Claude profile is not shown); the GitHub channel installs and loads the pinned version in a session (files 06, 10, 14). Remaining: run the Skill directly and via the intended entry on Codex and Antigravity beyond the observed invocations. |
| AC-03 | Evidence: canonical QA role packaged; Claude plugin agent loads as `agentic:<name>` with the declared tools (comment 7168438883). Remaining: native delegate identity beyond that, limits and effective model/effort are unrun; "read-only" is instruction-only. Treat unsupported explicit selections according to #76 without substituting another route. |
| AC-04 | Evidence: diagnostic covers missing rules, an unrelated repo, a nested checkout boundary and an out-of-root rules path; Claude negatives N2 (bad `sha`) and N3 (invalid manifests). Remaining: missing/disabled/incompatible plugin through the client (an enabled-but-uninstalled plugin fails open), unreadable rules, collision (N1, silent first-wins) and gate-bypass attempts need surface-level tests. |
| AC-05 | Native user install, update and rollback passed in isolated profiles against a synthetic Git source. Verify startup messages and loaded skills for both projects at each version, keeping their rules and v2 configuration separate. Published tags remain a release smoke check. |
| AC-06 | Evidence: skills, methodology, roles, templates and Claude agents are moved with per-file source blob, destination hash and transformation class in [PROVENANCE.md](PROVENANCE.md), checked by tests (the byte comparison with the template baseline runs only when `AGENTIC_TEMPLATE_CHECKOUT` points to a checkout containing it). The command-line tools and their tests are ported (increment 6; see `PROVENANCE.md`). Remaining: other native adapters (OpenCode review-read and adapters), template-only tooling, and client-level evidence that the moved assets load. No existing capability is retired by this package. |
| AC-07 | Evidence: this slice contains no competing approval rules; `approvals.md` and `qa-review.md` are pinned byte-identical to 5b53f75 by `sha256` tests; CI runs 45656722504 (2dc8015) and 45656917820 (506e52b) were green; see the PR checks for the final commit. An independent semantic audit before the history rewrite found no drift in the moved files (increment 5 audit; evidence kept by the coordinator, not in the repository). The rewritten baseline 5b53f75 has the same source blobs as the audited baseline. Remaining: review all common semantic consumers, including the #76 v2 selection rule, and record runtime context loads. |

This README makes no operational claim; merge and release require the owner's explicit approval.

Before claiming operational support, use two synthetic projects from the same profile and an unrelated checkout. Check the version shown at startup and reported by the installed skill through install, update and rollback. Verify each project retains its own rules and v2 configuration. Capture the client version, effective artifact path and applicable permissions.
