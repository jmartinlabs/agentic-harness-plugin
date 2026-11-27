# Guía de usuario de Agentic Harness

Guía operativa para usuarios humanos de `agentic-harness-plugin`. Cubre el ciclo completo desde la instalación hasta la resolución de problemas sin exigir la lectura previa del historial de Issues o Pull Requests.

> **Nota de alcance:** Esta guía vive en `docs/guia/`, fuera de `skills/`, `roles/`, `methodology/` y `agents/`. No entra en el contexto automático de ningún agente ni duplica políticas canónicas: cada capítulo explica el uso práctico y enlaza al documento dueño.

## Cobertura de versión

Esta guía describe el comportamiento real del repositorio en el commit **`a8a0d99`** (**v2.2.1** sobre **v2.2.0**, incluyendo el cambio de renovación proactiva de contexto de la Issue #61):

- **Sobre v2.2.0:** flujo nativo en GitHub (`planning-statuses`, sub-issues, `blocked_by`, reserva blanda), configuración de host T3 (`t3.json` / `t3.local.json`), política de checkout principal del coordinador (#51), PR Watch nativo (#50) y simplificación de `orchestrate` (#55).
- **Cambios de v2.2.1 (#60) y #61:** carga bajo demanda de `orchestrate` desde `AGENTS.md` (el hook `SessionStart` solo informa la versión del plugin y ya no inyecta `orchestrate` en Claude Code), requisito explícito de cargar `orchestrate` al usar `work-issue`, y comprobación proactiva de renovación de contexto y salidas acotadas en el coordinador.
- **Límites vigentes:** los perfiles nativos v2 en clientes *standalone* y el catálogo propio de tipos de Issue permanecen sin soporte verificado hasta validación funcional; esta guía no promete funciones inexistentes.

---

## Parte 0 — Cómo leer esta guía

### Capas del sistema

El flujo completo se organiza en cuatro capas con responsabilidades separadas:

1. **Plugin (`agentic-harness-plugin`):** activos compartidos instalados globalmente por usuario y cliente (`skills/`, `methodology/`, `roles/`, `templates/`, `agents/`, `adapters/`, `hooks/`, `scripts/`). Nunca se copian dentro de los proyectos.
2. **Configuración (`.agents/harnesses/`):** selección de proveedor, modelo y esfuerzo del coordinador (`t3.json` / `t3.local.json` en host T3, o `<cliente>.json` en *standalone*) y reglas locales del proyecto (`specs/project-rules.md`).
3. **Issues (GitHub nativo):** única fuente operativa del trabajo autorizado mediante los siete estados nativos (`planning-statuses`), sub-issues, dependencias `blocked_by` y reserva blanda.
4. **Pull Requests (GitHub):** vehículo de entrega, verificación independiente (`qa-review`), vigilancia orientada a eventos (*PR Watch*) y cierre trazable tras aprobación explícita de *merge*.

### Roles humanos y de agente

- **Usuario / Owner (humano):** define objetivos y prioridades, aprueba especificaciones (`SPEC`), autoriza la ejecución desde `Backlog`, concede permisos de publicación externa, *merge* y *release*, y resuelve escalados.
- **Coordinador (sesión principal):** planifica, reserva Issues, divide el trabajo en *work packets*, despacha subagentes o *delegates*, verifica resultados y mantiene su checkout en la rama base configurada. Nunca ejecuta trabajo técnico directo.
- **Trabajador / *Delegate* (sesión hija acotada):** ejecuta un único *work packet* en un *worktree* aislado usando uno de los cuatro perfiles reutilizables ([functional](../../roles/functional.md), [implementation](../../roles/implementation.md), [qa-review](../../roles/qa-review.md) o [infrastructure](../../roles/infrastructure.md)). Nunca lee configuración de coordinador, delega ni aprueba.

### Parte 0.5 — Tres modos de sesión

La frontera entre modos no es el tema de la conversación, sino la **acción**:

| Modo | Se activa con | Carga metodología | Autoriza |
| --- | --- | --- | --- |
| `work-issue` | Cola de Issues autorizada | Sí, requiere `orchestrate` en contexto | Reservar, ejecutar y entregar Issues |
| `orchestrate` | Cualquier coordinación o delegación | Sí, carga completa bajo demanda | Delegar, verificar y cerrar el trabajo |
| Conversación normal | Preguntas, análisis o lectura | No | Nada que implique delegar o editar |

Reglas operativas:

- En cuanto una sesión va a delegar, coordinar o tomar una Issue, debe asegurar que el texto completo de `orchestrate` esté cargado en el contexto antes del primer despacho (y tras cualquier renovación de contexto).
- En v2.2.1 (`a8a0d99`), el hook `hooks/session-start.py` únicamente muestra el banner de versión en Claude Code y Codex (no inyecta `orchestrate` al iniciar). La salvaguarda de disparo reside en `AGENTS.md` (referenciado por `CLAUDE.md` mediante `@AGENTS.md` en Claude Code), salvo en clientes donde `AGENTS.md` se pierda si no se inicia desde la raíz del proyecto (como Hermes) o esté pendiente de verificación (Antigravity).
- No se carga metodología en conversación normal ni se piden confirmaciones al usuario para cambiar de modo.

### Mapa de dueños canónicos

Cada regla tiene un único documento dueño en el repositorio:

| Documento canónico | Qué posee |
| --- | --- |
| [methodology/document-ownership.md](../../methodology/document-ownership.md) | Frontera estricta entre plugin, plantilla y proyecto derivado |
| [methodology/approvals.md](../../methodology/approvals.md) | Puertas protegidas, autorizaciones implícitas, worktrees y limpieza post-merge |
| [methodology/issue-workflow.md](../../methodology/issue-workflow.md) | Protocolo nativo de Issues en GitHub (`planning-statuses`, reserva, cierre) |
| [methodology/identifiers.md](../../methodology/identifiers.md) | Etapas documentales (`SPEC`, `DEV`, `QA`, `MERGE`) y trazabilidad |
| [methodology/dynamic-agents.md](../../methodology/dynamic-agents.md) | Esquema JSON v2, perfiles, T3 host, checkout principal y renovación de contexto |
| [methodology/dynamic-agents-external-clients.md](../../methodology/dynamic-agents-external-clients.md) | Delegación en clientes externos, relay y verificación `requested` / `observed` |
| [methodology/workflows.md](../../methodology/workflows.md) | Clasificación de riesgo (`Quick`, `Standard`, `Full`) y flujos de trabajo |
| [methodology/epic-orchestration.md](../../methodology/epic-orchestration.md) | Coordinación multi-épica, dependencias y paralelismo |
| [methodology/ci-policy.md](../../methodology/ci-policy.md) | Rutas protegidas y alcance de CI (`docs-only` frente a `full`) |
| [skills/orchestrate/SKILL.md](../../skills/orchestrate/SKILL.md) | Procedimiento operativo del coordinador y PR Watch |
| [skills/work-issue/SKILL.md](../../skills/work-issue/SKILL.md) | Superficie mínima para tomar y entregar Issues autorizadas |
| [roles/README.md](../../roles/README.md) | Índice y límites de los cuatro perfiles de rol |
| [PROVENANCE.md](../../PROVENANCE.md) | Inventario de extracción desde la plantilla (`5b53f75`) |

### Ecosistema plugin / plantilla / proyecto

- **Plugin (`agentic-harness-plugin`):** distribución global versionada por usuario; aporta skills, metodología, roles, plantillas, adaptadores y validadores.
- **Plantilla (`agent-project-template`):** base histórica de proyectos nuevos (`init-project`); conserva documentos exclusivos de plantilla (`docs/`, `specs/methodology/acceptance-scenarios.md`) que no viven en el plugin.
- **Proyecto derivado:** conserva únicamente sus archivos de entrada (`AGENTS.md`, `CLAUDE.md`), reglas locales (`specs/project-rules.md`), configuración `.agents/harnesses/*.json` y artefactos vivos creados desde `templates/`.

### Cómo usar esta guía y en qué orden

- **Primer contacto e instalación:** lee Parte I → Parte II → Parte III.
- **Operación diaria (Issue → PR → Merge):** lee Parte IV → Parte V → Parte VI → Parte VII → Parte VIII → Parte IX.
- **Sesiones largas, auditoría y fallos:** consulta Parte X, Parte XI, Parte XII y los Apéndices según necesidad.

---

## Índice completo

| Parte | Archivo | Contenido principal |
| --- | --- | --- |
| Parte I | [Instalación y mantenimiento](01-instalacion.md) | Requisitos, instalación en los 5 clientes, verificación, actualización, rollback y permisos |
| Parte II | [Inicio y adopción](02-inicio-y-adopcion.md) | Proyecto nuevo, adopción en repo existente, propiedad de archivos y primer ciclo |
| Parte III | [Configuración de modelos](03-modelos.md) | Standalone vs T3, esquema JSON v2, precedencia, `effort`, `requested`/`observed` y recetas |
| Parte IV | [Issues](04-issues.md) | Estados nativos, transiciones, anatomía, tipos de trabajo, dependencias, reserva y etapas |
| Parte V | [Autorizaciones](05-autorizaciones.md) | Puertas protegidas, qué autoriza cada fase, matriz de permisos, publicación y merge |
| Parte VI | [Coordinación y delegación](06-coordinacion.md) | Roles, *work packet*, delegación práctica, sesiones, *relay* y multi-épica |
| Parte VII | [QA y review](07-qa-review.md) | QA independiente, review interno y externo, rechazo y reanudación |
| Parte VIII | [Git](08-git.md) | Ramas, *worktrees*, checkout principal del coordinador, limpieza post-merge y recuperación |
| Parte IX | [PR Watch](09-pr-watch.md) | Ciclo de vida, lectura consolidada al despertar, fin de vigilancia, matriz por cliente y medición |
| Parte X | [Handoff y contexto](10-handoff-contexto.md) | Cuándo hacer handoff, formato, parada segura, renovación autónoma y presupuesto de contexto |
| Parte XI | [Consumo](11-consumo.md) | Qué se mide, lectura de informes, coste por tipo de trabajo, reducción y falsos indicadores |
| Parte XII | [Resolución de problemas](12-troubleshooting.md) | Método de diagnóstico y solución de fallos en instalación, modelos, Issues, Git y PR/CI |
| Apéndices | [Apéndices A–I](apendices.md) | Tablas de referencia, esquema JSON v2, comandos, glosario, mapa canónico e historia doctrinal |

---

## Correcciones documentales de la Issue #62

Registro de los hallazgos detectados al redactar la guía y el capítulo donde se documenta o aclara cada uno:

| Hallazgo | Dónde se trata en la guía |
| --- | --- |
| `workflows.md:29` con `## Model advice` vacío; remitir a `dynamic-agents.md` | [Parte III — Configuración de modelos](03-modelos.md) |
| `README.md` raíz sin `t3.json`/`t3.local.json`, sin `update-agentic` en scripts y con nota obsoleta sobre *live checks* | [Parte I — Instalación y mantenimiento](01-instalacion.md) y [Parte III — Configuración de modelos](03-modelos.md) |
| `CHANGELOG.md` con entrada `[1.1.0] - unreleased` (errata histórica) | [Apéndices (Apéndice H)](apendices.md) |
| `roles/README.md:12` cita `AGENTS.md` y `adopt-project` cita "model selection" | [Parte II — Inicio y adopción](02-inicio-y-adopcion.md) y [Parte VI — Coordinación y delegación](06-coordinacion.md) |
| `CHANGELOG.md` v2.0.0 anuncia tipos nativos sin dueño canónico ni validación propia | [Parte IV — Issues](04-issues.md) y [Apéndices (Apéndice H)](apendices.md) |
| Etapas `SPEC/DEV/QA/MERGE` frente a `planning-statuses` (vocabularios no equivalentes) | [Parte IV — Issues](04-issues.md) y [Apéndices (Apéndice A)](apendices.md) |
| Relación entre `PROVENANCE.md` (`5b53f75`) y plantilla (`8611c37`) | [Apéndices (Apéndices H e I)](apendices.md) |
| PR Watch sin matriz por cliente | [Parte IX — PR Watch](09-pr-watch.md) |
| Consumo y *troubleshooting* ausentes en la documentación previa | [Parte XI — Consumo](11-consumo.md) y [Parte XII — Resolución de problemas](12-troubleshooting.md) |
