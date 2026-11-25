# Agentic Harness · pilot candidate

This is the first vertical candidate for [SPEC #77](https://github.com/jmartinlabs/agent-project-template/issues/77#issuecomment-7165024336). It packages one read-only project readiness Skill, the approvals methodology, a canonical QA role and a diagnostic script. The pilot does not replace an existing harness.

Use Python 3.10 or later for the portable, local checks:

```sh
python3 -m unittest discover -s tests -v
python3 scripts/verify-project.py --project tests/fixtures/a --coordinator claude
```

The script inspects readiness and reports paths. It locates exactly the selected coordinator's existing v2 configuration as a candidate path when present. It does not parse v2, resolve model or effort, dispatch a worker, or establish what version the client loaded. The reported artifact version is local package metadata.

## Package paths and evidence

| Candidate surface | Packaging reference | Current evidence |
| --- | --- | --- |
| Claude Code | [Plugin guide](https://code.claude.com/docs/en/plugins), `.claude-plugin/plugin.json` | Manifest and common Skill present. Installed discovery, direct invocation and native independent QA experiment unrun. |
| Codex | [Portable packaging guide](https://developers.openai.com/plugins/build/plugins), root `plugin.json` | Manifest and common Skill present. Desktop installation, effective revision and live dispatch unrun. |
| Antigravity | [Plugins guide](https://antigravity.google/docs/plugins), `.antigravity-plugin/plugin.json` | Manifest and common Skill present. App/CLI loading, per-project version isolation and native mode unrun. |

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
