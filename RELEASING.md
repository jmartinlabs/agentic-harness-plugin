# Releasing (maintainers)

## Versioning policy (SemVer)

- MAJOR: a change of skill names, of the project-path contract, of the required project files, of how the v2 harness schema is handled, or the removal of a capability.
- MINOR: a new capability, skill or tool, or a new client surface.
- PATCH: fixes and documentation.

## Procedure

1. Bump `version` in `plugin.json`, `.claude-plugin/plugin.json` and `.antigravity-plugin/plugin.json`, and rename both marketplaces to `agentic-harness-X-Y-Z` (`validate-core` checks it), in the same change as the content; update `CHANGELOG.md`. Never publish two revisions under one marketplace name on a tag, and never reuse a released name. The Codex and Claude caches are keyed by `version`, so a new commit without a bump keeps the same cache path.
2. Merge to `main` with green CI, using a merge commit (it keeps the provenance commits). The status check `required` (an aggregate job in `.github/workflows/validate.yml` that fails unless the `pilot` and `claude-validate` jobs succeed) is the merge gate that the `main-required` ruleset names. A merge needs the owner's explicit approval.
3. Verify before tagging: `git fetch`; `git diff --stat <approved PR head> origin/main` is empty; `git rev-parse origin/main^{tree}` equals the QA'd tree; CI on the `main` SHA is green, including `required`.
4. Create an annotated tag on that exact `main` SHA and publish it: `git tag -a vX.Y.Z <main sha> -m "vX.Y.Z"`, `git push origin vX.Y.Z`, then `gh release create vX.Y.Z --verify-tag --notes-file <notes from the CHANGELOG entry>`. Tags are never moved; a mistake gets a new PATCH release. Tagging and releasing need the owner's explicit approval.
5. Post-release smoke test (tag-form pins were never run): install by tag on Claude Code (`marketplace add jmartinlabs/agentic-harness-plugin#vX.Y.Z`, then `install agentic@agentic-harness-X-Y-Z`) and on Codex (`--ref vX.Y.Z`), and run the diagnostic on each. All client evidence so far is on 0.1.0 content, so this is also the first load of the released content.

## Consumers

Pin a tag or a full sha:

- Claude Code: `claude plugin marketplace add jmartinlabs/agentic-harness-plugin#<tag-or-sha> --scope local`.
- Codex: `codex plugin marketplace add jmartinlabs/agentic-harness-plugin --ref <tag-or-full-sha>`.
- Antigravity: installs a branch only (a sha or tag URL was rejected in the tested run), so it cannot be pinned to a release; this is a limitation.

A branch or a sha that is not a tag shares the marketplace name of its version, so isolation between revisions of the **same** version is not guaranteed.

Check with `agentic-verify-project`: it blocks when the running version is not the one the project enables, or when two are enabled.

## Update and rollback

- Update or roll back one project: follow "Versions per project" in the README (add the other tag's marketplace, install, uninstall the old one, update the committed settings). The new version applies after a restart.
- `plugin update` does not move a project between releases.

## Compatibility with the scaffold

The scaffold declares one release: its marketplace name, tag and `enabledPlugins` key. Every release needs those three values changed to adopt it. PATCH and MINOR releases need no other project change. A MAJOR release also requires an adoption note.
