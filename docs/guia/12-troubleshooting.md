# Parte XII — Resolución de problemas

Método sistemático para diagnosticar y resolver fallos frecuentes en instalación, modelos, Issues, Git/worktrees y PR/CI antes de reintentar o forzar estados.

## 1. Método de diagnóstico

1. **Reproduce y observa:** registra el comando, código de salida y salida real; nunca asumas éxito sin evidencia.
2. **Aísla la capa:** cliente (permisos, caché, hooks), plugin (`validate-core`, `verify-project.py`), proyecto (`.agents/harnesses/*.json`), Git/worktree local o GitHub (Issues, PR, CI).
3. **Corrige de forma reversible:** preserva cambios locales y detente ante ambigüedad de alcance o autorización.

## 2. Instalación y clientes

- **Claude Code deniega lecturas del plugin:** obtén `installPath` con `claude plugin list --json`, ejecuta `python3 "<installPath>/scripts/verify-project.py" --print-rules` y añade `Read(//<installPath>/**)` y `Bash(agentic-*:*)` a `.claude/settings.local.json`. Refresca `Read` tras actualizar.
- **Hooks inactivos en Codex CLI:** confíalos con `/hooks` tras instalar o actualizar. Comprueba que no exista un `plugin.json` en la raíz que suprima `hooks/codex.json`.
- **Antigravity sin agentes ni hooks:** comportamiento esperado; instala desde `stable` (sin pin por tag/SHA) y carga solo `.antigravity-plugin/plugin.json` y las 13 skills por nombre simple.
- **OpenCode o Hermes desactualizados:** ejecuta `python3 <plugin-root>/scripts/update-agentic --check`. En Hermes, los perfiles bajo `$HERMES_HOME/profiles/*/` sin symlink a `<shared-repo>/skills` o con copias locales muestran aviso; `update-agentic` no repara symlinks de perfiles.
- **Plugin habilitado pero no instalado:** falla abierto sin aplicar reglas; instala explícitamente en ámbito de usuario ([README](../../README.md)).
- **Copias locales que eclipsan al plugin:** si `verify-project.py` detecta `.agents/skills`, `.claude/agents` o `specs/methodology`, usa `adopt-project` para inventariar y proponer su retirada (requiere aprobación).

## 3. Modelos y configuración v2

- **`validate-core --project` devuelve 1:** exige JSON estricto (sin claves duplicadas ni `NaN`/`Infinity`), `version: 2`, campos permitidos y rutas dentro del proyecto. Elimina `.agents/external-agents.json` si persiste.
- **Host T3 detiene el dispatch por rol sin configurar:** si existe `.agents/harnesses/t3.local.json`, es el único archivo activo sin herencia de `t3.json` ni nativa. Define el perfil del rol o `local.provider` y `local.model` en ese mismo archivo.
- **Proveedor o modelo no disponible:** nunca sustituyas proveedor ni modelo; detén el dispatch e informa.
- **Esfuerzo no expuesto en el host:** si proveedor y modelo existen pero `effort` no está soportado (ej. `medium` en Antigravity Hydrogen), despacha sin la opción nativa de esfuerzo manteniendo proveedor y modelo exactos, y registra `UNVERIFIED`.
- **Discrepancia `requested` vs `observed`:** identidad distinta marca `FAIL` (no confiar en la ejecución); falta de metadatos registra `UNVERIFIED`.
- **Perfiles nativos v2 en standalone:** no soportados hasta pasar verificación funcional en la superficie y versión del cliente ([dynamic-agents.md](../../methodology/dynamic-agents.md)).

## 4. Issues y flujo en GitHub

- **`planning-statuses` devuelve 404 o no está disponible:** detente y pide autorización humana; no asumas cola vacía ni inventes estados locales.
- **Issues abiertas con `status=null`:** repórtalas como sin estado, nunca como cola vacía.
- **`blocked_by` en `Not planned` o `Duplicate`:** solo `Done` desbloquea; retira `blocked_by` si sobra o corrige la referencia.
- **Issue pasó de `Backlog` a `Todo` sola:** nunca uses GitHub assignees (disparan `Backlog` → `Todo` sin revertir). Enruta con `agent:<cliente>`.
- **Colisión de reserva blanda:** tras `PATCH` `"In progress"` y `Reserva:`, relee una vez tras 10–15 s (sin polling). En la misma ronda gana el timestamp de servidor más antiguo; el otro se detiene sin escribir más.

## 5. Git y worktrees

- **Checkout principal del coordinador desviado o sucio:** prohibido `checkout`, `reset --hard` o `clean -fd`. Preserva los cambios e informa si bloquean.
- **`git pull --ff-only` falla tras merge:** si el host ya actualizó con auto-pull, verifica `HEAD` y limpieza; si hay divergencia, preserva e informa.
- **`git branch -d` rechaza borrar tras merge:** conserva la rama e informa; nunca uses `git branch -D` ni `git worktree remove --force`.

## 6. PR, CI y validación

- **PR abierta vuelve a `In review`:** reabrir una PR lista o marcarla ready con `Closes #N` fuerza `In review`. En rechazo con `Closes`, pasa la PR a draft y la Issue a `Todo`; con `Refs #N`, vuelve a `Todo` directamente.
- **CI ejecuta `full` en cambios de docs:** comprueba si se tocaron rutas protegidas (`AGENTS.md`, `skills/`, `.agents/`) según [ci-policy.md](../../methodology/ci-policy.md); ante duda, CI usa `full`.
- **`validate-core` falla por neutralidad o enlaces:** revisa rutas locales de usuario o enlaces rotos/con `#ancla`.

## 7. Cuándo escalar

Escala sin improvisar ni forzar cuando falte una autorización protegida (merge, SPEC Full, despliegue, borrado), haya ambigüedad en reservas o Git, falle `planning-statuses`, falte un proveedor/modelo o falte una regla en el work packet.

## Fuentes canónicas

- [README.md](../../README.md)
- [methodology/dynamic-agents.md](../../methodology/dynamic-agents.md)
- [methodology/issue-workflow.md](../../methodology/issue-workflow.md)
- [methodology/approvals.md](../../methodology/approvals.md)
- [methodology/ci-policy.md](../../methodology/ci-policy.md)
- [scripts/validate-core](../../scripts/validate-core)
- [scripts/verify-project.py](../../scripts/verify-project.py)
- [scripts/update-agentic](../../scripts/update-agentic)
