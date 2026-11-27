# Apéndices

Referencia rápida de estados, tipos de trabajo, esquema JSON v2, autorizaciones, comandos, glosario, mapa canónico, historia doctrinal y relación entre plantilla y plugin.

## Apéndice A — Estados y transiciones

El sistema usa dos vocabularios **distintos y no equivalentes**: los estados operativos nativos de GitHub Issues (`planning-statuses`) y las etapas documentales del ciclo de vida (`SPEC`, `DEV`, `QA`, `MERGE`).

**Estados operativos nativos (`planning-statuses`):** `Backlog`, `Todo`, `In progress`, `In review`, `Done`, `Not planned`, `Duplicate`. Todo empieza en `Backlog`; solo `Todo` autoriza ejecución. `gh` no tiene `--status`: se escribe con `gh api -X PATCH repos/{owner}/{repo}/issues/{n} -f status="..."`. Transiciones verificadas en [issue-workflow.md](../../methodology/issue-workflow.md): una PR lista con `Closes #N` sobrescribe `Todo`/`In progress` a `In review` al crearse, marcarse lista o reabrirse (una PR draft puede no mover `Todo` → `In progress`, por lo que siempre se reserva manualmente; con `Refs #N` se conserva `Todo`/`In progress`). El merge a la rama por defecto pasa la Issue a `Done` y la cierra; contra `test` se usa `Refs #N` y se cierra tras promoción/aceptación. Una dependencia `blocked_by` solo se satisface en `Done`.

**Etapas documentales ([identifiers.md](../../methodology/identifiers.md)):**

| Etapa | Estados |
| --- | --- |
| `SPEC` | `planned` → `drafting` → `awaiting-approval` → `approved` → `superseded` |
| `DEV` | `not-ready` → `ready` → `implementing` → `testing` → `verified` |
| `QA` | `planned` → `test-design` → `awaiting-candidate` → `verifying` → `passed` / `failed` / `blocked` |
| `MERGE` | `not-ready` → `PR-open` → `ready-for-review` → `authorization-pending` → `approved` → `merged` / `closed` |

La aceptación funcional es un veredicto aparte (`pending` / `favorable-with-reservations` / `accepted` / `rejected`), nunca una quinta etapa. Un estado en una etapa nunca implica otro ni autoriza `MERGE`.

## Apéndice B — Tipos de trabajo

Los flujos adaptativos en [workflows.md](../../methodology/workflows.md) clasifican el riesgo y la preparación requerida sin eximir al coordinador de delegar todo el trabajo técnico:

| Tipo | Alcance típico | Preparación | Verificación | Autorización |
| --- | --- | --- | --- | --- |
| `Quick` | Bug o ajuste acotado de bajo riesgo | Plan breve, resultado esperado | Tests focalizados, diff, regresiones | Puede avanzar tras plan de 1 línea si es reversible y sin puerta protegida |
| `Standard` | Funcionalidad acotada | Plan breve, casos borde, checks de aceptación | Implementación, tests, code review | Requiere confirmación del usuario antes de implementar (salvo autorización vigente) |
| `Full` | Proyecto nuevo, feature transversal o arquitectura | Discovery, decisiones aprobadas, roadmap y SPEC aprobada | Desarrollo incremental, QA independiente, cumplimiento de SPEC, review | Requiere confirmación del usuario en clasificación, roadmap, SPEC y gates protegidos |

El riesgo pesa más que el tamaño: autenticación, pagos, seguridad, migraciones o contratos incompatibles exigen `Full` aunque el cambio sea pequeño. En Issues ([issue-workflow.md](../../methodology/issue-workflow.md)), la estructura se adapta en cuatro casos: simple (Issue única), con incertidumbre (Padre + `Analysis` + `DEV`), compleja con requisitos claros (Padre + `SPEC` + `DEV`) y compleja con incertidumbre (Padre + `Analysis` + `SPEC` + `DEV`). Las sub-issues nacen en `Backlog` con `blocked_by` y se mueven a `Todo` al autorizarse.

## Apéndice C — Esquema JSON v2

