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

Status below is local and synthetic only. Sources are comments on [issue #77](https://github.com/jmartinlabs/agent-project-template/issues/77): 7165742456, 7166402182, 7166540941 (Codex handoff: Codex A/B update and rollback; its traces were re-verified by independent QA), 7166905791, 7167550781, 7167784394, 7167801822. Cited comments are the coordinators' records; this README does not restate their raw output.

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
- The published https/GitHub channel and private marketplaces are unrun.
- Hooks and instructions are not enforcement. N4 (a project rule relaxing a gate) is a weak, prompted observation, not enforcement.
- Effective model/effort selection is unverified (only requested/accepted). Codex quota-gated tests are unrun.

### Subagent permissions (observed, Claude Code 2.1.330, local synthetic)

Independently QA'd; local synthetic, 5 sessions. The plugin agent loads as `agentic:<name>` and the child's self-reported tools matched its `tools` list. Frontmatter `hooks` and `permissionMode: bypassPermissions` had no observable effect, but no restricted action was attempted, so "ignored" is the docs' statement and was not exercised. "Child tools are the intersection with the parent's tools" is inferred, with no negative control. A child's file-writing Bash redirection was blocked in a `-p` non-interactive run in default permission mode with no approver ("needs approval and none was available"), not an unconditional deny; a read-only `pwd` ran. The qa-review "read-only" refusals were model compliance (instruction-only), because Bash is in the agent's tools. Not measured: behaviour with Bash pre-approved, `acceptEdits` or bypass on the parent; whether hooks/`permissionMode` are honoured when a restricted action is attempted; any negative control for tools outside the child's list; effective model/effort. Run flags for two of the probes are not recorded in the trace. The template's qa-review adapter reads `.agents/roles/qa-review.md` relative to the project; a plugin distribution must point to the plugin copy.

OpenCode and Hermes belong to a later increment. No runtime or v2 profile support is claimed. No hook, MCP tool or native agent definition is required for this diagnostic. For the pilot's separate QA experiment, pass the canonical role through the existing bounded native work packet where supported. No hook or existing behavior in the upstream template is removed.

Both marketplace descriptors target the same package at the repository root: `.claude-plugin/marketplace.json` for Claude Code and `.agents/plugins/marketplace.json` for Codex. Select the reviewed Git revision when adding the marketplace. Marketplace validation and repository registration, source resolution, installation, and the effective revision loaded in a session are separate checks. Antigravity uses its own manifest and direct Git/directory distribution path. No marketplace or plugin configuration on the machine is created by the local checks.

## Provenance and next verification

`methodology/approvals.md` and `roles/qa-review.md` are verbatim from [Agentic Template e9a4616](https://github.com/jmartinlabs/agent-project-template/tree/e9a46160753c5e61f7d3291da9e6a0299f840aa0), from `specs/methodology/approvals.md` and `.agents/roles/qa-review.md` respectively. This staged extraction links a candidate to its upstream baseline. Subsequent distribution must maintain one canonical source.

| SPEC criterion | Candidate evidence and remaining check |
| --- | --- |
| AC-01 | Static assets and synthetic fixtures only. The definitive mandatory/init/adopt/optional path inventory and an actual GitHub creation/adoption flow are required before any template reduction. |
| AC-02 | Local test separates installed artifact, A and B roots and checks a subdirectory. Run the installed Skill directly and via the intended entry on each candidate runtime. |
| AC-03 | Canonical QA role packaged. Native delegate identity, limits and effective model/effort are unrun. Treat unsupported explicit selections according to #76 without substituting another route. |
| AC-04 | Diagnostic covers missing rules, an unrelated repo, a nested checkout boundary and an out-of-root rules path. Missing/disabled/incompatible plugin, unreadable rules through the client, collision and attempts to bypass gates need surface-level tests. |
| AC-05 | The script is read-only and fixtures use separate roots. Native pin, update/rollback and uninstall without changing B are unrun. |
| AC-06 | The portable slice is an entry Skill, approvals, a QA role and a read-only utility. Existing orchestration, remaining canonical roles/skills, Relay, work-issue, handoff, measurement, native adapters, hooks and shared validators remain to classify and move with evidence. No existing capability is retired by the pilot. |
| AC-07 | This slice contains no competing approval rules. Review all common semantic consumers at extraction, including orchestrate step 4 and the #76 v2 selection rule. Runtime context loads and independent QA beyond the standalone tests remain to be recorded. |

Before claiming operational support, use two separate projects pinned to different candidate versions and an unrelated checkout. Confirm the loaded version in each, exercise an upgrade, rollback and uninstall in one and confirm the other remains unchanged. Capture client version, loaded artifact provenance, permission behavior and actual startup versus invocation resources. A failing core gate or isolation test blocks operational adoption on that surface.
