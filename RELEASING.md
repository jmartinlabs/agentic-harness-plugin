# Releasing (maintainers)

## Versioning policy (SemVer)

- MAJOR: a change of skill names, of the project-path contract, of the required project files, of how the v2 harness schema is handled, or the removal of a capability.
- MINOR: a new capability, skill or tool, or a new client surface.
- PATCH: fixes and documentation.

## Procedure

1. Bump `version` in `plugin.json`, `.claude-plugin/plugin.json` and `.antigravity-plugin/plugin.json` in the same change as the content; update `CHANGELOG.md`. The Codex and Claude caches are keyed by `version`, so a new commit without a bump keeps the same cache path.
2. Merge to `main` with green CI. A merge needs the owner's explicit approval.
3. Create an annotated tag `vX.Y.Z` on the exact `main` SHA whose tree equals the validated candidate. Tags are never moved; a mistake gets a new PATCH release.
4. Publish GitHub release notes from the `CHANGELOG.md` entry. Tagging and releasing need the owner's explicit approval.

## Consumers

Pin a tag or a full sha:

- Claude Code: `claude plugin marketplace add jmartinlabs/agentic-harness-plugin#<tag-or-sha> --scope local`.
- Codex: `codex plugin marketplace add jmartinlabs/agentic-harness-plugin --ref <tag-or-full-sha>`.
- Antigravity: installs a branch only (a sha or tag URL was rejected in the tested run), so it cannot be pinned to a release; this is a limitation.

Check the pin with `agentic-verify-project`: `pin_status` is `tag-match`, `tag-mismatch`, `sha-or-branch` (not comparable) or `absent`.

## Update and rollback

- Update: bump the pin to the new tag or sha and reinstall; changing the pin (re-add by sha) is the observed flow (README, "GitHub distribution channel"). `marketplace update` followed by `plugin update` is the intended routine but is not claimed here: the README records only an executor report with no saved output.
- Rollback: re-pin to the previous tag or sha and reinstall. Re-pinning by sha returned 0.1.1 to 0.1.0 in the observed channel flow (README, "GitHub distribution channel").
- Branch-tracking update without a re-pin: to be completed with the branch-update result.

## Compatibility with the scaffold

The scaffold pins a plugin tag. PATCH and MINOR releases are compatible with it. A MAJOR release requires a scaffold update and an adoption note.
