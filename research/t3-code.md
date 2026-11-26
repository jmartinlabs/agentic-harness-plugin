# Research — T3 Code

Investigación sobre T3 Code como motor de coordinación para Agentic Harness.
Sub-issue [#34](https://github.com/jmartinlabs/agentic-harness-plugin/issues/34) de
[#17](https://github.com/jmartinlabs/agentic-harness-plugin/issues/17).

| Campo | Valor |
|---|---|
| Estado | Consolidada; **pendiente de revisión externa**. No es una decisión arquitectónica aprobada |
| Fecha de observación | 2026-11-26 |
| Versiones | T3 Code 0.1.11 (Beta, macOS) · plugin 1.2.2 (1.2.1 en Claude Code y Antigravity) · Claude Code 2.1.330 · Codex CLI 0.172.0 · OpenCode 2.3.2 · Antigravity no registrada |
| Coordinador usado | Claude Sonnet 5.5 dentro de T3 |
| Cambios funcionales | Ninguno |

## 1. Conclusión

T3 completó una vez el ciclo implementación → QA → corrección → nueva QA → review con trabajadores
de tres clientes, sin intervención humana tras la autorización. La adaptación usada fue solo texto
en el mensaje de delegación.

La orientación propuesta es: **T3 ejecuta y supervisa; Agentic Harness aporta método, roles, gates y
evidencia**. Es apto para un piloto acotado. La fiabilidad no está demostrada: una ejecución por
caso, tarea pequeña y sintética, y un solo cliente observado como coordinador.

## 2. Método, evidencia y límites

| Etiqueta | Significado | Sección |
|---|---|---|
| Experimental | Ejecutado y comprobado en esta investigación | 3 |
| Inspección | Observado en disco, registros o código instalado, sin ejercitar el comportamiento | 4 |
| Documentado | Esquema de herramientas o documentación oficial, sin ejercitar | 5 |
| Hipótesis | Inferencia sin comprobar; se marca como tal donde aparece | — |

- Fases: análisis de solo lectura; compatibilidad del plugin global; pruebas autorizadas 1–3;
  propuesta de integración; análisis de cuotas; análisis de coordinador común.
- Las pruebas se hicieron sobre un repositorio sintético temporal.
- Parte del análisis previo usa observaciones de unas pocas delegaciones triviales anteriores a las
  pruebas. No se reproducen sus registros.
- Desviación: durante la primera fase, que excluía lanzar trabajadores, se usó un subagente para leer
  documentación pública (unos 61.000 tokens).
- La documentación pública procede de la rama principal de T3 y puede adelantarse a la versión
  instalada.
- Independencia respecto a #18–#21: no se consultaron para investigar ni probar. Al preparar esta
  consolidación se consultó su formato y quedaron visibles parte de las conclusiones de #20 y los
  encabezados de #21. No se ha incorporado contenido de ninguna.
- Las evidencias originales se conservan localmente, fuera del repositorio. Este documento omite
  identificadores de hilos y sesiones, rutas personales, datos de cuenta, cifras de cuota y todo
  registro de otros proyectos. Un tercero no puede reproducir las observaciones solo con él.

## 3. Capacidades verificadas experimentalmente

### 3.1 Montaje de las pruebas

| Elemento | Valor |
|---|---|
| Tarea | Módulo Python pequeño con diez criterios de aceptación |
| Defecto sembrado | El reparto de un importe asignaba todo el resto a la última parte; el encargo del implementador no lo incluía |
| Implementación | OpenCode · DeepSeek V4.1 Flash · `high` |
| QA | Codex · `gpt-6.1-terra` · `medium` |
| Review | Antigravity · `gemini-4-hydrogen` · `medium` |
| Candidatos | base `73c37c3` → `e15d25c` (rechazado) → `1e91543` (aprobado) |

Los SHA pertenecen al repositorio sintético, no a este.

### 3.2 Resultados

| Capacidad | Resultado | Evidencia y matiz |
|---|---|---|
| Delegar desde Claude a OpenCode, Codex y Antigravity | PASS | Hilos hijos creados con proveedor y modelo explícitos |
| Seleccionar esfuerzo | PASS | Confirmado en el registro de cada cliente |
| Modelo efectivo en Antigravity | PASS con matiz | El log del cliente cambia al modelo y nivel pedidos; los metadatos citan además variantes y un modelo auxiliar cuya función no se determinó |
| Verificar solo con herramientas T3 | PARCIAL | El modelo ejecutado figuró vacío en OpenCode y Antigravity; ninguna herramienta expone esfuerzo ni tokens |
| Modelo inexistente | PASS | Rechazo `model_unavailable`, sin sustitución |
| Ejecución paralela | PASS | Tres trabajadores simultáneos y, después, dos |
| Recepción automática | PASS | 9 de 9 ejecuciones reactivaron al coordinador; una llegó durante un turno en curso |
| Reutilizar trabajador | PASS en OpenCode y Antigravity | Misma sesión nativa y recuerdo exacto de datos previos |
| Rol explícito en el mensaje | PASS | Los tres se identificaron como trabajadores |
| QA independiente | PASS | Hilo propio; detectó el defecto sin que se le indicara |
| QA sobre el commit correcto | PASS | Cada QA creó un worktree separado por instrucción y comprobó HEAD |
| Corrección y revalidación | PASS | Corrección en el mismo hilo; QA nueva y review aprobadas, 17 pruebas |
| Cumplimiento de restricciones | PASS en lo registrado | Sin delegaciones, push ni escrituras fuera del repositorio sintético según la actividad registrada y el estado de Git; no es vigilancia del sistema de archivos |
| Antigravity sin ruta | Sin skills del Harness | No veía ninguna en su catálogo |
| Antigravity con ruta en el mensaje | PASS | Leyó rol, skill y reglas enlazadas de su instalación global, sin cambiar configuración |

El implementador observó por su cuenta el defecto sembrado, lo informó y no lo modificó. La QA no
recibió esa observación. La segunda QA sí conocía el defecto anterior, que era su regresión.

### 3.3 Consumo y duración

Tokens según el registro de T3; la entrada incluye la caché. No hay coste monetario fiable.

| Ejecución | Segundos | Entrada | En caché | Salida |
|---|---:|---:|---:|---:|
| Sonda OpenCode | 38 | 37.735 | 24.832 | 961 |
| Sonda Codex | 49 | 88.399 | 80.000 | 703 |
| Sonda Antigravity | 44 | 108.823 | 67.778 | 4.013 |
| Ruta Antigravity (hilo reutilizado) | 9 | 83.805 | 77.107 | 2.514 |
| Implementación OpenCode | 37 | 253.763 | 234.496 | 4.737 |
| QA-1 Codex | 34 | 136.392 | 122.624 | 1.394 |
| Corrección OpenCode (hilo reutilizado) | 14 | 160.449 | 156.160 | 2.018 |
| QA-2 Codex | 29 | 108.248 | 103.296 | 1.274 |
| Review Antigravity | 26 | 162.674 | 116.163 | 5.542 |
| **Total trabajadores** | | **1.140.288** | **982.456** | **23.156** |

- Ciclo de implementación a review: 2 min 28 s; 821.526 de entrada (88.787 sin caché).
- Coordinador: cuatro turnos intermedios del ciclo acumularon 3,54 millones de entrada, casi toda en
  caché, con un contexto previo de unos 350.000 tokens. No representa un coordinador recién abierto.
- Intervención humana: la autorización inicial; ninguna aprobación posterior.

### 3.4 Otras comprobaciones directas

- Este coordinador Claude recibió `orchestrate` completo mediante el hook de inicio, con las 13
  skills y los agentes del plugin.
- Lanzar un trabajador Codex añadió a la configuración global de Codex una entrada que marca el
  repositorio de trabajo como de confianza (autoría exacta no determinada).
- `delegate_task` rechazó dirigir un trabajador a otro proyecto local: los hijos se ejecutan en el
  proyecto del coordinador.

## 4. Observado por inspección, sin ejercitar

| Observación | Detalle |
|---|---|
| Instalaciones globales | T3 usa los clientes y configuraciones del usuario en Claude, Codex y OpenCode |
| Hermes | El perfil no predeterminado configurado en T3 no tiene las skills del plugin y tiene una `work-issue` propia homónima |
| Antigravity | T3 usa un `GEMINI_HOME` privado; enlaza skills y reglas globales, pero busca plugins en el perfil privado |
| OpenCode | El selector de agente de T3 solo ofrece agentes `primary` o `all`; los adaptadores del plugin son `subagent` |
| OpenCode, permisos | T3 añade a la sesión una regla que permite todo; podría anular las restricciones de `qa` y `review` (precedencia: hipótesis) |
| Codex | Los trabajadores corrieron sin sandbox pese a una configuración global más restrictiva |
| Trabajadores | Reciben las instrucciones de T3 y disponen de herramientas de delegación |
| Instrucciones comunes | No se encontró en los ajustes de T3 un campo de instrucciones globales ni perfil de coordinador; los campos de instrucciones vistos son de títulos, ramas, textos de Git y revisión |
| Cuotas | T3 guarda en caché local cuotas de Claude y Codex; marca OpenCode y Antigravity como no admitidos; sin datos de Hermes |
| Consumo | La base local guarda tokens por turno; la caché agregada de uso incluía Claude, Codex, Grok y Pi, no OpenCode ni Antigravity |
| Workflows | Documentados en la rama principal; ausentes en la versión instalada |

## 5. Capacidades documentadas

| Capacidad | Fuente |
|---|---|
| Subagentes delegados interactivos y subagentes nativos en solo lectura; el hijo no supera el permiso del padre; detener el padre detiene a sus delegados | [Subagents](https://github.com/pingdotgg/t3code/blob/main/docs/user/subagents.md) |
| Enviar, encolar, guiar, reiniciar, interrumpir y cancelar hilos; consultar estado | Esquemas de las herramientas de T3 |
| Modos de permiso; los restringidos piden aprobación y no equivalen a solo lectura | [Permission modes](https://github.com/pingdotgg/t3code/blob/main/docs/user/permission-modes.md) y esquemas |
| Página de uso, límites de suscripción y fuentes de cuota externas; OpenCode Go y Console bajo ciertas condiciones | [Usage](https://github.com/pingdotgg/t3code/blob/main/docs/user/usage.md) |
| Tareas programadas, webhooks, vigilancia de PR | [Project settings](https://github.com/pingdotgg/t3code/blob/main/docs/user/project-settings.md) y esquemas |
| Workflows duraderos (Labs) | [Workflows](https://github.com/pingdotgg/t3code/blob/main/docs/user/workflows.md) |
| Skills por cliente con `$`; Antigravity carga skills globales y de proyecto | [Composer](https://github.com/pingdotgg/t3code/blob/main/docs/user/composer.md) |
| `t3.json`: scripts, worktrees e iconos; no instrucciones | [Project config](https://github.com/pingdotgg/t3code/blob/main/docs/user/t3-json.md) |
| Enlaces de prompt que abren un borrador sin enviarlo, a través de un dominio web de T3 | [Prompt links](https://github.com/pingdotgg/t3code/blob/main/docs/user/prompt-links.md) |

## 6. Limitaciones y riesgos detectados

| Limitación | Riesgo | Mitigación posible |
|---|---|---|
| Un trabajador puede asumir rol de coordinador: una delegación trivial anterior, sin cabecera de rol, se presentó así | Alto | Cabecera explícita de trabajador |
| Restricciones solo por instrucción; hijos con acceso total | Alto | Verificación posterior; barrera de solo lectura fuera de T3 para riesgo alto |
| El worktree de T3 parte del commit del coordinador, no del trabajo del autor (documentado) | Alto | Fijar el SHA y comprobarlo |
| Sin delegación a otro proyecto local | Medio | Abrir el coordinador en el proyecto de la entrega |
| Verificación de modelo y esfuerzo depende de registros del cliente | Medio | Registrar «no verificado» |
| Cuotas sin herramienta ni comando: solo caché interna no documentada, parcial por cliente | Medio | Tratarlas como orientativas |
| Hermes y Antigravity no cargan el plugin en T3 de forma equivalente | Medio | Ruta en el mensaje (probado solo en Antigravity) o corregir configuración |
| La guía que inyecta T3 pide corregir uno mismo hallazgos pequeños; contradice al coordinador exclusivo | Medio | Declarar precedencia del Harness |
| `update-agentic --check` revisa el directorio principal de Hermes, no otros perfiles | Bajo | Candidato a issue |
| T3 en Beta; formatos internos y herramientas pueden cambiar | Medio | Repetir pruebas al actualizar |
| El contexto del coordinador domina el consumo | Medio | Un coordinador nuevo por entrega |
| Estado de la entrega fuera de T3: no conoce gates ni fases | Medio | Git, Project `Status` y checkpoints |
| Dependencia de un equipo encendido y de T3 en ejecución (hipótesis para delegaciones) | Medio | Probar recuperación |

## 7. Propuestas arquitectónicas

**Ninguna está aprobada ni implementada.**

### 7.1 Reparto de responsabilidades

| T3 | Agentic Harness |
|---|---|
| Sesiones, modelos, paralelismo, avisos | Cuándo y a quién delegar |
| Worktrees y permisos | Propiedad de archivos y prohibiciones |
| Registro de uso e interfaz | Evidencia PASS/FAIL/UNRUN y modelo solicitado frente a observado |
| Programación y vigilancia de PR | Gates, aprobaciones y merge humano |

Sin demonio, cola, panel ni adaptador de código propios.

### 7.2 Activación del coordinador con cualquier cliente

No se halló mecanismo nativo. Propuesta: un mensaje de arranque igual para todos, que remita a una
única instalación: el clon compartido `~/.local/share/agentic-harness-plugin`.

```text
Actúa como coordinador de Agentic Harness en esta conversación.
1. Si no tienes cargada la skill orchestrate, lee
   ~/.local/share/agentic-harness-plugin/skills/orchestrate/SKILL.md
   y resuelve sus enlaces desde ese directorio.
2. Delega con las herramientas de T3 (delegate_task); no uses subagentes
   propios, swarm ni CLI. No edites código ni corrijas hallazgos.
3. A cada trabajador indícale: ROL: TRABAJADOR, su rol, el archivo
   roles/<rol>.md de esa instalación, commit, ficheros, prohibiciones
   y formato de respuesta.
4. Las correcciones van al mismo hilo; cada nueva QA, a uno nuevo.
Antes de actuar, confirma versión leída, herramientas disponibles y rutas.
Rutas (rol: cliente, modelo, esfuerzo): …
Tarea y alcance autorizado: …
```

- Los puntos 2–4 serían provisionales hasta que exista una sección «T3 Code» en la metodología.
- La raíz única **sustituye** a una propuesta anterior de usar la raíz propia de cada cliente (que es
  la que se probó). La lectura de la raíz compartida por Codex y Antigravity está sin probar.
- Solo Claude está observado como coordinador.
- Descartado: duplicar instrucciones en los archivos globales de cada cliente.

### 7.3 Selección por rol y dificultad

- La configuración v2 no expresa qué cliente usar por rol, usa alias que no coinciden con el catálogo
  de T3 y mantiene un archivo por coordinador.
- Piloto: rutas explícitas de la persona propietaria en el mensaje o en la Issue.
- Después: un único `.agents/harnesses/t3.json` con el esquema v2 más el campo `client` en los
  perfiles, válido para cualquier coordinador. Requiere soporte en `validate-core` antes de crearlo.

```json
{
  "version": 2,
  "local": {
    "profiles": {
      "qa-review": {
        "standard": { "client": "<cliente>", "model": "<modelo>", "effort": "<nivel>" },
        "complex":  { "client": "<cliente>", "model": "<modelo>", "effort": "<nivel>" }
      }
    }
  }
}
```

| Cliente | `effort` se traduce a |
|---|---|
| Claude | `effort` |
| Codex | `reasoningEffort` |
| OpenCode | `variant` |
| Antigravity | `thought_level` |
| Hermes | `reasoning_effort`, si el modelo la ofrece |

### 7.4 Plantilla de delegación

Ampliar [la plantilla de paquete](../templates/agent-work-packet.md), sin crear otra:

```text
ROL: TRABAJADOR — <rol>. No eres el coordinador.
Paquete: <ID>
Lee primero: <instalación>/roles/<rol>.md [y la skill de la fase]
Autorización: <quién, qué y cuándo>
Repositorio, base y candidato: <…>
Aislamiento: <worktree y rama | worktree en el SHA | solo lectura>
Objetivo y criterios: <spec o Issue>
Propiedad: <ficheros | ninguno>
Prohibido: otras rutas; merge, despliegue, push o PR sin autorización; instalar;
  orchestrate, work-issue y Project Status; delegar
Reglas aplicables: <3–6, con enlace>
Verificación: <comandos>
Devuelve: COMPLETED/PARTIAL/BLOCKED; SHA; PASS/FAIL/UNRUN con evidencia;
  riesgos; modelo y esfuerzo como autodeclaración
```

### 7.5 Compatibilidad fuera de T3

La integración se aplicaría solo si existen las herramientas de T3. Archivos v2 por coordinador,
subagentes nativos y [CLI externo](../methodology/dynamic-agents-external-clients.md) no cambian.

### 7.6 Cuotas

- Consultar y registrar las cuotas disponibles antes de delegar y avisar al superar un umbral
  (punto de partida: 85 % de sesión o 90 % semanal). Dato ausente o con más de 10 minutos:
  desconocido, sin cambios por suposición.
- Cambio de ruta solo entre alternativas aprobadas de antemano; nunca créditos ni pagos adicionales.
- Recomendación para el piloto: **sin cambio automático**.
- Cualquier cambio de ruta exige consentimiento explícito: hoy
  [orchestrate](../skills/orchestrate/SKILL.md) prohíbe cambiar a una ruta con otro coste sin él.

### 7.7 Cambios futuros previstos

| Archivo | Cambio |
|---|---|
| `methodology/dynamic-agents-external-clients.md` | Sección «T3 Code» |
| `templates/agent-work-packet.md` | Cabecera de trabajador, lectura inicial y SHA |
| `methodology/dynamic-agents.md` | Referencia a la sección y a las rutas |
| `scripts/validate-core` y pruebas | Nombre `t3` y campo `client` |
| Procedencia, changelog y manifiestos | Hashes y versión |

Restricciones: `orchestrate` está a 25 bytes de su límite, así que no conviene ampliarlo; un archivo
nuevo en `methodology/` exige registro de procedencia, por eso se amplían los existentes.

## 8. Impacto potencial sobre P2–P6

No se cierran ni modifican esas Issues.

| Fase | Lo que podría aportar T3 | Evidencia | Seguiría en el Harness | Orientación propuesta |
|---|---|---|---|---|
| [P2 · #23](https://github.com/jmartinlabs/agentic-harness-plugin/issues/23) equipos y reutilización | Crear, paralelizar, reutilizar, cancelar | Tres primeras experimentales; cancelar documentado | Criterio de reutilización, un ejecutor por tarea, parada confirmada | Sustituir motor por reglas |
| [P3 · #24](https://github.com/jmartinlabs/agentic-harness-plugin/issues/24) comunicación | Mensajes entre hilos y avisos | Coordinador↔trabajador experimental; entre trabajadores sin probar | Autoridad: un mensaje no autoriza | No construir canal; relé por coordinador |
| [P4 · #25](https://github.com/jmartinlabs/agentic-harness-plugin/issues/25) modelo y esfuerzo | Selección por delegación | Experimental en tres clientes | Rutas y solicitado frente a observado | Usar selección nativa; definir rutas |
| [P5 · #26](https://github.com/jmartinlabs/agentic-harness-plugin/issues/26) jerarquía | Linaje de hilos | Sin probar | Límites de autoridad y profundidad | Aplazar; mantener sin subdelegación |
| [P6 · #27](https://github.com/jmartinlabs/agentic-harness-plugin/issues/27) supervisión visual | Panel de agentes, uso y límites | Documentado; interfaz no revisada | Rol, veredicto y SHA en el cierre | No construir; confirmar suficiencia en piloto |

Esta sustitución solo vale dentro de T3. Fuera de él, cada cliente conserva sus límites.

## 9. Decisiones aprobadas

Decisiones expresas de la persona propietaria el 2026-11-26. Ninguna aprueba la arquitectura de §7.

| # | Decisión | Alcance |
|---|---|---|
| A1 | Los resultados bastan para avanzar hacia un piloto real | Dirección; no autoriza aún el piloto |
| A2 | Revisar una propuesta antes de nuevas pruebas o modificaciones; después, piloto con una issue real | Orden de trabajo |
| A3 | Priorizar una solución declarativa que reutilice la instalación global y no duplique instrucciones | Requisito de diseño |
| A4 | Poder convertir en coordinadora una conversación con cualquier cliente y modelo compatible, con interés en Claude, Codex, OpenCode y Antigravity Hydrogen | Requisito |
| A5 | En las pruebas 1–3, la falta de sandbox no era bloqueo y las restricciones se evaluaban como instrucciones | Solo esas pruebas |
| A6 | Mantener la entrada de confianza que Codex añadió para este repositorio | Configuración local |
| A7 | Consolidar esta investigación y completarla con una revisión externa antes de continuar con el piloto | Estado actual |

## 10. Decisiones pendientes

| # | Decisión | Recomendación actual |
|---|---|---|
| D1 | Ruta que fija un cliente y no está disponible: ¿detener o heredar? | Detener, como excepción explícita a la regla v2 |
| D2 | ¿Archivo común `t3.json` o rutas en cada archivo por coordinador? | Archivo común |
| D3 | ¿Mensaje de arranque como activación, o línea automática en las instrucciones de cada proyecto? | Mensaje |
| D4 | ¿Raíz de instrucciones única o por cliente? | Única, si la prueba la confirma |
| D5 | ¿Probar coordinadores Codex, OpenCode y Antigravity antes del piloto? | Antes. Reemplaza la recomendación previa de pilotar primero con Claude |
| D6 | ¿Pilotar antes de modificar el plugin? | Sí |
| D7 | Issue del piloto | Aviso de perfiles Hermes sin skills en `update-agentic --check`; por crear |
| D8 | Política de cuotas: umbrales, alternativas y automatismo | Consultar y avisar |
| D9 | Reglas de proyecto de este repositorio, ausentes para `verify-project` | Registrar la limitación en el piloto |
| D10 | Alcance de soporte para Hermes y Antigravity | Antigravity por ruta; Hermes después |
| D11 | Comparación con #18–#21 y efecto en #23–#27 | Tras la revisión conjunta, en #17 |

## 11. Pruebas pendientes

Requieren autorización y consumen cuota.

| # | Prueba | Criterio |
|---|---|---|
| T1 | Coordinadores Codex, OpenCode y Antigravity con el mensaje de arranque | Leen la raíz común, delegan por T3, no ejecutan trabajo técnico y se reactivan |
| T2 | Piloto con una issue real y coordinador en hilo nuevo | Solo intervención en gates; QA sobre SHA correcto; consumo medido |
| T3 | Claude como trabajador; efecto del hook | Actúa como trabajador |
| T4 | Reutilización de un trabajador Codex | Conserva contexto |
| T5 | Cancelación, reinicio de T3 y suspensión del equipo | Estado correcto, sin duplicados |
| T6 | Error de cuota observado cuando ocurra, sin provocarlo | Se detiene lo afectado sin sustitución no aprobada |
| T7 | Modos con aprobación | Se conoce qué bloquea cada uno |
| T8 | Permisos de `qa` y `review` de OpenCode bajo T3 | Las denegaciones se aplican |
| T9 | Carga automática del `AGENTS.md` del proyecto de entrega, incluido Antigravity | Presente en contexto |
| T10 | Hermes con las skills disponibles; hooks de Codex | Carga confirmada |
| T11 | Escritores concurrentes y tarea de mayor tamaño | Sin interferencias |
| T12 | Ruta con cuota y frescura del dato | Dato actualizado o marcado desconocido |

## 12. Correcciones registradas durante la investigación

| Afirmación anterior | Corrección |
|---|---|
| El trabajador OpenCode no tenía agente ni constaba su carga de instrucciones | Una sesión previa recibió instrucciones de proyecto y las 13 skills, con el agente `build` |
| La falta de skills en una sesión Codex antigua era una diferencia entre proyectos | Probablemente el plugin aún no estaba instalado (hipótesis) |
| El esfuerzo efectivo quedaría sin verificar en general | Verificado en registros de OpenCode, Codex y Antigravity |
| Recomendación de pilotar primero con coordinador Claude | El requisito A4 lleva a recomendar probar antes los demás coordinadores (D5) |

## 13. Revisión externa

Pendiente. Aquí se añadirán sus conclusiones, indicando cuáles cambian propuestas, decisiones o
pruebas.
