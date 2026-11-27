# Parte VIII — Git

Describe cómo gestionar ramas, *worktrees* aislados, el checkout principal del coordinador, la actualización y limpieza local tras un merge y la recuperación segura ante errores. Acude a este capítulo antes de aislar trabajo concurrente, actualizar la rama base o limpiar recursos locales.

## Ramas y aislamiento de escritura

Cada tarea de escritura opera en su propia rama y nunca directamente sobre la rama base configurada del proyecto (por ejemplo `main` o una rama de desarrollo como `test`).

Cambiar de rama dentro de un único directorio **no** aísla archivos sin confirmar ni trabajo concurrente: cuando varios escritores trabajan en paralelo, cada uno necesita un *worktree* separado y propiedad de archivos disjunta ([dynamic-agents.md](../../methodology/dynamic-agents.md), sección *Ownership, stopping and recovery*). Si no es posible garantizar ambas condiciones, las escrituras se serializan.

La autorización para realizar una tarea —de código o documentación— autoriza también a publicar su rama y abrir o actualizar su PR en el repositorio existente, salvo instrucción explícita de mantener el trabajo solo en local ([approvals.md](../../methodology/approvals.md), sección *Branch and PR publication*). Antes de hacer `push`, revisa el diff, los archivos en *stage*, posibles secretos y cambios ajenos.

## Worktrees locales

Crear un *worktree* local no requiere aprobación individual cuando cumple tres condiciones ([approvals.md](../../methodology/approvals.md), sección *Local worktrees*):

1. Respalda trabajo ya autorizado por el usuario.
2. Aporta aislamiento útil.
3. No afecta a trabajo existente.

Antes de crearlo, comprueba el alcance autorizado, `git status` (cambios sin confirmar o sin rastrear), los *worktrees* existentes, la rama y la ruta destino. Usa siempre una ubicación nueva y sin conflictos; nunca sobrescribas, muevas ni descartes cambios previos. En host T3, el aislamiento se solicita en la delegación (`isolation: "worktree"` en `delegate_task`), nunca creando el *worktree* manualmente dentro del prompt del trabajador. Si un proyecto derivado exige aprobación por cada *worktree*, esa regla más estricta prevalece.

## El checkout principal del coordinador

El checkout principal del coordinador permanece siempre en la rama base configurada y actúa únicamente como superficie de coordinación ([dynamic-agents.md](../../methodology/dynamic-agents.md), sección *Coordinator main checkout*). Nunca se cambia a una rama de tarea ni se aplican allí cambios de los trabajadores.

- **Al inicio de sesión:** inspecciona rama actual, `HEAD`, cambios en *stage*, sin *stage* o sin rastrear, lista de *worktrees* y relación con el *upstream* de la rama base. Informa el estado observado y conserva cualquier cambio inesperado; si bloquea el trabajo autorizado, detente y pregunta.
- **Actualización tras merge:** el *auto-pull* del host (como en T3 cuando está activado) es opcional. Si ya actualizó el checkout, verifica rama, `HEAD` y limpieza sin repetir el `pull`. Si no lo actualizó, y el checkout está limpio, en la rama base y sin commits locales ni divergencia, avanza manualmente con `git pull --ff-only` (o `git merge --ff-only`). Si no es posible un *fast-forward*, conserva el estado y reporta el bloqueo.

## Limpieza local tras el merge

Solo después de recibir aprobación explícita de merge **y** confirmar que la PR está en estado `MERGED`, eliminar el *worktree* y la rama local de esa tarea es cierre ordinario autorizado ([approvals.md](../../methodology/approvals.md), sección *Post-merge local cleanup*).

Antes de borrar, verifica todas estas condiciones:

1. El *worktree* y la rama pertenecen exclusivamente a esa tarea (nunca `main`, el checkout actual ni otras tareas).
2. Ningún agente o sesión activa es dueño de ellos; ante duda, conservar.
3. La PR está `MERGED` con commit de merge conocido y la rama local no tiene commits más allá del candidato fusionado.
4. El *worktree* está limpio (sin cambios en *stage*, sin *stage*, sin rastrear ni archivos ignorados relevantes).

Ejecuta únicamente la secuencia segura, sin `--force` ni `-D`:

```sh
git worktree remove <task-worktree>
git branch -d <task-branch>
```

Los merges *squash* y *rebase* son válidos. Si `git branch -d` rechaza el borrado porque Git no puede probar la integración, conserva la rama y repórtalo; nunca cambies a `-D` ni borres ramas remotas en esta limpieza.

## Prohibiciones y recuperación segura

Están prohibidas las operaciones destructivas o forzadas: `git reset --hard`, `git clean -fd`, `git checkout -- .`, `git pull --force`, `git push --force`, `git worktree remove --force` y `git branch -D`.

Ante salidas fuera de alcance, conflictos o un árbol sucio inesperado, detente, inspecciona y preserva todos los cambios existentes antes de aplicar una recuperación selectiva y reversible sobre las ediciones atribuibles ([dynamic-agents.md](../../methodology/dynamic-agents.md), sección *Ownership, stopping and recovery*).

## Fuentes canónicas

- [Aprobaciones, worktrees y limpieza](../../methodology/approvals.md)
- [Gestión dinámica de agentes](../../methodology/dynamic-agents.md)
- [Delegación en clientes externos](../../methodology/dynamic-agents-external-clients.md)
- [Orquestación principal](../../skills/orchestrate/SKILL.md)
