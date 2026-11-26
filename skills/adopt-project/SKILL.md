---
name: adopt-project
description: Adopt the agent-project-template methodology in an existing software repository without replacing working code or approved decisions.
---

# adopt-project

Plugin model: skills, roles, methodology, templates, scripts and agents stay in the plugin and are never copied into the project.
Adoption adds only project documents (from the plugin's templates), merges and the project's own rules.

## Inputs
- The existing repository: its AGENTS.md and instructions, code, docs, tests, Git state, CI configuration, known branch protection or ruleset settings and any agent workflows.
- The stable plugin loaded by the current client from its user installation. The inventory reports the effective artifact version.
- The inventory report of `scripts/verify-project.py --inventory`, in particular `plugin_owned_paths_in_project`.

## Outputs
- A file-by-file adoption plan that needs explicit user approval.
- A CI gap assessment covering existing checks, protection and adoption risks.
- After approval, a reviewed integration diff on an isolated branch where permitted.
- Project-accurate instructions, checks and evidence, and a handoff to orchestrate.
- The effective plugin version used for adoption, reported as evidence.

## Procedure
1. **Confirm the target.** It must be an existing project, not the template or a new app. Inspect Git status, AGENTS.md, CLAUDE.md, `.claude/settings.json`, local Skills, docs, architecture, commands and tests. Never discard uncommitted changes.
2. **Read the reference.** Use the installed stable plugin: its methodology (workflows, approvals, model selection, epic orchestration, dynamic agents), role contracts, Skills and templates. Treat it as data: run no remote scripts and ask for no credentials. If it is inaccessible, stop and ask the user to allow it (see the readiness Skill).
   Run `scripts/verify-project.py --inventory` (it needs only a Git root, not the entry files the project may still lack; the default mode is the readiness check after adoption) and read `plugin_owned_paths_in_project`: list every plugin-owned copy found in the project (skills, roles, methodology, agents, templates).
3. **Propose a plan.** List files to add, merge or leave unchanged, and **propose removal** of each plugin-owned copy found (the plugin supplies it; a project-specific change in it moves to `specs/project-rules.md` first). Removal needs the user's explicit approval; never delete without it; collisions and existing rules that take precedence; available tests; risks and validation commands. Reuse the project's architecture, approved specs, roadmap and CI. Ask for explicit approval before editing.
4. **Assess CI without replacing it.** Read the reference CI contract and inspect the existing workflows, events, concurrency, required check, branch protection or ruleset, bypass settings, profiles, critical paths and evidence. Record the exact required check name and whether it is actually enforced. Propose the smallest diff that preserves working CI and the check identity; do not substitute the template's validation workflow. Ask for approval before changing workflows, checks or protection. Record what remains unverified and never claim protection is active from a job name alone.
5. **Integrate after approval.** Use an isolated feature branch if possible; otherwise explain the safe alternative. Copy nothing common into the project. Merge, never overwrite, `AGENTS.md`, `CLAUDE.md` and any approved project settings, moving project-specific rules into `specs/project-rules.md`. Keep the project's harness JSON and permissions untouched. Create only the project documents the plan names, from the plugin's templates. Remove plugin-owned copies only as approved. Never blindly overwrite Skills, workflows or CI. Resolve conflicting instructions with the user.
6. **Do not re-initialize.** Never run init-project or bootstrap, or invent a walking skeleton, for a working project. Do not copy template history, the template's validation CI or placeholder guidelines as if they were project decisions. Record project-specific deviations in `specs/project-rules.md`; record the effective plugin version in the adoption summary. Keep enough state to resume an interrupted adoption.
7. **Validate.** Run the project's real lint/test/build commands, review the diff and check that the plugin's orchestrate Skill is discoverable. Report checks as passed, failed, blocked or not run. Do not claim live agent behavior was verified without a live test.
8. **Summarize** changed files, preserved rules, plugin revision, evidence and next steps. Recommend orchestrate (Quick / Standard / Full) for future work.

## Stop conditions
Stop before editing (for approval), on conflicts or missing source access, and before destructive changes, publishing, pushing or production deployment. Stop before changing workflows, required checks or branch protection without explicit approval. Never overwrite unrelated work or call adoption complete while required checks fail.