La configuración de delegación vive exclusivamente en `.agents/harnesses/` en la raíz principal del proyecto y se valida con [validate-core](../../scripts/validate-core) (JSON estricto sin claves duplicadas ni `NaN`/`Infinity`, `version: 2`, sin fallback v1).

**Coordinador standalone (`.agents/harnesses/<coordinator>.json` para `claude`, `codex`, `opencode`, `hermes`, `antigravity`):**
- `local`: `{ model, effort, profiles }`, donde `profiles.<rol>` (`functional`, `implementation`, `qa-review`, `infrastructure`) admite `standard` y `complex` con al menos `model` o `effort`. Es una solicitud con fallback a herencia nativa; los perfiles nativos v2 permanecen no soportados hasta verificación funcional ([dynamic-agents.md](../../methodology/dynamic-agents.md)).
- `external.<cliente>`: `{ enabled, transport: "cli", model, effort, tasks: { review, investigate, develop } }` con modos `automatic`, `on_request` o `disabled`. `automatic` solo es válido para `claude` → `codex` `review`.

**Host T3 (`.agents/harnesses/t3.json` versionado o `t3.local.json` gitignored):**
- `local`: `{ provider, model, effort, profiles }`. `provider` y `model` son obligatorios juntos al fijar defaults o perfiles. `profiles.<rol>` admite roles canónicos (selección única `{ provider, model, effort }` o `{ standard, complex }`) y `review` (solo selección única, reutilizando `qa-review`).
- Exclusividad local: si existe `t3.local.json`, es el único archivo activo sin herencia cruzada. Precedencia atómica: (1) selección explícita del owner (`provider` + `model`), (2) `local.profiles.<rol>`, (3) defaults `local` del mismo archivo, (4) detener dispatch. Mapeo de `effort`: OpenCode `variant`, Antigravity `thought_level`, Codex `reasoningEffort`.

## Apéndice D — Autorizaciones

Política definida en [approvals.md](../../methodology/approvals.md). Una aprobación es un control a nivel de instrucción y nunca se infiere de CI en verde, QA aprobado o un plan previo.

| Operación | ¿Requiere nueva aprobación explícita? | Regla clave |
| --- | --- | --- |
| Merge de una PR | Sí (por PR y candidate SHA) | Prohibido auto-merge; requiere verbo explícito (`Apruebo PR #N`) |
| SPEC Full, wireframes, decisión de producto/financiera | Sí | Aprobar o fusionar una PR de SPEC no autoriza `DEV` |
| Inicio de `DEV` (cuando hay puerta separada) | Sí | `Todo` en Issue autoriza ejecución según flujo |
| Cambio material de seguridad/arquitectura, despliegue, migración, borrado | Sí | Preguntar una decisión identificable a la vez |
| Implementación, tests y subagentes dentro del alcance autorizado | No | Trabajo ordinario; respeta reglas más estrictas del proyecto |
| Worktree local nuevo y aislado | No (si cumple 3 condiciones) | Alcance autorizado, aislamiento útil, sin afectar cambios previos |
| Publicar rama o abrir/actualizar PR del alcance autorizado | No | Respetar `local only`; revisar diff y secretos antes de push |
| Limpieza post-merge (`git worktree remove`, `git branch -d`) | No (tras merge confirmado) | Sin `--force` ni `-D`; conservar si hay duda o trabajo ajeno |

Respuestas genéricas (`ok`, `dale`, `continúa`, silencio) nunca aprueban operaciones protegidas. Registra siempre alcance, objetivo, SHA/revisión y mensaje del usuario.

## Apéndice E — Comandos

En Claude Code con el plugin activo están disponibles los shims `bin/agentic-*` en `PATH`; en el resto de clientes se invocan directamente desde `<plugin-root>/scripts/` con Python 3.10+.

