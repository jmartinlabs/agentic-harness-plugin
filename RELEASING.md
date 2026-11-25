# Releasing (maintainers)

## Versioning policy (SemVer)

- MAJOR: a breaking change to skill names, required project files, the project-path contract, v2 handling or a supported capability.
- MINOR: a new compatible capability, skill, tool or client surface.
- PATCH: compatible fixes and documentation.

## Procedure

1. Bump `version` in `.codex-plugin/plugin.json`, `.claude-plugin/plugin.json` and `.antigravity-plugin/plugin.json` in the content change and update `CHANGELOG.md`. Both marketplace descriptors keep the fixed name `agentic-harness`. Clients use the manifest version for their installed caches.
2. Obtain the owner's approval to merge. Use a merge commit to keep the provenance commits. The `required` status check aggregates the regression tests and strict Claude validation.
3. Verify before tagging. Fetch and compare the approved PR head tree with the `main` tree. Confirm that the evidence applies to the tree being released and that `required` passes on the exact `main` SHA.
4. With explicit approval, create an annotated tag on that SHA, publish the tag and create the release with the changelog notes. Keep published tags immutable. Correct a published artifact with a new version.
5. With release approval that includes promotion, fast-forward the `stable` branch to the exact commit of the published tag, for example `git push origin 'vX.Y.Z^{commit}:refs/heads/stable'`. Before pushing, verify that the release is public and that the existing `stable` tip is an ancestor of the release commit if the branch exists. If the update would not fast-forward, stop and inspect the release history.
6. Smoke-test native user installation or refresh from `stable` in isolated Claude Code and Codex profiles. Check the startup version and diagnostic in new sessions. Smoke-test rollback using a previous published tag when available.

## Consumers

Use the installation, update and rollback commands in the [Quick start](README.md#quick-start). For an individual user's global rollback, select a previous published tag at user scope using the same marketplace identity. To ship a rollback to everyone tracking `stable`, publish a new version restoring the previous behavior and promote it through the normal approval process.

The scaffold keeps its own rules and v2 configuration. Compatible releases require no project distribution changes. A major release also needs an adoption note.
