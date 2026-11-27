# Parte V — Autorizaciones

Este capítulo resume qué decisiones están protegidas por aprobación humana explícita, qué trabajo puede avanzar sin pedir permiso en cada paso y cómo se autorizan la publicación y el merge. Acude aquí ante cualquier duda sobre si puedes avanzar, publicar o fusionar cambios.

## Puertas protegidas

La política en [approvals.md](../../methodology/approvals.md) es una puerta a nivel de instrucciones (la protección técnica dura requiere hooks o rulesets de GitHub; las reglas más estrictas de un proyecto siempre prevalecen). Requieren aprobación explícita del usuario por separado:

- Mergear una PR.
- Aprobar una especificación *Full*, wireframes o una decisión sustantiva de producto o financiera.
- Autorizar desarrollo, cuando el proyecto mantiene puerta separada de desarrollo.
- Cambios materiales de seguridad o arquitectura.
- Acciones destructivas.
- Despliegue a producción o migración de datos operativos.
- Cualquier otra aprobación exigida por el proyecto.

Regla invariable: CI en verde, QA aprobado, un plan preaprobado, una autorización previa de alcance o código terminado **nunca implican** aprobación de otra acción protegida.

## Qué autoriza y qué no

1. **Trabajo ordinario**: dentro de un alcance ya autorizado por el usuario, no necesitan aprobación por paso la implementación, los tests, el uso de subagentes, los worktrees locales que cumplan la política (apoyo a trabajo autorizado, aislamiento útil, sin afectar trabajo existente) ni la publicación de rama y PR de ese trabajo.
2. **Aprobación válida**: exige un verbo explícito de aprobación y un objetivo identificable uno a uno (por ejemplo, `Apruebo PR #34`, `Approve PR #34 merge`, `I approve specification 07`). Un `Approved`, `Aprobado` o `Apruebo` aislado solo vale si responde inmediatamente a una única petición concreta recién formulada.
3. **Lo que nunca aprueba**: `ok`, `okk`, `dale`, `continúa`, `continue`, `go ahead`, `adelante`, el silencio, las reacciones o cualquier asentimiento genérico solo permiten continuar trabajo ya autorizado, nunca superar una puerta protegida. Tampoco sirve como evidencia un mensaje de commit o nota de agente que diga que el usuario aprobó.
4. **Invalidación por cambios**: cualquier cambio material posterior a la aprobación (nuevo SHA, nuevo contenido o nuevo artefacto) requiere nueva aprobación.
5. **Issues y workflows**: en Issues ([issue-workflow.md](../../methodology/issue-workflow.md)), solo el estado `Todo` autoriza ejecución (nunca comentarios, etiquetas `agent:*` ni `Backlog`). En [workflows.md](../../methodology/workflows.md), *Quick* puede ejecutarse tras un plan de una línea solo si es reversible, de bajo riesgo y sin puerta protegida; *Standard* y *Full* requieren confirmación previa salvo autorización explícita vigente.

## Matriz de autorizaciones

| Acción | Qué la autoriza | Qué NO la autoriza |
| --- | --- | --- |
| Ejecutar Issue | Estado `Todo` + dependencias `Done` | `Backlog`, comentarios, etiquetas `agent:*`, assignees |
| Implementar / tests / subagentes | Alcance ya autorizado (`Standard`/`Full`/`Todo`) | Modo solo lectura, consulta o planificación |
| Worktree local | Alcance autorizado + aislamiento sin conflictos | Regla de proyecto que exija permiso por worktree |
| Publicar rama y abrir/editar PR | Autorización del trabajo (código, docs o spec) | Instrucción `local only` / `no publicar`, flujo *handoff* |
| Aprobar especificación *Full* | Verbo explícito + ID y revisión de spec | Mergear PR de spec, `dale`, QA previo |
| Mergear PR | Verbo explícito + número de PR y HEAD SHA | CI verde, QA `passed`, auto-merge, `ok` |
| Limpieza local post-merge | Aprobación de merge + PR confirmada `MERGED` | Borrado remoto, `--force`, `-D`, checkout principal |

## Publicación, merge y limpieza post-merge

- **Publicación de rama y PR**: autorizar el trabajo autoriza publicar su rama y crear o actualizar su PR en el repositorio existente (siempre actualizando la PR existente en vez de duplicarla). Antes de hacer `push`, revisa el diff, los archivos en stage, posibles secretos y cambios ajenos. Se permite PR en borrador mientras falten checks o decisiones, pero crear o mergear una PR de especificación no aprueba su contenido ni autoriza desarrollo. Esta autorización ordinaria no cubre crear repositorios, cambiar visibilidad, `push` directo a ramas protegidas, `push --force`, releases, paquetes ni despliegues.
- **Merge de PR**: exige siempre aprobación explícita e identificable para esa PR y su candidato (`expectedHeadSha`). Está prohibido activar auto-merge como atajo. Antes de fusionar, reverifica el HEAD actual y los checks requeridos.
- **Limpieza local post-merge**: una vez aprobada la fusión de forma explícita **y** confirmada la PR como `MERGED`, borrar el worktree local (`git worktree remove` sin `--force`) y la rama local (`git branch -d` sin `-D`) de esa tarea es cierre ordinario, previa verificación de exclusividad, ausencia de cambios sin guardar y ausencia de commits fuera del candidato mergeado. Si `git branch -d` falla o hay dudas, conserva el recurso y repórtalo. El checkout principal del coordinador sigue sus propias reglas en [dynamic-agents.md](../../methodology/dynamic-agents.md).

## Fuentes canónicas

- [approvals.md](../../methodology/approvals.md)
- [workflows.md](../../methodology/workflows.md)
- [issue-workflow.md](../../methodology/issue-workflow.md)
- [dynamic-agents.md](../../methodology/dynamic-agents.md)