| Script | Shim (Claude Code) | Uso y opciones principales |
| --- | --- | --- |
| [verify-project.py](../../scripts/verify-project.py) | `agentic-verify-project` | Probe de solo lectura: `--project DIR`, `--coordinator <cliente>`, `--print-rules`, `--inventory` |
| [validate-core](../../scripts/validate-core) | — | Valida plugin o proyecto: `--project DIR`, `--harness-file PATH`, `--root DIR` (0 OK, 1 fallo, 2 uso) |
| [update-agentic](../../scripts/update-agentic) | — | Actualiza clientes instalados o `--check` en solo lectura |
| [agent-relay](../../scripts/agent-relay) | `agentic-relay` | Transporte Git entre dos participantes (`--remote`): `init`, `join`, `send`, `read`, `status`, `close` |
| [check-delegation-route](../../scripts/check-delegation-route) | `agentic-check-delegation-route` | Verifica ruta real en Hermes (`--state-db` / `--profile`, `--delegation` / `--latest`, `--expect-*`, `--json`) |
| [report-agent-usage](../../scripts/report-agent-usage) | `agentic-usage-report` | Informe de uso Codex (`--session UUID`, `--turn`, `--task`, `--sessions-dir`, `--output-dir`) |
| [auto-agent-usage](../../scripts/auto-agent-usage) | `agentic-usage-auto` | Hook de ciclo de vida Codex (`--sessions-dir`, `--output-dir`) |

Comandos operativos clave: `gh api -X PATCH repos/{owner}/{repo}/issues/{n} -f status="In progress"` (estado de Issue), `git pull --ff-only` (actualización segura del coordinador), `git worktree remove <ruta>` y `git branch -d <rama>` (limpieza post-merge).

## Apéndice F — Glosario

- **Coordinador:** sesión principal que planifica, reserva Issues, construye work packets, verifica resultados y mantiene su checkout en la rama base configurada sin ejecutar trabajo técnico directo.
- **Worker / Delegate:** agente hijo acotado que ejecuta un único work packet en un worktree aislado; nunca lee configuración de coordinador, delega ni aprueba.
- **Work packet:** contrato compacto basado en [agent-work-packet.md](../../templates/agent-work-packet.md) con objetivo, autorización, propiedad de archivos, reglas aplicables, verificación y esquema de retorno.
- **Perfil de rol:** contrato reutilizable (`functional`, `implementation`, `qa-review`, `infrastructure`) que define comportamiento y límites, no un agente permanente.
- **Harness JSON v2:** esquema de configuración en `.agents/harnesses/` validado por `validate-core`.
- **Exclusividad local:** regla de host T3 por la que `t3.local.json` reemplaza por completo a `t3.json` sin herencia cruzada.
- **Reserva blanda (`Reserva:`):** marca en Issue (`PATCH` `"In progress"` + comentario de ronda) con relectura a los 10–15 s para detectar colisiones sin CAS.
- **`planning-statuses`:** API nativa de estados de GitHub Issues (`Backlog`..`Duplicate`).
- **Etapas (`SPEC`/`DEV`/`QA`/`MERGE`):** ciclo documental de [identifiers.md](../../methodology/identifiers.md), distinto de `planning-statuses`.
- **`Requested` vs `Observed`:** verificación de identidad real del modelo/esfuerzo (`FAIL` en discrepancia, `UNVERIFIED` si falta metadato).
- **PR Watch:** vigilancia nativa orientada a eventos (link/watch, lectura consolidada al despertar, unwatch al cerrar, sin polling).
- **Handoff:** punto de reanudación en [handoff](../../skills/handoff/SKILL.md) con marca `STOP REQUESTED — NO AUTO-RESUME` en paradas explícitas.

## Apéndice G — Archivo canónico a capítulo

Mapa entre cada documento canónico del repositorio y la parte correspondiente del índice aprobado en la Issue #62:

