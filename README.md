# Agentic Harness · pilot candidate

This is the first vertical candidate for [SPEC #77](https://github.com/jmartinlabs/agent-project-template/issues/77#issuecomment-7165024336). It packages one read-only project readiness Skill, the approvals methodology, a canonical QA role and a diagnostic script. The pilot does not replace an existing harness. Licensed under the MIT licence (`LICENSE`, holder jmartinlabs, 2026).

`orchestrate` is not part of this candidate. `methodology/approvals.md` is the canonical approvals source; where it mentions `orchestrate`, it refers to the template's orchestrate Skill, which the pilot does not ship.

Use Python 3.10 or later for the portable, local checks:

```sh
python3 -m unittest discover -s tests -v
python3 scripts/verify-project.py --project tests/fixtures/a --coordinator claude
```

The script inspects readiness and reports paths. It locates exactly the selected coordinator's existing v2 configuration as a candidate path when present. It does not parse v2, resolve model or effort, dispatch a worker, or establish what version the client loaded. The reported artifact version is local package metadata.

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

Independently QA'd; local synthetic, 5 sessions. The plugin agent loads as `agentic:<name>` and the child's self-reported tools matched its `tools` list. Frontmatter `hooks` and `permissionMode: bypassPermissions` had no observable effect, but no restricted action was attempted, so "ignored" is the docs' statement and was not exercised. "Child tools are the intersection with the parent's tools" is inferred, with no negative control. A child's file-writing Bash redirection was blocked in a `-p` non-interactive run in default permission mode with no approver ("needs approval and none was available"), not an unconditional deny; a read-only `pwd` ran. The qa-review "read-only" refusals were model compliance (instruction-only), because Bash is in the agent's tools. Not measured: behaviour with Bash pre-approved, `acceptEdits` or bypass on the parent; whether hooks/`permissionMode` are honoured when a restricted action is attempted; any negative control for tools outside the child's list; effective model/effort. Run flags for two of the probes are not recorded in the trace. The template's qa-review adapter reads `.agents/roles/qa-review.md` relative to the project; a plugin distribution must point to the plugin copy.

OpenCode and Hermes belong to a later increment. No runtime or v2 profile support is claimed. No hook, MCP tool or native agent definition is required for this diagnostic. For the pilot's separate QA experiment, pass the canonical role through the existing bounded native work packet where supported. No hook or existing behavior in the upstream template is removed.

Both marketplace descriptors target the same package at the repository root: `.claude-plugin/marketplace.json` for Claude Code and `.agents/plugins/marketplace.json` for Codex. Select the reviewed Git revision when adding the marketplace. Marketplace validation and repository registration, source resolution, installation, and the effective revision loaded in a session are separate checks. Antigravity uses its own manifest and direct Git/directory distribution path. No marketplace or plugin configuration on the machine is created by the local checks.

## GitHub distribution channel (observed)

Observed with Claude Code 2.1.330, local scope, one temporary profile on one machine, against the public repository `jmartinlabs/agentic-harness-plugin`. The raw logs and traces are local evidence retained by the coordinator, not part of this repository; file numbers cited below refer to that local set. Nothing here is a release: no tags and no releases exist, and no merge is made. `pilot/version-0.1.1` (head `1deaeca7a547a281c86f31960ae538b4a2114f7e`, base `506e52bf0530252ca8a4e0ac8cdc9a4e328758c7`) is a temporary test branch kept until the owner authorizes its deletion.

- Add: `claude plugin marketplace add jmartinlabs/agentic-harness-plugin#<branch>` and `...#<40-hex sha>` both work (04, 08, 12).
- Install and version: the plugin loads from `<profile>/plugins/cache/<marketplace>/agentic/<version>` and `installed_plugins.json` records `gitCommitSha`. `506e52b...` gives 0.1.0 (05, 06); `1deaeca...` gives 0.1.1 (09, 10).
- Rollback: re-pinning the marketplace to `506e52b...` returns to 0.1.0 (11-14).
- `claude plugin marketplace remove` also uninstalls the plugin installed from it (07).
- Transport: the shorthand form tries SSH first and falls back to HTTPS when SSH fails (04, 16); the explicit HTTPS URL form works (18, 20). The fallback was forced with `GIT_SSH_COMMAND=false`; an unreachable or unauthorized key was not tested separately.
- The manifest `version` pins the plugin version (per the docs), so a release flow must bump it. A new commit at an unchanged `version` (S5) is unrun.
- Not verified: the update path without re-pinning (a plain `plugin update` after a new commit on the tracked branch, with or without `marketplace update`) was only reported by the executor and no output was saved; do not rely on it. A new commit at an unchanged manifest `version` was not tested.
- Not covered: private repositories, auto-update, a second machine, user or project scope, Windows/Linux, other clients.

## Provenance and next verification

`methodology/approvals.md` and `roles/qa-review.md` are verbatim from [Agentic Template e9a4616](https://github.com/jmartinlabs/agent-project-template/tree/e9a46160753c5e61f7d3291da9e6a0299f840aa0), from `specs/methodology/approvals.md` and `.agents/roles/qa-review.md` respectively. This staged extraction links a candidate to its upstream baseline. Subsequent distribution must maintain one canonical source.

| SPEC criterion | Candidate evidence and remaining check |
| --- | --- |
| AC-01 | Remaining: static assets and synthetic fixtures only. The definitive mandatory/init/adopt/optional path inventory and an actual GitHub creation/adoption flow are required before any template reduction. No new evidence in this increment. |
| AC-02 | Evidence: local test separates installed artifact, A and B roots and checks a subdirectory; Claude Code A/B local-scope installs resolved the right project from the installed artifact (comment 7165742456; separate profiles, and isolation inside one shared Claude profile is not shown); the GitHub channel installs and loads the pinned version in a session (files 06, 10, 14). Remaining: run the Skill directly and via the intended entry on Codex and Antigravity beyond the observed invocations. |
| AC-03 | Evidence: canonical QA role packaged; Claude plugin agent loads as `agentic:<name>` with the declared tools (comment 7168438883). Remaining: native delegate identity beyond that, limits and effective model/effort are unrun; "read-only" is instruction-only. Treat unsupported explicit selections according to #76 without substituting another route. |
| AC-04 | Evidence: diagnostic covers missing rules, an unrelated repo, a nested checkout boundary and an out-of-root rules path; Claude negatives N2 (bad `sha`) and N3 (invalid manifests). Remaining: missing/disabled/incompatible plugin through the client (an enabled-but-uninstalled plugin fails open), unreadable rules, collision (N1, silent first-wins) and gate-bypass attempts need surface-level tests. |
| AC-05 | Evidence: the script is read-only and fixtures use separate roots; Claude Code and Codex A/B per-project versions, update and rollback (comments 7165742456, 7166540941); the GitHub channel pins by branch or sha, installs 0.1.0/0.1.1 and rolls back by re-pin (04-14). Remaining: update with a new commit at an unchanged `version` (S5) is unrun; B untouched during a GitHub-channel change, auto-update and a second machine are unrun. |
| AC-06 | Remaining: the portable slice is an entry Skill, approvals, a QA role and a read-only utility. Existing orchestration, remaining canonical roles/skills, Relay, work-issue, handoff, measurement, native adapters, hooks and shared validators remain to classify and move with evidence. No existing capability is retired by the pilot. |
| AC-07 | Evidence: this slice contains no competing approval rules; `approvals.md` and `qa-review.md` are pinned byte-identical to e9a4616 by `sha256` tests; CI runs 45656722504 (2dc8015) and 45656917820 (506e52b) are green. Remaining: review all common semantic consumers at extraction, including orchestrate step 4 and the #76 v2 selection rule, and record runtime context loads. |

This README makes no operational claim and no merge, release or migration is requested.

Before claiming operational support, use two separate projects pinned to different candidate versions and an unrelated checkout. Confirm the loaded version in each, exercise an upgrade, rollback and uninstall in one and confirm the other remains unchanged. Capture client version, loaded artifact provenance, permission behavior and actual startup versus invocation resources. A failing core gate or isolation test blocks operational adoption on that surface.
