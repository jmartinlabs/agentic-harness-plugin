# Parte IV — Issues

Este capítulo describe cómo se gestionan las Issues de GitHub como única fuente operativa del trabajo autorizado, sin tableros Project externos ni trackers locales. Acude aquí antes de listar la cola, reservar una Issue, crear sub-issues o interpretar su estado.

## Estados nativos (`planning-statuses`)

El protocolo de [issue-workflow.md](../../methodology/issue-workflow.md) y [SKILL.md](../../skills/work-issue/SKILL.md) usa exclusivamente los siete estados nativos de GitHub: `Backlog`, `Todo`, `In progress`, `In review`, `Done`, `Not planned` y `Duplicate`.

1. **Preflight obligatorio**: antes de listar, ejecuta `gh api repos/{owner}/{repo}/planning-statuses` (debe devolver `200`). Si devuelve `404` o falla, detente y pide autorización humana; nunca asumas cola vacía ni inventes estados.
2. **Issues sin estado (`status == null`)**: si no hay `Todo`, comprueba si hay abiertas con `status == null` y repórtalas como sin estado (`unset`), sin dar la cola por vacía.
3. **Escritura**: `gh issue` no tiene `--status`; usa `gh api -X PATCH repos/{owner}/{repo}/issues/{n} -f status="In progress"`.

## Transiciones verificadas

- Una PR lista (`ready`) con `Closes #N` sobrescribe `Todo`/`In progress` a `In review` al crearse o pasar a lista (un `PATCH` posterior persiste). Con `Refs #N` se preservan y el paso a `In review` es manual.
- Una PR en borrador (`draft`) puede no mover `Todo` → `In progress`: reserva siempre manualmente.
- Reabrir una PR lista fuerza `In review`: no cierres ni reabras PRs en correcciones ordinarias.
- Enviar una review no cambia el estado; volver a `Todo` es manual.
- El merge a la rama por defecto pasa a `Done` y cierra la Issue; contra `test`, usa `Refs #N` y cierra tras promoción o aceptación. Reabrir vuelve a `Backlog`; descartar pasa a `Not planned`.

## Anatomía y tipos de Issue

La plantilla [issue.md](../../templates/issue.md) estructura cada Issue para que sea autosuficiente: *Objective*, *Requested phase* (`Analysis`, `Specification` o `Development`), *Scope* (dentro y fuera), *Routing*, *Linked SPEC*, *Acceptance checks* (`AC-01`, `AC-02`), *Dependencies* y *Authorization and evidence*.

> Nota documental: aunque [CHANGELOG.md](../../CHANGELOG.md) (v2.0.0) menciona *native issue types*, el repositorio no define ni valida un catálogo propio de tipos de Issue en `methodology/` ni en `validate-core` (hueco documental). En la práctica se emplean los tipos nativos disponibles en el repositorio (como `Task`) junto con la estructura adaptativa.

## Tipos de trabajo y dependencias

Según la complejidad, [issue-workflow.md](../../methodology/issue-workflow.md) define cuatro estructuras:

| Caso | Estructura |
| --- | --- |
| Simple | Issue única |
| Con incertidumbre | Padre + Analysis + DEV |
| Compleja con requisitos claros | Padre + SPEC + DEV |
| Compleja con incertidumbre | Padre + Analysis + SPEC + DEV |

Las sub-issues se crean en `Backlog` con dependencias nativas `blocked_by`; crear una sub-issue nunca autoriza su ejecución (debe pasar a `Todo`). La Issue padre se cierra solo cuando se cumple el objetivo global.

Una dependencia `blocked_by` se satisface **únicamente** cuando la Issue bloqueante está en `Done`. Los estados `Not planned`, `Duplicate`, `Backlog`, `Todo`, `In progress` e `In review` no desbloquean: si ya no aplica, elimina la relación `blocked_by` o corrige la referencia duplicada.

## Reserva, routing y concurrencia

- **Sin assignees**: nunca uses GitHub assignees, ya que asignan automáticamente `Backlog` → `Todo` y no revierten. Enruta con etiquetas `agent:<cliente>` (`claude`, `codex`, `opencode`, `hermes`, `antigravity`); sin etiqueta, cualquier cliente compatible puede tomarla.
- **Coordinador único y reserva blanda**: solo se soporta un coordinador por repositorio (no hay CAS). Solo el coordinador reserva o cambia estados; los workers nunca tocan Issues.
- **Secuencia de reserva**: (1) `PATCH` a `In progress`; (2) publica el comentario `Reserva: <agente> · ronda: <enlace al comentario de rechazo | inicial> · <alcance>`; (3) espera ~10–15 s y relee una sola vez (sin polling). Si aparece otra reserva de la misma ronda, gana el timestamp de servidor más antiguo y el otro coordinador se detiene sin escribir más; si el orden es ambiguo o hay dos reservas propias, detente y pregunta.
- **Review rechazada**: registra un comentario identificable de rechazo (abre nueva ronda) y vuelve a `Todo` (con `Closes #N` y PR lista, pasa la PR a borrador → `In progress` y luego `Todo`; con `Refs #N`, directo). Reutiliza siempre la rama y la PR existentes.

## Cierre, trazabilidad y etapas de documento

Las fases sin PR (`Analysis`, `SPEC` o documentales) se entregan mediante un informe breve en la Issue y se cierran con `Done` por aceptación del owner; ningún agente se autoacepta. La trazabilidad única conecta Issue (decisiones), PR (diff/QA/review), CI y SHA candidato sin tableros paralelos.

No confundas las cuatro etapas documentales de [identifiers.md](../../methodology/identifiers.md) (`SPEC`, `DEV`, `QA`, `MERGE`, cada una con sus propios estados y veredicto separado de aceptación funcional) con los siete estados operativos de GitHub (`planning-statuses`). Son vocabularios distintos sin equivalencia 1:1: que una Issue pase a `In review` no equivale a `QA passed` ni autoriza `MERGE`.

## Fuentes canónicas

- [issue-workflow.md](../../methodology/issue-workflow.md)
- [SKILL.md](../../skills/work-issue/SKILL.md)
- [issue.md](../../templates/issue.md)
- [identifiers.md](../../methodology/identifiers.md)
- [approvals.md](../../methodology/approvals.md)
- [CHANGELOG.md](../../CHANGELOG.md)