| Archivo canónico | Parte de la guía |
| --- | --- |
| [README.md](../../README.md), [RELEASING.md](../../RELEASING.md), [AGENTS.md](../../AGENTS.md) | Parte 0, Parte I, Parte XII, Apéndice E, Apéndice I |
| [adapters/hermes/README.md](../../adapters/hermes/README.md), `adapters/opencode/` | Parte I, Parte VI, Parte XII |
| [skills/verify-project/SKILL.md](../../skills/verify-project/SKILL.md), [skills/init-project/SKILL.md](../../skills/init-project/SKILL.md), [skills/adopt-project/SKILL.md](../../skills/adopt-project/SKILL.md), [skills/bootstrap/SKILL.md](../../skills/bootstrap/SKILL.md) | Parte I, Parte II, Parte XII |
| [methodology/document-ownership.md](../../methodology/document-ownership.md) | Parte 0, Parte II, Apéndice I |
| [methodology/dynamic-agents.md](../../methodology/dynamic-agents.md), [methodology/dynamic-agents-external-clients.md](../../methodology/dynamic-agents-external-clients.md) | Parte III, Parte VI, Parte VIII, Parte X, Parte XII, Apéndice C |
| [methodology/issue-workflow.md](../../methodology/issue-workflow.md), [skills/work-issue/SKILL.md](../../skills/work-issue/SKILL.md), [templates/issue.md](../../templates/issue.md) | Parte IV, Parte XII, Apéndice A, Apéndice B |
| [methodology/identifiers.md](../../methodology/identifiers.md) | Parte IV, Parte VI, Apéndice A |
| [methodology/approvals.md](../../methodology/approvals.md) | Parte V, Parte VII, Parte VIII, Parte XII, Apéndice D |
| [methodology/workflows.md](../../methodology/workflows.md), [methodology/epic-orchestration.md](../../methodology/epic-orchestration.md) | Parte IV, Parte VI, Apéndice B |
| [skills/orchestrate/SKILL.md](../../skills/orchestrate/SKILL.md), [skills/relay/SKILL.md](../../skills/relay/SKILL.md), [skills/relay/GITHUB_API.md](../../skills/relay/GITHUB_API.md) | Parte VI, Parte IX, Apéndice E |
| [roles/README.md](../../roles/README.md), [roles/functional.md](../../roles/functional.md), [roles/implementation.md](../../roles/implementation.md), [roles/qa-review.md](../../roles/qa-review.md), [roles/infrastructure.md](../../roles/infrastructure.md), `agents/*.md` | Parte 0, Parte VI, Parte VII |
| [skills/spec/SKILL.md](../../skills/spec/SKILL.md), [skills/dev/SKILL.md](../../skills/dev/SKILL.md), [skills/task/SKILL.md](../../skills/task/SKILL.md), [skills/tweak/SKILL.md](../../skills/tweak/SKILL.md), [skills/roadmap/SKILL.md](../../skills/roadmap/SKILL.md) | Parte II, Parte VI, Parte VII |
| [methodology/ci-policy.md](../../methodology/ci-policy.md) | Parte VIII, Parte XII |
| [skills/handoff/SKILL.md](../../skills/handoff/SKILL.md) | Parte X |
| [templates/progress.md](../../templates/progress.md), [templates/agent-work-packet.md](../../templates/agent-work-packet.md), [templates/specification.md](../../templates/specification.md), [templates/testplan.md](../../templates/testplan.md), [templates/roadmap.md](../../templates/roadmap.md), [templates/brainstorming.md](../../templates/brainstorming.md) | Parte II, Parte VI, Parte XI, Apéndice I |
| [CHANGELOG.md](../../CHANGELOG.md), [PROVENANCE.md](../../PROVENANCE.md) | Apéndice H, Apéndice I |

## Apéndice H — Historia de la doctrina

El plugin recoge su evolución en [CHANGELOG.md](../../CHANGELOG.md) y su origen en [PROVENANCE.md](../../PROVENANCE.md):

