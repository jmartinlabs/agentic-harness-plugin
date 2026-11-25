# Document ownership and workflow

For new work, see [adaptive Quick / Standard / Full workflows](workflows.md), [epic scheduling](epic-orchestration.md) and [dynamic agent management](dynamic-agents.md). These route the original Full-document lifecycle only when warranted; small changes need no mandatory feature documents. See manual acceptance scenarios (`specs/methodology/acceptance-scenarios.md` in the template, not part of the plugin).
Derived-project harness requirements live in the [change-aware CI contract](ci-policy.md), implemented during bootstrap.
Work tracked in Issues follows the [issue workflow](issue-workflow.md): when a Project exists its `Status` is the only phase gate and the operational queue, replacing `epic-board.md`; without one, the manual protocol applies and nothing simulates a second tracker.
Language: methodology and guidance are written in English. The comment-protocol wire values the
tools parse (`Autor`, `Rol`, `Fase`, `Huella del contexto`) and `docs/GUIA_VISUAL_ORQUESTACION.md`
stay in Spanish on purpose; do not translate them without changing `scripts/work-issue` and its tests.
This plugin ships the methodology; a project created from it starts uninitialized, with no product, stack or architecture approved. Nothing below is copied into the project: the plugin keeps skills, roles, methodology, templates, scripts and agents, and the documents in the table are created in the project, from the plugin's templates where one exists, by the skill named.

| Document | Owns | Created/updated by |
| --- | --- | --- |
| `specs/project.md` | Purpose, users, problem, scope and references | init-project stage 1 |
| `specs/setup-progress.md` | Stage status, decision links, pending questions, next action | init-project |
| `specs/guidelines/architecture.md` | Canonical approved technology and boundary decisions with rationale | init-project / dev |
| `specs/guidelines/ui.md` | Applicable interface conventions or explicit not-applicable reason | init-project / dev |
| `specs/guidelines/quality.md` | Commands, checks, review and Definition of Done | bootstrap / dev |
| `specs/guidelines/security.md` | Threats, safeguards and authorization boundaries | init-project / dev |
| `specs/project-rules.md` | Local gates, restrictions and verification rules; read by the skills before every gate | project scaffold, or init-project / adopt-project |
| `specs/roadmap.md` | Approved product outcomes and epic scope | roadmap |
| `specs/epic-board.md` | Optional multi-epic queue, blockers, dependencies and evidence links when no Project owns status; never canonical approvals | orchestrate only |
| `specs/NN-slug-brainstorming.md` | Append-only questions and confirmed answers | spec |
| `specs/NN-slug-specification.md` | Approved behavior, contracts and acceptance checks | spec |
| `specs/NN-slug-progress.md` | Per-task state when no Project or board exists; append-only evidence history | dev |
| `specs/NN-slug-testplan.md` | Acceptance-to-verification mapping and current results | dev |
| `specs/session-handoff.md` | Optional latest shutdown checkpoint when no existing progress/board file fits; retire after successful restoration and consolidation; if tracked, remove in the same task change, never a standalone PR; no automatic resume authority | handoff only |

Use two-digit identifiers (01–99) and lowercase hyphenated slugs. Allocate the next
unused number; never overwrite a document belonging to another feature. Beyond 99,
ask for an agreed migration rather than silently changing the naming scheme.
Templates live in [templates](../templates); copy them without overwriting existing work.
Recommendations are proposals, not approvals. Record approval source/date at its canonical
location. Setup progress links to decisions instead of duplicating their text.

Eight steps: bootstrap → context files → enforceable rules → roadmap → specification
→ reusable spec Skill → build → reusable dev Skill. Skills implement these repeatable
processes; the initialization walkthrough coordinates the first four steps.

Mixed-client work reuses the [work packet](../templates/agent-work-packet.md) and
[coordination contract](dynamic-agents.md). A current summary in the Project/tracker
or in existing progress/setup/board documents owns operational state; other documents link it.
