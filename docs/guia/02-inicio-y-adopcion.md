# Parte II — Inicio y adopción

Esta guía explica cómo iniciar un proyecto nuevo con el plugin, adoptar la metodología en un repositorio existente sin perder código ni decisiones, identificar qué archivos posee cada proyecto y recorrer el primer ciclo completo.

## Proyecto nuevo

Cuando el repositorio aún no tiene código funcional ni decisiones aprobadas:

1. **Comprueba la preparación:** ejecuta `verify-project` (o `python3 <plugin-root>/scripts/verify-project.py`). Si estás dentro del checkout del propio plugin o plantilla, crea o abre primero un repositorio independiente para tu aplicación.
2. **Inicializa con `init-project`:** el skill `init-project` coordina siete etapas secuenciales y guarda el avance en `specs/setup-progress.md` para poder pausar y reanudar sin reiniciar desde cero:
   - **Etapa 1 (Identity):** nombre, objetivo, usuarios y problema en `specs/project.md`.
   - **Etapa 2 (Technology):** opciones de stack y aprobación explícita de decisiones materiales.
   - **Etapa 3 (Architecture):** estructura, módulos, datos, seguridad y pruebas antes de escribir código.
   - **Etapa 4 (Bootstrap):** delega en `bootstrap` para construir el *walking skeleton* mínimo extremo a extremo, pruebas automatizadas, comando único de verificación local/CI y cumplimiento del contrato de CI en `specs/guidelines/quality.md`.
   - **Etapa 5 (Guidelines):** completa `specs/guidelines/` (`architecture.md`, `ui.md`, `quality.md`, `security.md`) y fusiona descripción y comandos reales en `AGENTS.md`.
   - **Etapa 6 (Roadmap):** genera `specs/roadmap.md` con `roadmap` y, si hay tracker disponible, deja las Issues de planificación en `Backlog` (nunca en `Todo`).
   - **Etapa 7 (Handoff):** resume enlaces y próximos pasos (`spec` 01 y luego `dev` 01).

## Proyecto existente

Si el repositorio ya tiene código operativo o decisiones aprobadas, **no** uses `init-project` ni `bootstrap`: usa `adopt-project`.

1. **Inventario en solo lectura:** antes de tener `AGENTS.md` o `CLAUDE.md`, ejecuta:
   ```sh
   python3 <plugin-root>/scripts/verify-project.py --inventory --project <ruta-proyecto>
   ```
   Requiere solo una raíz Git. Revisa `plugin_owned_paths_in_project` para detectar copias locales obsoletas de `skills/`, `roles/`, `methodology/`, `agents/` o `templates/`.
2. **Plan y evaluación de CI:** `adopt-project` inspecciona estado Git, reglas locales y workflows existentes. Propone un plan archivo por archivo y la eliminación de copias propiedad del plugin (trasladando antes cualquier regla propia a `specs/project-rules.md`). Conserva la identidad de los checks obligatorios de CI sin sustituirlos por los de la plantilla.
3. **Integración tras aprobación:** en una rama aislada cuando sea posible, fusiona (sin sobrescribir) `AGENTS.md` y `CLAUDE.md` (que debe incluir `@AGENTS.md`), conserva intactos los archivos `.agents/harnesses/*.json` y añade solo los documentos de `specs/` aprobados en el plan.
4. **Nota sobre referencias internas:** el skill `adopt-project` menciona *model selection* entre las áreas de metodología, y `roles/README.md` remite a `AGENTS.md` para los límites de rol; la configuración de modelos y rutas de delegación está documentada en [dynamic-agents.md](../../methodology/dynamic-agents.md) (sección *Coordinator configuration*), no en un archivo separado.

## Archivos que posee el proyecto

El plugin nunca se copia al proyecto. El repositorio conserva únicamente sus archivos propios:

- **Entrada e instrucciones:** `AGENTS.md` (con el preflight de coordinación), `CLAUDE.md` (`@AGENTS.md`) y `specs/project-rules.md` (reglas locales y puertas adicionales).
- **Configuración de modelos:** `.agents/harnesses/<coordinador>.json` en clientes standalone (`claude`, `codex`, `opencode`, `hermes`, `antigravity`), o `.agents/harnesses/t3.json` y `.agents/harnesses/t3.local.json` en el host T3 (el README raíz omite los archivos `t3*.json`, pero el validador y `orchestrate` los reconocen). Valida con `scripts/validate-core --project <dir>`.
- **Documentos generados en `specs/`:** definidos en [document-ownership.md](../../methodology/document-ownership.md) (`project.md`, `setup-progress.md`, `guidelines/*.md`, `roadmap.md`, `NN-slug-*.md` y `session-handoff.md` temporal).

## Primer ciclo completo

Con el proyecto inicializado o adoptado:

1. Define una capacidad con `spec` (`specs/NN-slug-brainstorming.md` y `specs/NN-slug-specification.md`) y obtén aprobación explícita si es trabajo Full.
2. Coordina la ejecución con `orchestrate` (o toma una Issue autorizada con `work-issue`), delegando la implementación en un subagente con paquete acotado.
3. Pasa QA independiente antes de marcar la tarea lista y solicita aprobación explícita para hacer merge de la PR.

## Proyecto que no adopta la metodología

Puedes usar el plugin instalado en un repositorio sin `AGENTS.md` ni carpeta `specs/` para tareas puntuales (por ejemplo con `tweak` o `task`). En ese escenario:

- `verify-project.py` en modo por defecto fallará por ausencia de `AGENTS.md` y `CLAUDE.md`; usa `--inventory` si solo quieres inspeccionar el repositorio.
- Siguen aplicando las reglas de aprobación explícita ([approvals.md](../../methodology/approvals.md)) y las restricciones locales del proyecto si existe `specs/project-rules.md`.

## Fuentes canónicas

- [Propiedad de documentos](../../methodology/document-ownership.md)
- [Skill init-project](../../skills/init-project/SKILL.md)
- [Skill adopt-project](../../skills/adopt-project/SKILL.md)
- [Skill bootstrap](../../skills/bootstrap/SKILL.md)
- [Gestión dinámica de agentes](../../methodology/dynamic-agents.md)
- [Política de aprobaciones](../../methodology/approvals.md)
- [Roles de especialistas](../../roles/README.md)
- [Configuración T3 de ejemplo](../../.agents/harnesses/t3.json)
