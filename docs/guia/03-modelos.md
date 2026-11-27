# Parte III — Configuración de modelos

Esta guía explica cómo configurar qué proveedor, modelo y nivel de esfuerzo (`effort`) usa el coordinador al delegar tareas, tanto en clientes standalone como en el host T3. Acude a este capítulo antes de editar `.agents/harnesses/` o diagnosticar por qué un worker usó un modelo inesperado.

## Standalone frente a host T3

El esquema v2 separa dos contextos de ejecución con reglas distintas, definidas en [dynamic-agents.md](../../methodology/dynamic-agents.md) (secciones *Coordinator configuration*, *Native role profiles* y *Host worker configuration*):

- **Coordinador standalone** (`claude`, `codex`, `opencode`, `hermes`): lee `.agents/harnesses/<cliente>.json`. Si el archivo no existe, la delegación nativa sigue sus reglas habituales y no habilita clientes externos. Si existe pero es ilegible o inválido, el despacho se detiene. Los workers nunca leen la configuración del coordinador ni delegan.
- **Host T3** (orquestador multiproveedor): lee `.agents/harnesses/t3.json` (versionado) o `.agents/harnesses/t3.local.json` (opcional, en `.gitignore`, editable sin PR). La configuración vive solo bajo `.agents/harnesses/` en la raíz principal del proyecto, nunca en un worktree ni en un `t3.json` raíz nativo.

> Nota documental: el [README.md](../../README.md) principal no menciona `t3.json` ni `t3.local.json`; la referencia normativa está en [dynamic-agents.md](../../methodology/dynamic-agents.md) y en [validate-core](../../scripts/validate-core). Asimismo, la sección *Model advice* de `workflows.md` está vacía: toda la configuración de modelos remite a `dynamic-agents.md`.

## Referencia del esquema v2

No existe lector ni fallback v1. Todo archivo debe ser JSON estricto (claves únicas, sin `NaN`/`Infinity`) con `"version": 2`:

- **Standalone (`<cliente>.json`)**: admite `local` (`model`, `effort` y `profiles` por rol canónico `functional`, `implementation`, `qa-review`, `infrastructure` con niveles `standard` y `complex`) y `external` (clientes CLI externos con `enabled`, `transport: "cli"`, `model`, `effort` y `tasks`: `review`, `investigate`, `develop`). En standalone, los perfiles nativos v2 siguen marcados como no soportados hasta superar verificación funcional por cliente y versión; operan como solicitud y recaen en herencia nativa si no pueden aplicarse o confirmarse.
- **Host T3 (`t3.json` / `t3.local.json`)**: admite solo `version` y `local` (sin `external`). En `local` se definen `provider`, `model`, `effort` (si se fija alguno por defecto, `provider` y `model` son obligatorios juntos) y `profiles`. Los cuatro roles canónicos admiten selección única `{provider, model, effort}` o `{standard, complex}`; el rol adicional `review` admite solo selección única y reutiliza [qa-review.md](../../roles/qa-review.md).

## Precedencia, exclusividad y validación

1. **Exclusividad local en T3**: si existe `t3.local.json`, es el único archivo activo. No hay fusión ni herencia entre `t3.local.json` y `t3.json`: un rol sin perfil ni defaults en el archivo activo queda sin configurar y detiene el despacho (salvo bootstrap inicial cuando aún no existe `t3.json`).
2. **Lectura bajo demanda y validación**: el coordinador lee el archivo activo antes de cada despacho (sin caché de arranque) y lo valida con `python3 scripts/validate-core --project <proyecto> --harness-file <archivo-activo>`. Si falla, detiene el despacho.
3. **Precedencia atómica en T3**: (1) selección explícita del owner para la tarea (`provider` y `model` obligatorios, `effort` opcional); (2) perfil coincidente en `local.profiles.<rol>`; (3) defaults del mismo archivo (`local.provider`/`model`/`effort`); (4) detener el despacho. Nunca se sustituye proveedor, modelo ni se recurre a APIs o créditos de pago no autorizados.
4. **Precedencia por campo en standalone**: selección explícita del owner → valor del perfil → default local → herencia nativa (`null` u omitido pasa al siguiente nivel).

## Mapeo de `effort` y verificación `requested` / `observed`

En T3, antes de despachar se comprueba el catálogo del host (proveedor habilitado, modelo listado y `effort` soportado), traduciendo `effort` a la opción nativa: `variant` en OpenCode, `thought_level` en Antigravity y `reasoningEffort` en Codex.

- Si el proveedor o el modelo no están disponibles: detener el despacho sin sustituir.
- Si proveedor y modelo existen pero `effort` no está expuesto o soportado (autorización permanente en Antigravity Hydrogen cuando `medium` no está soportado): despachar sin la opción nativa de `effort`, mantener `provider` y `model` exactos, y registrar `effort` solicitado, observado `not exposed` y veredicto `UNVERIFIED`.

Antes del despacho se registran `provider`, `model` y `effort` solicitados (`requested`), y al finalizar se comparan con los metadatos reales de ejecución (`observed`), según [agent-work-packet.md](../../templates/agent-work-packet.md). Una identidad distinta equivale a `FAIL`; la ausencia de metadatos equivale a `UNVERIFIED`. El autoreporte del worker nunca sirve como evidencia.

## Recetas prácticas

Configuración versionada real en [.agents/harnesses/t3.json](../../.agents/harnesses/t3.json):

```json
{
  "version": 2,
  "local": {
    "provider": "antigravity",
    "model": "gemini-4-hydrogen",
    "effort": "medium",
    "profiles": {
      "qa-review": { "provider": "opencode", "model": "alibaba-token-plan/glm-5.3", "effort": "low" },
      "review": { "provider": "codex", "model": "gpt-6.1-terra", "effort": "low" }
    }
  }
}
```

Para pruebas locales sin abrir PR, crea `.agents/harnesses/t3.local.json` con los mismos campos obligatorios (`provider` y `model` en `local` o en cada perfil) y valídalo con `--harness-file`. Al borrarlo, el siguiente despacho vuelve automáticamente a `t3.json`.

## Fuentes canónicas

- [dynamic-agents.md](../../methodology/dynamic-agents.md) (secciones *Coordinator configuration*, *Native role profiles* y *Host worker configuration*)
- [t3.json](../../.agents/harnesses/t3.json)
- [agent-work-packet.md](../../templates/agent-work-packet.md)
- [dynamic-agents-external-clients.md](../../methodology/dynamic-agents-external-clients.md)
- [validate-core](../../scripts/validate-core)
