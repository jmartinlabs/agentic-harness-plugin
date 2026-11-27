# Parte XI — Consumo

Esta parte explica qué telemetría de consumo ofrece el plugin, cómo leer los informes locales, cómo se relaciona el coste con el tipo de trabajo y qué métricas no representan consumo real. Acude aquí para auditar sesiones de Codex o reducir gasto de contexto sin saltar puertas.

## Qué se mide

El plugin incluye dos scripts de contabilidad local, de solo lectura y *best-effort*, sin llamadas a modelo ni a red:

- `scripts/report-agent-usage` (`agentic-usage-report` en Claude Code): inspecciona rollouts JSONL bajo `$CODEX_HOME/sessions` (por defecto `~/.codex/sessions`) y agrega los eventos `token_usage_record` por respuesta de una sesión raíz (`--session <UUID>`) o turno (`--turn <UUID>`).
- `scripts/auto-agent-usage` (`agentic-usage-auto`): adaptador conectado a los hooks `Stop`, `SubagentStop` y `SessionEnd` en `hooks/codex.json`. Actualiza el informe de la sesión padre usando bloqueo POSIX (`fcntl`) y escritura atómica; si falla, emite solo un aviso no bloqueante. En `hooks/hooks.json` (Claude Code) solo hay `SessionStart` (banner de versión), sin captura automática de consumo.

**Alcance estricto:** `report-agent-usage` y `auto-agent-usage` **no miden T3 Code ni OpenCode** (ni Claude Code, Hermes o Antigravity). Solo procesan el formato de rollout de Codex; además, rechazan sustituir datos faltantes por contadores acumulados antiguos. En T3 Code, el consumo y la actividad se consultan en la telemetría propia del host (T3 Usage y actividad del hilo).

## Lectura de informes

Los informes se guardan con permisos `0600` en directorios únicos con marca UTC bajo `<CODEX_HOME>/usage-reports/<proyecto>/` (o `.../auto/<session>/`) en dos archivos: `usage.md` y `usage.csv`.

Cada fila agrupa por `Root turn` (límite de tarea), `Agent` (`/root` o `agent_path` del subagente) y `Model` (registrado en `turn_context`), mostrando `Requests`, `Input`, `Cached (included in input)` y `Output`. Reglas clave de interpretación:

- **No sumes la caché al input:** `Input` ya incluye los tokens en caché (`Cached`) y también el contexto repetido entre peticiones.
- **`NA` no es cero:** si falta alguna categoría de tokens en un registro, se muestra `NA` y se añade una advertencia; los informes reflejan solo el instante capturado y pueden ser incompletos en sesiones aún activas.

## Coste por tipo de trabajo

La clasificación en `workflows.md` y `orchestrate` escala el esfuerzo según el riesgo:

- **Quick:** un único worker acotado con plan de una línea y pruebas focalizadas.
- **Standard:** feature acotada con plan breve, casos borde, tests y revisión.
- **Full:** especificación aprobada, desarrollo incremental, QA independiente y revisión de código.

El consumo crece sobre todo con las rondas de corrección, las relecturas completas y el historial acumulado. Aun así, límites o cuotas **nunca** autorizan omitir QA independiente, pruebas de seguridad o aprobaciones humanas.

## Reducción

Para contener el consumo de tokens sin degradar la calidad:

1. Usa contexto fresco acotado por defecto en subagentes y paquetes de trabajo compactos.
2. Haz lecturas parciales de archivos y filtra salidas en origen; evita releer sin cambios.
3. Sustituye el polling de CI por PR Watch en hosts compatibles o consultas espaciadas.
4. Renueva el contexto del coordinador en puntos seguros (`freshContext`) antes de que el historial se infle.
5. Reserva los perfiles `complex` de la configuración v2 para tareas con incertidumbre o riesgo real, dejando `standard` para trabajo acotado.

## Qué no es consumo

- Los conteos de tokens **no equivalen** a dinero, ni a cuota de suscripción, ni al tamaño actual de la ventana de contexto (referencia orientativa de ~150k/200k en T3).
- No es consumo válido ninguna cifra estimada o inferida sin telemetría real: está prohibido inventar porcentajes, costes o ejecuciones a partir de prompts enviados.

## Fuentes canónicas

- [Script `report-agent-usage`](../../scripts/report-agent-usage)
- [Script `auto-agent-usage`](../../scripts/auto-agent-usage)
- [Hooks de Codex](../../hooks/codex.json)
- [Hooks de Claude Code](../../hooks/hooks.json)
- [Contrato de flujos adaptativos](../../methodology/workflows.md)
- [Gestión dinámica de agentes](../../methodology/dynamic-agents.md)
- [Skill `orchestrate`](../../skills/orchestrate/SKILL.md)
- [README del plugin](../../README.md)