- **v1.0.0:** extracción desde la plantilla hacia plugin distribuible con 13 skills, 4 roles, `validate-core`, shims `bin/agentic-*` y manifests para Claude Code, Codex y Antigravity.
- **Errata `[1.1.0] - unreleased`:** `CHANGELOG.md` contiene una sección `## [1.1.0] - unreleased` (originalmente en la línea 69; actualmente en la línea 89 tras añadir v2.2.0 y v2.2.1). Trátala como errata histórica: no existió una release `1.1.0` publicada ni debe construirse historia o dependencia sobre ella.
- **v1.2.0 – v1.2.2:** soporte de OpenCode, Hermes y Antigravity, hooks de uso en Codex (`hooks/codex.json`), coordinación exclusiva sin fallback técnico del coordinador (#22) y actualizador multi-cliente `update-agentic` (#31).
- **v2.0.0 (MAJOR):** adopción del flujo nativo en GitHub (`planning-statuses`, sub-issues, `blocked_by`, reserva blanda) y retiro de `scripts/work-issue` y `epic-board`. Aunque el changelog anuncia tipos y perfiles nativos v2, su soporte en clientes standalone permanece marcado como **no soportado** hasta verificación funcional.
- **v2.1.0 – v2.2.1:** configuración de host T3 (`t3.json` / `t3.local.json`), política de checkout principal del coordinador (#51), PR Watch nativo (#50), simplificación de `orchestrate` (#55) y carga bajo demanda desde `AGENTS.md` (#60).
- **Relación `PROVENANCE.md` (`5b53f75`) y plantilla (`8611c37`):** `PROVENANCE.md` fija la línea base de extracción desde `agent-project-template` en el commit `5b53f75` (con blob SHA de origen, `sha256` de destino y clase `copy` / `link-rewrite` / `path-reword` / `deliberate-delta`, validada por `validate-core`). El commit `8611c37` corresponde a una referencia posterior de alineación en la plantilla: `PROVENANCE.md` no es un registro vivo de sincronización con `8611c37`, sino el inventario de origen de `5b53f75`.

## Apéndice I — Plantilla y plugin

El ecosistema separa tres capas con propiedad estricta ([document-ownership.md](../../methodology/document-ownership.md)):

1. **Plugin (`agentic-harness-plugin`):** se instala una vez por usuario y cliente desde el marketplace `agentic-harness`. Contiene los activos compartidos que **nunca se copian al proyecto**: `skills/` (13), `methodology/`, `roles/` (4), `templates/` (7), `agents/` (4 para Claude Code), `adapters/` (OpenCode y Hermes), `hooks/`, `scripts/` y `bin/`, además de los manifests (`.claude-plugin/plugin.json`, `.codex-plugin/plugin.json`, `.antigravity-plugin/plugin.json`) y descriptores de marketplace (`.claude-plugin/marketplace.json`, `.agents/plugins/marketplace.json`).
2. **Plantilla (`agent-project-template`):** origen histórico de la metodología (`5b53f75`) y base para proyectos nuevos creados con `init-project`. Conserva elementos exclusivos de plantilla (`docs/*`, `specs/methodology/acceptance-scenarios.md`) que no forman parte del plugin.
3. **Proyecto derivado:** posee sus archivos de entrada (`AGENTS.md`, `CLAUDE.md`), reglas locales (`specs/project-rules.md`), configuración v2 (`.agents/harnesses/*.json`) y documentos vivos creados desde `templates/`: [agent-work-packet.md](../../templates/agent-work-packet.md), [brainstorming.md](../../templates/brainstorming.md), [issue.md](../../templates/issue.md), [progress.md](../../templates/progress.md), [roadmap.md](../../templates/roadmap.md), [specification.md](../../templates/specification.md) y [testplan.md](../../templates/testplan.md). Si un proyecto conserva copias locales bajo `.agents/skills`, `.claude/agents` o `specs/methodology`, `verify-project.py` las señala como sombras de activos del plugin.

## Fuentes canónicas

- [methodology/identifiers.md](../../methodology/identifiers.md)
- [methodology/approvals.md](../../methodology/approvals.md)
- [methodology/issue-workflow.md](../../methodology/issue-workflow.md)
- [methodology/workflows.md](../../methodology/workflows.md)
- [methodology/dynamic-agents.md](../../methodology/dynamic-agents.md)
- [methodology/document-ownership.md](../../methodology/document-ownership.md)
- [scripts/validate-core](../../scripts/validate-core)
- [CHANGELOG.md](../../CHANGELOG.md)
- [PROVENANCE.md](../../PROVENANCE.md)
- [README.md](../../README.md)
