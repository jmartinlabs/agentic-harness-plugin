# Parte I — Instalación y mantenimiento

Esta guía cubre la instalación global del plugin `agentic` (v2.2.1) en los cinco clientes soportados, su verificación, actualización, rollback y modelo de permisos. Acude aquí al configurar un equipo nuevo, cambiar de versión o resolver problemas de confianza y rutas.

## Requisitos y distribución

- **Requisitos:** Python 3.10 o superior para hooks, diagnóstico de preparación y herramientas CLI (`scripts/`).
- **Canal:** todas las instalaciones recomendadas siguen la rama `stable`.
- **Modelo de distribución:** el plugin se instala una vez por usuario y cliente desde el marketplace `agentic-harness`. Sus manifiestos (`.claude-plugin/plugin.json`, `.codex-plugin/plugin.json` y `.antigravity-plugin/plugin.json`) declaran la versión `2.2.1`; `.claude-plugin/marketplace.json` publica el catálogo. El plugin conserva `skills/`, `methodology/`, `roles/`, `templates/`, `scripts/` y `agents/`; ningún proyecto copia esos directorios.
- **Binarios y shims:** en Claude Code, `bin/agentic-*` (`agentic-verify-project`, `agentic-relay`, `agentic-check-delegation-route`, `agentic-usage-report`, `agentic-usage-auto`) queda en `PATH` mientras el plugin está activo. En el resto de clientes se ejecuta `python3 <plugin-root>/scripts/<herramienta>`.

## Instalación por cliente

Instala a nivel de usuario (`--scope user` o equivalente) una sola vez por cliente:

1. **Claude Code:**
   ```sh
   claude plugin marketplace add https://github.com/jmartinlabs/agentic-harness-plugin.git#stable --scope user
   claude plugin install agentic@agentic-harness --scope user
   ```
2. **Codex CLI:**
   ```sh
   codex plugin marketplace add https://github.com/jmartinlabs/agentic-harness-plugin.git --ref stable
   codex plugin add agentic@agentic-harness
   ```
   Después revisa y confía en los hooks con `/hooks`.
3. **Antigravity:**
   ```sh
   antigravity plugin install https://github.com/jmartinlabs/agentic-harness-plugin/tree/stable
   ```
   Instala globalmente en `$HOME/.gemini/config/plugins/agentic` desde la rama (no fija un SHA). Carga los 13 skills como nombres planos (por ejemplo `verify-project`, `orchestrate`) e ignora `agents/*.md` y `hooks/hooks.json`.
4. **OpenCode:**
   Clona `stable` en `~/.local/share/agentic-harness-plugin` y enlaza adaptadores y cada skill individualmente en `~/.config/opencode/` (`agents/`, `plugins/review-read` y `skills/*`) para no pisar skills previos:
   ```sh
   git clone --branch stable https://github.com/jmartinlabs/agentic-harness-plugin.git ~/.local/share/agentic-harness-plugin
   mkdir -p ~/.config/opencode/agents ~/.config/opencode/plugins ~/.config/opencode/skills
   for agent in ~/.local/share/agentic-harness-plugin/adapters/opencode/agents/*.md; do
     ln -sfn "$agent" ~/.config/opencode/agents/"$(basename "$agent")"
   done
   ln -sfn ~/.local/share/agentic-harness-plugin/adapters/opencode/plugins/review-read ~/.config/opencode/plugins/review-read
   for skill in ~/.local/share/agentic-harness-plugin/skills/*; do
     ln -sfn "$skill" ~/.config/opencode/skills/"$(basename "$skill")"
   done
   ```
5. **Hermes Agent:**
   Clona `stable` en `${XDG_DATA_HOME:-$HOME/.local/share}/agentic-harness-plugin` y enlaza `skills/*` dentro de `${HERMES_HOME:-$HOME/.hermes}/skills`. Lanza siempre `hermes` desde la raíz del proyecto para que cargue `AGENTS.md`. Consulta la guía completa de perfiles y `model_map` en [el adaptador de Hermes](../../adapters/hermes/README.md).

## Verificación

- **Estado global de clientes:** ejecuta `python3 <plugin-root>/scripts/update-agentic --check` (solo lectura). Informa versión y estado de Claude Code, Codex, OpenCode, Hermes (incluidos perfiles bajo `profiles/*/`) y Antigravity sin modificar nada ni iniciar sesiones.
- **Preparación de un proyecto:** dentro del repositorio destino ejecuta `agentic-verify-project` (Claude Code) o `python3 <plugin-root>/scripts/verify-project.py` (otros clientes, con `--coordinator <cliente>` si aplica).
- **Configuración v2 del proyecto:** valida `.agents/harnesses/*.json` con `python3 <plugin-root>/scripts/validate-core --project <directorio-proyecto>`.

## Actualización

1. Para actualizar todos los clientes ya instalados en un paso (sin instalar los ausentes):
   ```sh
   python3 <plugin-root>/scripts/update-agentic
   ```
2. Para actualizar un cliente concreto, usa su gestor (`claude plugin marketplace update agentic-harness` + `claude plugin update agentic@agentic-harness --scope user`; `codex plugin marketplace upgrade agentic-harness`; en Antigravity desinstala y reinstala desde `tree/stable`; en OpenCode/Hermes haz `git pull --ff-only` sobre `stable` y re-enlaza `skills/*` si cambió el conjunto).
3. Inicia una sesión nueva en el cliente para cargar la versión actualizada.

## Rollback y migración

- **Rollback:** ejecuta la desinstalación o retirada del marketplace **fuera de cualquier proyecto** (en Claude Code evita hacerlo dentro de un proyecto para no alterar `.claude/settings.json`) y reinstala sustituyendo `stable` por una etiqueta publicada (por ejemplo `v1.2.0`). En OpenCode y Hermes basta con `git fetch --tags` y `git checkout <etiqueta>`.
- **Migración desde otro origen o ref:** desinstala y retira el marketplace antiguo fuera de cualquier proyecto, limpia referencias obsoletas al plugin en los ajustes del proyecto (conservando `.agents/harnesses/` y reglas propias) y reinstala desde `stable`.

## Permisos y confianza

- **Claude Code:** si deniega la lectura de archivos del plugin, obtén `installPath` con `claude plugin list --json` y ejecuta `python3 "<installPath>/scripts/verify-project.py" --print-rules`. Añade las reglas `Read(//<installPath>/**)` y `Bash(agentic-*:*)` a `.claude/settings.local.json` (no versionado) y refresca la regla `Read` tras cada actualización.
- **Codex CLI:** revisa y aprueba los hooks con `/hooks` después de cada instalación, actualización o rollback (`update-agentic` nunca aprueba hooks automáticamente).
- **Hermes Agent:** no uses `--yolo` ni `approvals.mode: off`; la aprobación de comandos de shell no sustituye a las puertas de decisión.
- **Alcance de la confianza:** los hooks y las reglas de skills operan a nivel de instrucciones, no como aislamiento duro del sistema operativo; la política de decisiones protegidas reside en [approvals.md](../../methodology/approvals.md).

## Fuentes canónicas

- [README del plugin](../../README.md)
- [Adaptador de Hermes](../../adapters/hermes/README.md)
- [Política de aprobaciones](../../methodology/approvals.md)
- [Skill verify-project](../../skills/verify-project/SKILL.md)
- [Script update-agentic](../../scripts/update-agentic)
- [Script validate-core](../../scripts/validate-core)
