# Parte IX — PR Watch

Esta parte explica cómo vigilar una Pull Request mientras espera checks de CI o revisión sin caer en bucles de sondeo manual. Acude aquí al entregar una PR y al despertar tras una notificación de estado.

## Ciclo de vida

La vigilancia nativa sustituye las consultas repetidas (`gh pr checks`, `gh pr view`, bucles `sleep` o temporizadores). Su ciclo sigue estas reglas:

1. **Activar una sola vez:** inicia el watch al entregar la PR (en borrador o lista, según la puerta del proyecto) cuando el paso siguiente sea esperar checks o revisión. Nunca lo actives antes de que exista la PR ni después de cerrar QA.
2. **Enlazar y vigilar:** en hosts con herramientas nativas de PR (como T3 Code), usa `link_pull_request` y `watch_pull_request` con `until: "checks"`. Usa `until: "merged"` únicamente cuando tengas autorización explícita para actuar tras una aprobación de merge.
3. **No sondear mientras vigila:** con el watch activo, evita consultas manuales repetidas de CI.
4. **Gobernanza intacta en `gh`:** el watch no sustituye las puertas del repositorio; `planning-statuses`, reservas, transiciones de Issue, `blocked_by`, aprobación explícita de merge, SHA final y verificación final de CI siguen operando en `gh`.

## Al despertar

Cuando el watch despierte el turno, ejecuta una secuencia mínima:

1. **Una sola lectura consolidada:** llama a `pull_request_read` con `include: ["checks", "threads", "comments"]`.
2. **Un único log si hay fallo:** si algún check falló, ejecuta `ci_logs` una sola vez para diagnosticar.
3. **Actuar o informar:** corrige si está en alcance o reporta el estado y cierra el turno.

Un despertar **nunca autoriza un merge**. El auto-merge está prohibido; siguen siendo obligatorios la aprobación humana explícita e identificable, `expectedHeadSha`, la verificación final de CI y la QA/revisión independiente.

## Fin de vigilancia

Un despertar no equivale al fin del watch:

- **No** llames a `unwatch_pull_request` en cada despertar ni mientras sigan pendientes checks o revisiones.
- Llama a `unwatch_pull_request` **solo** cuando la vigilancia termine de forma permanente (devolución final sin más espera) o para detener un watch que ya no hace falta.
- Si el watch terminó por merge o cierre de la PR, no es necesario llamar a `unwatch_pull_request`.

## Fallback por cliente

El soporte de vigilancia nativa depende del cliente y del rol:

| Superficie / Rol | Watch nativo | Fallback cuando no aplica o falla |
| --- | --- | --- |
| Coordinador en host T3 | `link_pull_request` + `watch_pull_request` + `pull_request_read` | Si el watch se corta, haz **una** lectura puntual y marca el estado como no verificado (no inventes estado ni re-vigiles a ciegas). |
| Workers / subagentes delegados | No vigilan (ni aunque el brief lo pida) | El coordinador padre asume el watch tras la entrega del hijo. |
| Clientes standalone (Claude Code, Codex, OpenCode, Hermes, Antigravity sin MCP de PR del host) | Sin watch nativo en el plugin | Consultas espaciadas progresivamente con `gh`, siempre sin bucles, `gh pr checks --watch`, `sleep` ni temporizadores. |

## Medición

No se añade instrumentación nueva para evaluar PR Watch: se usa la telemetría existente del host (T3 Usage y actividad del hilo). El método consiste en comparar una línea base de **5 PRs sin watch** frente a un piloto de **5 PRs con watch** midiendo medianas de:

- turnos del coordinador;
- operaciones en GitHub;
- despertares del hilo;
- tiempo transcurrido de `ready` a `merge`, además de registrar cualquier falso negativo.

## Fuentes canónicas

- [Skill `work-issue`](../../skills/work-issue/SKILL.md) (sección *PR watch*)
- [Política de aprobaciones](../../methodology/approvals.md) (secciones *Protected decisions* y *Branch and PR publication*)
- [Política de CI](../../methodology/ci-policy.md)
- [Historial de cambios](../../CHANGELOG.md) (entrada `2.2.0`)
