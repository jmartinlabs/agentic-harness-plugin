# Parte X — Handoff y contexto

Esta parte define cómo detener o transferir una sesión sin perder trazabilidad ni inventar autorizaciones, y cuándo conviene renovar el contexto del coordinador. Acude aquí ante saturación de contexto, cambios de fase o pausas forzadas.

## Cuándo hacer handoff

El checkpointing es **adaptativo**: se recomienda abrir una sesión nueva tras una entrega significativa, un cambio de fase o saturación de contexto, pero nunca se impone de forma automática. Antes de sugerir un nuevo chat o detener una sesión activa, ejecuta el procedimiento `$handoff`.

## Formato del checkpoint

Reutiliza el archivo de progreso existente del proyecto; crea `specs/session-handoff.md` únicamente si no existe otro soporte. El checkpoint debe contener **solo estado actual y verificable**:

- Cabecera literal: `STOP REQUESTED — NO AUTO-RESUME`.
- Alcance autorizado, rama actual, `HEAD` SHA y número/estado de PR.
- Enlaces (nunca copias completas) a Issue, PR, SPEC y evidencias.
- Aprobaciones válidas frente a pendientes, estado de checks (`PASS`, `FAIL` o `UNRUN`), bloqueos activos y **una única** siguiente acción segura.

Excluye el historial de ejecución, las decisiones obsoletas y las reglas que ya residen en el plugin. Tras escribirlo, relee el archivo para verificar ruta, `HEAD` y enlaces; si no quedó persistido, márcalo como `not persisted`.

## Handoff de parada y reanudación

Para detener una sesión de forma segura:

1. **Congela la ejecución:** detén nuevas delegaciones o ediciones. Registra a los workers controlados como `stopped`, `stop requested` o `unconfirmed`; nunca atribuyas control sobre sesiones externas o abiertas manualmente por el usuario.
2. **Inventaría Git y PR:** inspecciona `git status`, rama, `HEAD`, worktrees y estado de PR sin borrar ni hacer `stash` de archivos de propiedad dudosa. Solo haz commit de un WIP en la rama existente si es seguro y está autorizado.
3. **No abras PR para el handoff:** el flujo de parada nunca autoriza abrir una PR exclusiva de checkpoint.

Un checkpoint **no otorga** autoridad de reanudación automática. Al retomar en una sesión nueva:

- Verifica la deriva real de Git, PR y aprobaciones antes de actuar.
- Consolida el estado duradero en la Issue, SPEC o documento de progreso y elimina `specs/session-handoff.md` dentro de la misma rama de tarea.
- **Recuperación del modo de sesión:** antes del siguiente despacho, recupera explícitamente el modo operativo (`work-issue`, `orchestrate` o conversación normal) y asegúrate de cargar `orchestrate` en el contexto si falta al coordinar o tomar una Issue.

## Renovación autónoma

En hosts que soportan renovación de hilo (como T3 Code mediante `freshContext`), el coordinador puede renovar su propio contexto de forma autónoma con un handoff compacto y selectivo en puntos seguros —por ejemplo, tras un merge confirmado, una release, una QA/revisión cerrada o un cambio de fase, antes del siguiente bloque—, conservando intactas todas las autorizaciones, puertas de aprobación y enlaces de evidencia. Por defecto, los subagentes arrancan con contexto fresco acotado y mantienen su sesión mientras siga siendo útil.

## Presupuesto de contexto

En T3 Code, mientras el host no exponga `contextUsage`, la política (introducida con `#61`) usa **~150k** tokens como aviso orientativo y **~200k** como objetivo blando para evaluar una renovación antes del siguiente bloque. Nunca es un corte duro, ni se renueva a mitad de una puerta, durante operaciones irreversibles o cuando el coste del handoff supera su beneficio.

Para no agotar el presupuesto antes de tiempo: usa lecturas parciales, filtra salidas de comandos en origen, evita releer archivos sin cambios y mantén compactos los paquetes de trabajo. En el plugin, los hooks `SessionStart` cuidan también este presupuesto (`validate-core` impone un límite de 8704 bytes para salidas inyectadas al inicio).

## Fuentes canónicas

- [Skill `handoff`](../../skills/handoff/SKILL.md)
- [Skill `orchestrate`](../../skills/orchestrate/SKILL.md) (secciones *Inputs* y *Efficiency and communication*)
- [Gestión dinámica de agentes](../../methodology/dynamic-agents.md) (sección *Host worker configuration — Autonomous context renewal*)
- [Clientes externos y T3](../../methodology/dynamic-agents-external-clients.md) (sección *T3 host delegation*)
- [Historial de cambios](../../CHANGELOG.md) (entradas `1.2.1`, `2.1.0` y `2.2.1`)
