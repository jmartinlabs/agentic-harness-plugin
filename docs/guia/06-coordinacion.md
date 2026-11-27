# Parte VI — Coordinación y delegación

Explica cómo el coordinador divide el trabajo, delega en trabajadores acotados mediante *work packets*, gestiona sesiones y mensajes *relay* entre agentes, y coordina múltiples épicas sin duplicar autoridad. Acude a este capítulo cuando prepares una delegación o coordines trabajo en paralelo.

## Roles de especialista

La metodología define cuatro perfiles reutilizables, no agentes permanentes ni registrados en un directorio activo:

- **Functional:** descubrimiento, *brainstorming*, borradores de especificación y criterios de aceptación sin autoaprobación ([functional.md](../../roles/functional.md)).
- **Implementation:** desarrollo acotado sobre una especificación aprobada (`$dev`) o una tarea autorizada (`$task`) ([implementation.md](../../roles/implementation.md)).
- **QA / Review:** verificación independiente de conformidad, regresiones y evidencia ([qa-review.md](../../roles/qa-review.md)).
- **Infrastructure / DevOps:** tareas acotadas de Docker, CI, entorno de datos o preparación de despliegue ([infrastructure.md](../../roles/infrastructure.md)).

El coordinador puede lanzar cero, una o varias tareas con el mismo perfil o definir un rol temporal. Ningún rol reserva Issues ni cambia su estado nativo; esa restricción reside en el coordinador y en cada contrato de rol (aunque [roles/README.md](../../roles/README.md) mencione `AGENTS.md` como referencia del proyecto). En OpenCode existen adaptadores opcionales (`review`, `functional`, `implementation`, `qa`, `infrastructure`) cuyos archivos viven en `adapters/opencode/agents/` del plugin; su documentación completa está en la plantilla (`docs/OPENCODE_ADAPTER.md`).

## El work packet

Toda delegación usa un formato compacto basado en [agent-work-packet.md](../../templates/agent-work-packet.md):

1. **Identificador y perfil:** `<id> · <STAGE>-<NN>` (por ejemplo `ISSUE-62 · DEV-03`) y rol asignado.
2. **Objetivo, criterios de cierre y autorización:** qué debe quedar hecho, fuente de aprobación y dependencias satisfechas.
3. **Archivos y aislamiento:** rutas de lectura, rutas de escritura en propiedad exclusiva y rama o *worktree* asignado.
4. **Acciones prohibidas y reglas aplicables:** de 3 a 6 reglas concretas con enlace a su documento dueño; el trabajador lee su rol y el packet, no toda la metodología.
5. **Verificación y devolución:** comandos esperados, candidato (`SHA`) y formato de retorno (`COMPLETED`, `PARTIAL`, `BLOCKED` o `CANCELLED`).

**Error común:** repetir el brief completo al pedir correcciones. En una devolución por hallazgos se envían únicamente los defectos y los criterios de aceptación afectados, referenciando el packet original.

## Delegación práctica

El coordinador analiza, clasifica el riesgo (`Quick`, `Standard` o `Full`) y delega todo el trabajo técnico según [SKILL.md](../../skills/orchestrate/SKILL.md) (pasos 1–3). Incluso `Quick` usa un trabajador acotado; si no hay ningún trabajador utilizable y autorizado, el coordinador reporta el bloqueo y nunca asume la ejecución técnica ni simula una delegación.

Antes de despachar:

1. **Preflight:** comprobar estado de Git, propiedad de archivos, permisos y herramientas necesarias; los cambios documentales no requieren aplicación ni navegador.
2. **Configuración de modelos:** leer bajo demanda `.agents/harnesses/t3.local.json` o `t3.json` en host T3, o `.agents/harnesses/<coordinador>.json` en clientes *standalone*, aplicando [dynamic-agents.md](../../methodology/dynamic-agents.md) (sección *Coordinator configuration*). En T3, una ruta no disponible detiene el despacho sin sustituciones.
3. **Propiedad exclusiva:** los archivos de un trabajador activo quedan cerrados para el coordinador y otros escritores. Las escrituras concurrentes exigen *worktrees* aislados y archivos disjuntos; de lo contrario, se serializan. Para transferir propiedad hay que obtener confirmación de parada y *checkpoint* previo.

## Sesiones, contexto y renovación

Por defecto cada trabajador recibe contexto fresco y acotado; solo hereda historial completo ante una dependencia concreta imposible de resumir. Los chats que el usuario abre manualmente no son trabajadores adjuntos, y ningún proceso delegado persiste tras cerrar el cliente o la sesión.

En host T3, el coordinador puede renovar su propia sesión de forma autónoma (`freshContext` con un *handoff* compacto y selectivo) en puntos seguros —tras un merge confirmado, un *release*, un cierre de QA/review o un cambio de fase—, preservando todas las autorizaciones, puertas de aprobación y enlaces de evidencia.

## Comunicación entre agentes (relay)

Cuando dos participantes necesitan intercambiar mensajes entre sesiones mediante Git, [SKILL.md](../../skills/relay/SKILL.md) ofrece transporte opcional en una rama huérfana `relay/<id>` (`relay.md`), con `agentic-relay` (Claude Code), `python3 <plugin root>/scripts/agent-relay` o la API de GitHub ([GITHUB_API.md](../../skills/relay/GITHUB_API.md)).

- Solo se ejecuta bajo petición explícita (`init`, `join`, `Lee`, `$relay read`, `send`, `read --ack`, `status`, `close`), nunca de forma proactiva ni por *hooks*.
- No es cola de tareas, controlador ni canal de aprobación: `Listo - XXXX` y `Leído y registrado - XXXX` confirman publicación o lectura remota verificada, nunca aprobación ni merge.

## Trabajo multi-épica

Para iniciativas con múltiples flujos, [epic-orchestration.md](../../methodology/epic-orchestration.md) fija GitHub Issues, sub-issues y `planning-statuses` nativos como única fuente operativa, sin tableros externos. Las sub-issues nacen en `Backlog` enlazadas con `blocked_by`; solo `Todo` autoriza ejecución y cualquier dependencia abierta impide iniciar la fase dependiente. Las puertas de especificación, QA independiente y merge siguen siendo humanas y separadas.

## Fuentes canónicas

- [Orquestación principal](../../skills/orchestrate/SKILL.md)
- [Gestión dinámica de agentes](../../methodology/dynamic-agents.md)
- [Delegación en clientes externos](../../methodology/dynamic-agents-external-clients.md)
- [Orquestación multi-épica](../../methodology/epic-orchestration.md)
- [Plantilla de work packet](../../templates/agent-work-packet.md)
- [Índice de roles](../../roles/README.md)
- [Rol Functional](../../roles/functional.md)
- [Rol Implementation](../../roles/implementation.md)
- [Rol QA / Review](../../roles/qa-review.md)
- [Rol Infrastructure](../../roles/infrastructure.md)
- [Skill relay](../../skills/relay/SKILL.md)
- [Relay por API de GitHub](../../skills/relay/GITHUB_API.md)
