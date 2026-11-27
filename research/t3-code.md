# Research — T3 Code

Investigación sobre T3 Code como motor de coordinación para Agentic Harness.
Sub-issue [#34](https://github.com/jmartinlabs/agentic-harness-plugin/issues/34) de
[#17](https://github.com/jmartinlabs/agentic-harness-plugin/issues/17).

| Campo | Valor |
|---|---|
| Estado | Consolidada y revisada por el propietario; **base para las validaciones desde nuevas sesiones de T3**. No aprueba aún cambios en el plugin |
| Fecha de observación | 2026-11-26 |
| Versiones | T3 Code 0.1.11 (Beta, macOS) · plugin 1.2.2 (1.2.1 en Claude Code y Antigravity) · Claude Code 2.1.330 · Codex CLI 0.172.0 · OpenCode 2.3.2 · Antigravity no registrada |
| Coordinador usado | Claude Sonnet 5.5 dentro de T3 |
| Cambios funcionales | Ninguno |

## 1. Conclusión

T3 completó una vez el ciclo implementación → QA → corrección → nueva QA → review con trabajadores
de tres clientes, sin intervención humana tras la autorización. La adaptación usada fue solo texto
en el mensaje de delegación.

La orientación propuesta es: **T3 como motor de ejecución, delegación, comunicación, paralelismo y
monitorización; Agentic Harness como fuente de metodología, instrucciones, skills, roles, permisos y
gates**. T3 sería una opción de ejecución, no una dependencia obligatoria. Es apto para un piloto acotado. La fiabilidad no está demostrada: una ejecución por
caso, tarea pequeña y sintética, y un solo cliente observado como coordinador.

Es requisito del propietario no depender de Claude como coordinador (§9); eso todavía no está probado.

## 2. Método, evidencia y límites

| Etiqueta | Significado | Sección |
|---|---|---|
| Experimental | Ejecutado y comprobado en esta investigación | 3 |
| Inspección | Observado en disco, registros o código instalado, sin ejercitar el comportamiento | 4 |
| Documentado | Esquema de herramientas o documentación oficial, sin ejercitar | 5 |
| Hipótesis | Inferencia sin comprobar; se marca como tal donde aparece | — |
| Revisión externa | Aportado por la revisión externa; no comprobado de forma independiente en esta investigación | 4.1, 7, 13 |

- Fases: análisis de solo lectura; compatibilidad del plugin global; pruebas autorizadas 1–3;
  propuesta de integración; análisis de cuotas; análisis de coordinador común; revisión arquitectónica
  externa.
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
  identificadores de hilos y sesiones, rutas personales, datos de cuenta, cifras agregadas de consumo
  personal, porcentajes de cuota y todo registro de otros proyectos. Un tercero no puede reproducir
  las observaciones solo con este documento.

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

### 4.1 Estadísticas observadas en la interfaz (revisión externa)

Según la revisión externa, la interfaz de T3 ofrece de forma centralizada: tokens por cliente, modelo,
sesión y turno; tokens de entrada y salida; lecturas desde caché; coste equivalente de API; evolución
temporal; y número de sesiones.

Interpretación y conclusiones sobre eficiencia, caché y costes:

- Las cifras agregadas de consumo de la cuenta personal se omiten del documento público; **no equivalen
  al consumo exclusivo de las pruebas** de esta investigación (las métricas de las pruebas se conservan
  en §3.3).
- El coste equivalente de API no es el coste real de las suscripciones.
- Un coste ausente para DeepSeek **no significa consumo gratuito**.
- Las diferencias de coste equivalente observado entre modelos (por ejemplo, Hydrogen frente a Neon y
  Sonnet en tareas y proporciones de caché distintas) **no constituyen un benchmark comparable**.

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
| Restricciones solo por instrucción; hijos con acceso total (aceptado por el propietario, R5) | Alto | Comprobar cumplimiento y registrar incumplimientos; sin mecanismos adicionales de aislamiento |
| El worktree de T3 parte del commit del coordinador, no del trabajo del autor (documentado) | Alto | Fijar el SHA y comprobarlo |
| Sin delegación a otro proyecto local | Medio | Abrir el coordinador en el proyecto de la entrega |
| Verificación de modelo y esfuerzo depende de registros del cliente | Medio | Registrar «no verificado» |
| Cuotas: sin herramienta nativa de coordinación. Claude y Codex, accesibles por archivos internos; OpenCode, tokens sí y cuota no para la ruta usada; Antigravity, tokens sí y cuota todavía no; Hermes, cobertura incompleta | Medio | Consultar y registrar lo disponible; no desarrollar lectores ni adaptadores en el piloto |
| Formatos internos de T3 que pueden cambiar entre versiones; producto en Beta | Medio | Repetir pruebas al actualizar; no depender de ellos |
| Hermes y Antigravity no cargan el plugin en T3 de forma equivalente | Medio | Ruta en el mensaje (probado solo en Antigravity); no asumir carga automática de `orchestrate` |
| La guía que inyecta T3 pide corregir uno mismo hallazgos pequeños; contradice al coordinador exclusivo | Medio | Declarar precedencia del Harness |
| `update-agentic --check` revisa el directorio principal de Hermes, no otros perfiles | Bajo | Candidato a issue, sin autorizar |
| El contexto del coordinador domina el consumo | Medio | Medidas de §7.8; comprobar su efecto antes de imponerlas |
| Estado de la entrega fuera de T3: no conoce gates ni fases | Medio | Git, Project `Status` y checkpoints |
| Dependencia de un equipo encendido y de T3 en ejecución (hipótesis para delegaciones) | Medio | Probar recuperación |

## 7. Propuestas arquitectónicas

**Ninguna está implementada. Salvo lo recogido como requisito en §9, todas están pendientes de
aprobación.**

### 7.1 Arquitectura objetivo y responsabilidades

| T3 | Agentic Harness |
|---|---|
| Ejecución, delegación, paralelismo | Metodología, instrucciones y skills |
| Comunicación entre sesiones | Roles, permisos y reglas de delegación |
| Worktrees y modos de permiso | Propiedad de archivos y prohibiciones |
| Monitorización y consumo | Evidencia PASS/FAIL/UNRUN y modelo solicitado frente a observado |
| Programación y vigilancia de PR | Gates, aprobaciones y merge humano |

- T3 es una opción de ejecución; el plugin no pasa a depender de él.
- No desarrollar runtime, MCP, sistema de comunicación ni interfaz de monitorización propios cuando T3
  cubra la necesidad. Tampoco demonio, cola ni adaptador de código.
- Mantener la compatibilidad con los clientes usados fuera de T3.

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

- La activación con un mensaje manual corto es aceptable para el propietario; las instrucciones completas
  permanecen en Agentic Harness, sin duplicarlas (R3, R4).
- Los puntos 2–4 serían provisionales hasta que exista una sección «T3 Code» en la metodología.
- La raíz única **sustituye** a una propuesta anterior de usar la raíz propia de cada cliente (que es
  la que se probó). La lectura de la raíz compartida por Codex y Antigravity está sin probar.
- Solo Claude está observado como coordinador.
- Descartado: duplicar instrucciones en los archivos globales de cada cliente.

Activación y mantenimiento del plugin:

- Reutilizar la instalación global y mantener `update-agentic` como actualización; sin segunda
  instalación para T3.
- Priorizar la instalación compartida y **comprobar que todos los clientes pueden leerla**. Antigravity
  ya accedió a roles y skills mediante ruta explícita, desde su propia instalación.
- No asumir que todos los clientes cargan `orchestrate` automáticamente.
- No modificar hooks hasta demostrar que hace falta.
- No usar `T3CODE_THREAD_ID` para identificar trabajadores sin verificar que distingue ambos tipos de
  sesión; solo se observó en una sesión coordinadora.
- Evitar instrucciones generales en `AGENTS.md` que conviertan a todos los trabajadores en coordinadores.
- Tener presente el margen mínimo de tamaño de `orchestrate`.

### 7.3 Selección por rol y dificultad

- La configuración v2 no expresa qué cliente usar por rol, usa alias que no coinciden con el catálogo
  de T3 y mantiene un archivo por coordinador.
- Piloto: rutas explícitas de la persona propietaria en el mensaje o en la Issue.
- Propuesta: un único `.agents/harnesses/t3.json` por proyecto, independiente del coordinador,
  reutilizando el esquema v2 tanto como sea posible. **Es distinto del `t3.json` nativo de T3**, que está
  en la raíz del repositorio y no configura modelos.
- Seleccionaría cliente, proveedor, modelo y esfuerzo por rol y dificultad.
- Admitiría alternativas expresamente preautorizadas, en orden. Sin sustituciones silenciosas, sin
  contratar APIs ni activar pagos adicionales.
- La necesidad real de cambios en el validador se evaluará después del piloto. Hecho comprobado en el
  código: el validador actual rechazaría ese nombre de archivo y los campos nuevos, así que no debe
  crearse en un proyecto sin ese soporte.

Forma ilustrativa; los nombres de `provider` y `alternatives` están por definir:

```json
{
  "version": 2,
  "local": {
    "profiles": {
      "qa-review": {
        "standard": {
          "client": "<cliente>", "provider": "<proveedor>", "model": "<modelo>", "effort": "<nivel>",
          "alternatives": [ { "client": "<cliente>", "provider": "<proveedor>", "model": "<modelo>", "effort": "<nivel>" } ]
        },
        "complex": { "client": "<cliente>", "provider": "<proveedor>", "model": "<modelo>", "effort": "<nivel>" }
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

Política procedente de la coordinación previa con Codex, mantenida aquí como propuesta pendiente de
incorporar al plugin:

| Cuota restante | Comportamiento |
|---|---|
| Más del 25 % | Funcionamiento normal |
| 25 % o menos | No asignar nuevas tareas al proveedor |
| 5 % o menos | Cierre seguro y handoff |
| Desconocida | Mantener la ruta configurada y gestionar los errores que aparezcan |

- Se aplica el límite más restrictivo entre sesión y semana.
- Las alternativas expresamente preautorizadas pueden usarse sin pedir permiso adicional.
- Nunca usar automáticamente créditos de reinicio, activar pagos adicionales ni contratar APIs.
- En el piloto: consultar y registrar lo disponible, sin desarrollar lectores ni adaptadores.

Contraste con el repositorio: **estos umbrales no están incorporados todavía** en las skills,
metodología, roles, plantillas ni scripts del plugin 1.2.2; el propietario confirmó que proceden de la
política anterior de coordinación con Codex y se mantienen como propuesta pendiente de incorporar (D8).
[orchestrate](../skills/orchestrate/SKILL.md) exige respetar los límites reales, detener lo afectado y no
cambiar a una ruta con otro coste sin consentimiento explícito; una preautorización expresa sería
compatible con esto.

Sustituye la propuesta anterior de umbrales sobre porcentaje usado (85 % y 90 %) sin cambio automático.

### 7.7 Cambios futuros previstos

| Archivo | Cambio |
|---|---|
| `methodology/dynamic-agents-external-clients.md` | Sección «T3 Code» |
| `templates/agent-work-packet.md` | Cabecera de trabajador, lectura inicial y SHA |
| `methodology/dynamic-agents.md` | Referencia a la sección y a las rutas |
| `scripts/validate-core` y pruebas | Soporte del archivo `t3` y sus campos; necesidad a evaluar tras el piloto |
| Procedencia, changelog y manifiestos | Hashes y versión |

Restricciones: `orchestrate` está a 25 bytes de su límite, así que no conviene ampliarlo; un archivo
nuevo en `methodology/` exige registro de procedencia, por eso se amplían los existentes.

### 7.8 Consumo y eficiencia

La eficiencia del coordinador importa tanto como la de los trabajadores: en el ciclo medido, cuatro
turnos intermedios del coordinador sumaron unos 3,5 millones de tokens de entrada, principalmente en
caché, frente a unos 822.000 de los trabajadores del ciclo (89.000 sin caché) y 15.000 de salida.

A evaluar:

- Mensajes de delegación compactos.
- Carga de skills bajo demanda.
- No incorporar investigaciones completas al contexto operativo.
- Reutilizar trabajadores cuando aporte valor.
- Handoff y sesiones nuevas tras hitos relevantes.
- Diferenciar tokens procesados, tokens nuevos, caché y coste efectivo.
- Modelos económicos para coordinación y QA cuando su calidad baste.

**No imponer una sesión nueva por entrega sin comprobar que mejora la eficiencia.** Esto sustituye la
recomendación anterior de abrir siempre un coordinador nuevo.

### 7.9 Seguimiento centralizado del consumo

Evaluar si las estadísticas de T3 sustituyen total o parcialmente el seguimiento propio del plugin. No
desarrollar otra recopilación si las capacidades existentes bastan.

| Criterio | Lo observado hasta ahora | Estado |
|---|---|---|
| Cobertura por proveedor | Tokens por turno en Claude, Codex, OpenCode y Antigravity; incompletos en Hermes; la revisión externa vio coste de Antigravity en la interfaz | Por comprobar |
| Sesiones fuera de T3 | La documentación indica que agrega historiales de varios clientes | Por comprobar |
| Persistencia histórica | Documentados 92 días por defecto, configurables | Documentado |
| Exportación | No se investigó | Pendiente |
| Acceso programático | Sin herramienta ni comando de coordinación; base y caché internas | Limitado |
| Fiabilidad | No evaluada | Pendiente |
| Dependencia de formatos internos | Toda lectura hecha aquí dependió de ellos | Riesgo |

### 7.10 Roles y restricciones

El propietario acepta restricciones establecidas por las instrucciones del coordinador. La falta de
sandbox o de bloqueo de escritura no es bloqueante y no se desarrollarán mecanismos de aislamiento.

Sí debe comprobarse el cumplimiento efectivo. Los incumplimientos se registran y su tratamiento se
decide después.

| Comprobación | En las pruebas 1–3 |
|---|---|
| Rol asignado | Cumplido |
| Alcance autorizado | Cumplido en lo registrado |
| Prohibiciones | Cumplidas en lo registrado |
| Independencia de QA | Cumplida; la segunda QA conocía el defecto previo |
| Commit candidato exacto | Cumplido |
| Corrección por el ejecutor original | Cumplida |
| Coordinador sin trabajo técnico | Cumplido en el ciclo, salvo preparar el repositorio sintético y verificar evidencias. Antes del ciclo, el coordinador investigó directamente por la restricción de no lanzar trabajadores |

## 8. Impacto potencial sobre P2–P6

No se cierran, cancelan ni modifican esas Issues hasta concluir la evaluación. P1 se mantiene: el
coordinador solo coordina.

| Fase | Lo que podría aportar T3 | Evidencia | Seguiría en el Harness | Orientación propuesta |
|---|---|---|---|---|
| [P2 · #23](https://github.com/jmartinlabs/agentic-harness-plugin/issues/23) equipos y reutilización | Crear, paralelizar, reutilizar, cancelar | Tres primeras experimentales; cancelar documentado | Criterio de reutilización, un ejecutor por tarea, parada confirmada | Simplificar con reglas y capacidades nativas |
| [P3 · #24](https://github.com/jmartinlabs/agentic-harness-plugin/issues/24) comunicación | Mensajes entre hilos y avisos | Coordinador↔trabajador experimental; directa entre trabajadores no acreditada | Autoridad: un mensaje no autoriza | Usar T3; coordinador como relé |
| [P4 · #25](https://github.com/jmartinlabs/agentic-harness-plugin/issues/25) modelo y esfuerzo | Selección por delegación | Experimental en tres clientes | Rutas y solicitado frente a observado | Mantener selección declarativa de cliente, modelo y esfuerzo |
| [P5 · #26](https://github.com/jmartinlabs/agentic-harness-plugin/issues/26) jerarquía | Linaje de hilos | Sin probar | Límites de autoridad y profundidad | Aplazar hasta demostrar necesidad |
| [P6 · #27](https://github.com/jmartinlabs/agentic-harness-plugin/issues/27) supervisión visual | Interfaz, agentes, uso y consumo | Documentado; consumo observado por la revisión externa | Rol, veredicto y SHA en el cierre | Aprovechar la interfaz de T3 |

Esta sustitución solo vale dentro de T3. Fuera de él, cada cliente conserva sus límites.

## 9. Requisitos y decisiones del propietario

Expresados el 2026-11-26. El propietario dio su conformidad al documento consolidado como base para
las validaciones siguientes; no autorizan todavía modificaciones en el plugin ni pruebas desde esta
sesión.

### 9.1 Requisitos expresos

| # | Requisito |
|---|---|
| R1 | Poder seleccionar cualquier cliente y modelo compatible como coordinador dentro de T3; interés en Antigravity Hydrogen, OpenCode DeepSeek, Codex y Claude Code |
| R2 | No depender de Claude como coordinador |
| R3 | La activación mediante un mensaje manual corto es aceptable |
| R4 | Las instrucciones completas permanecen en Agentic Harness, sin duplicarlas; solución declarativa que reutilice la instalación global |
| R5 | Se aceptan restricciones por instrucciones; la falta de sandbox o de bloqueo de escritura no es criterio bloqueante en esta evaluación (antes limitado a las pruebas 1–3) |
| R6 | Mantener la compatibilidad con los clientes actuales y no contratar APIs externas |

### 9.2 Decisiones de proceso

| # | Decisión |
|---|---|
| A1 | Los resultados bastan para avanzar hacia las validaciones en nuevas sesiones de T3 |
| A2 | Conformidad del propietario con el documento consolidado; las siguientes pruebas las ejecutará en nuevas sesiones de T3, empezando por Antigravity con Hydrogen como coordinador, incorporando sus resultados a esta misma investigación |
| A3 | Mantener la entrada de confianza que Codex añadió para este repositorio |
| A4 | Mantener abierta la issue #34 y la PR #35 en borrador; no iniciar más pruebas ni implementaciones desde esta sesión |
| A5 | Omitir las cifras agregadas de consumo personal del documento público, conservando métricas de pruebas y conclusiones |
| A6 | Mantener los umbrales de cuota del 25 % y 5 % (procedentes de la política previa con Codex) como propuesta pendiente de incorporar al plugin |

## 10. Decisiones pendientes

| # | Decisión | Recomendación actual |
|---|---|---|
| D1 | Ruta no disponible sin alternativa preautorizada: ¿detener o heredar? | Detener; sin sustituciones silenciosas |
| D2 | Archivo `.agents/harnesses/t3.json` y su esquema (proveedor, alternativas) | Archivo único basado en v2 |
| D3 | Texto definitivo del mensaje de arranque | El de §7.2, compacto |
| D4 | Raíz de instrucciones compartida | Priorizarla y comprobar que todos la leen |
| D5 | Orden de validación | El de §11 |
| D6 | Momento de modificar el plugin | Después de validar y pilotar |
| D7 | Issue del piloto | Ejecutada en #36 / PR #37 (aviso de perfiles Hermes sin skills en `update-agentic --check`, §14) |
| D8 | Política de cuotas de §7.6 (25 % y 5 %) | Mantenerla como propuesta pendiente de incorporar al plugin (origen: política previa con Codex) |
| D9 | Reglas de proyecto de este repositorio, ausentes para `verify-project` | Registrar la limitación en el piloto |
| D10 | Alcance de soporte para Hermes y Antigravity | Antigravity por ruta; Hermes después |
| D11 | Sustituir total o parcialmente el seguimiento propio de uso | Decidir tras comprobar §7.9 |
| D12 | Política de sesiones del coordinador | Medir antes de imponer sesiones nuevas |
| D13 | Cambios mínimos que necesita Agentic Harness | Tras las validaciones |
| D14 | Comparación con #18–#21 y efecto en #23–#27 | Tras la revisión conjunta, en #17 |

## 11. Validaciones y pruebas pendientes

No deben iniciarse desde esta sesión. El propietario las ejecutará desde nuevas sesiones de T3, empezando
por la validación 1 (Antigravity con Hydrogen como coordinador), e incorporará los resultados a esta
misma investigación. La prueba real debe hacerse desde una sesión abierta en el proyecto
correspondiente.

### 11.1 Prioridad propuesta

| Orden | Validación | Criterio |
|---|---|---|
| 1 | Coordinador Antigravity Hydrogen | Lee la instalación compartida, delega por T3, no ejecuta trabajo técnico y se reactiva |
| 2 | Coordinador OpenCode DeepSeek | Igual |
| 3 | Coordinador Codex | Igual |
| 4 | Piloto con una issue real de bajo riesgo (**completada**, §14) | Intervención solo en gates; QA sobre el SHA correcto; restricciones comprobadas; consumo y cuotas registrados |
| 5 | Configuración declarativa definitiva | Esquema y necesidad de cambios en el validador |
| 6 | Recuperación tras interrupciones y agotamiento de cuota | Estado correcto, sin duplicados ni sustituciones no autorizadas; sin provocar el agotamiento |
| 7 | Cambios mínimos de Agentic Harness | Decisión, no prueba |

### 11.2 Otras pendientes

| Prueba | Criterio |
|---|---|
| Claude como trabajador y efecto del hook | Actúa como trabajador |
| Reutilización de un trabajador Codex | Conserva contexto |
| Modos con aprobación | Se conoce qué bloquea cada uno |
| Permisos de `qa` y `review` de OpenCode bajo T3 | Se conoce si las denegaciones se aplican |
| Carga del `AGENTS.md` del proyecto, incluido Antigravity | Presente en contexto |
| Hermes con las skills disponibles; hooks de Codex | Carga confirmada |
| Escritores concurrentes y tarea de mayor tamaño | Sin interferencias |
| Seguimiento de consumo (§7.9) | Criterios respondidos |
| Efecto de las medidas de eficiencia (§7.8) | Comparación con consumo medido |

## 12. Correcciones registradas durante la investigación

| Afirmación anterior | Corrección |
|---|---|
| El trabajador OpenCode no tenía agente ni constaba su carga de instrucciones | Una sesión previa recibió instrucciones de proyecto y las 13 skills, con el agente `build` |
| La falta de skills en una sesión Codex antigua era una diferencia entre proyectos | Probablemente el plugin aún no estaba instalado (hipótesis) |
| El esfuerzo efectivo quedaría sin verificar en general | Verificado en registros de OpenCode, Codex y Antigravity |
| Recomendación de pilotar primero con coordinador Claude | R1 y R2: validar antes los demás coordinadores (§11) |
| La caché agregada sin OpenCode ni Antigravity sugería falta de cobertura | La revisión externa vio coste de Antigravity en la interfaz; la caché inspeccionada no basta para deducir la cobertura |

## 13. Revisión externa

Incorporada el 2026-11-26. Procede de la revisión arquitectónica aportada por el propietario. No se han
hecho pruebas nuevas para verificarla.

| Tema de la revisión | Dónde está | Efecto sobre lo anterior |
|---|---|---|
| Arquitectura objetivo | §1, §7.1 | T3 queda como opción, no dependencia |
| Coordinador intercambiable | §7.2, R1–R4 | No depender de Claude; mensaje manual aceptable |
| Configuración de modelos | §7.3, D2 | Añade proveedor y alternativas; el validador se evalúa tras el piloto |
| Consumo y eficiencia | §4.1, §7.8, D12 | Retira la obligación de un coordinador nuevo por entrega |
| Seguimiento centralizado | §7.9, D11 | Línea de evaluación nueva |
| Cuotas | §6, §7.6, D8 | Sustituye umbrales y automatismo; origen confirmado en la política previa con Codex, pendiente de incorporar al plugin |
| Roles y restricciones | §7.10, R5 | Retira mitigaciones que añadían barreras técnicas |
| Activación y mantenimiento | §7.2 | Añade cautelas sobre hooks, identificación y `AGENTS.md` |
| Roadmap | §8 | Incluye P1; P2–P6 siguen abiertas |
| Validaciones | §11 | Orden: Antigravity, OpenCode, Codex, piloto, configuración, recuperación, cambios |
| Estado de decisiones | §9, §10 | Separa requisitos expresos de recomendaciones |

Criterio de clasificación: en §9.1 solo figura lo que el propietario formuló como requisito, aceptación o
restricción propia. El resto de la revisión se recoge como propuesta pendiente, aunque esté redactado en
imperativo.

## 14. Piloto práctico inicial (2026-11-26)

### 14.1 Alcance y entrega

| Elemento | Valor |
|---|---|
| Issue y PR | #36 · PR #37 (base `main`, HEAD aprobado `cdda36c`, merge `60d4a46`) |
| Issue de seguimiento | #38 (symlink cíclico en `${HERMES_HOME}/skills`, sin implementar) |
| Comportamiento entregado | `update-agentic --check` detecta perfiles de Hermes bajo `${HERMES_HOME}/profiles/*/` sin symlinks a `<shared>/skills` |
| Alcance y modo | *Advisory* y de solo lectura (sin escritura ni reparación). Archivos o subdirectorios internos no cuentan; `skills/` enlazado exactamente al compartido se considera cubierto |

### 14.2 Rutas solicitadas y observadas

| Rol | Ruta solicitada | Sesiones / turnos | Identidad observada |
|---|---|---|---|
| Implementación | `antigravity/gemini-4-hydrogen/thought_level=medium` | 1 sesión, 5 turnos | `executedModel=null` (no verificable por T3) |
| QA | `opencode/alibaba-token-plan/deepseek-v4.1-flash-1017/variant=low` | 6 sesiones nuevas | `executedModel=null` (no verificable por T3) |
| Review | `codex/gpt-6.1-terra/reasoningEffort=low` | 5 sesiones nuevas | `executedModel=null` (no verificable por T3) |

### 14.3 Verificación y evidencia de pruebas

- **Rondas**: 5 rondas de validación y 4 de corrección.
- **Hallazgos**: 5 defectos funcionales y 2 carencias documentales detectados (fallback de checkout, perfiles ocultos, límite de un enlace, `RuntimeError` con symlink cíclico, caso A de archivo o subdirectorio interno, caso B de `skills/` enlazado, y borde de `skills/` apuntando a otro checkout con enlace interno).
- **Criterio de veredicto**: QA dio `APTO` en rondas donde review u owner hallaron defectos.
- **Pruebas locales**: 105 tests `unittest` OK (1 *skip* preexistente), `validate-core` OK, `work-issue` 208, `agent-relay` 26, `delegation-route` 26, `agent-usage` 9, `auto-agent-usage` 8.
- **CI**: `pilot` (3.10/3.12), `claude-validate` y `required` en verde.

### 14.4 Consumo y duración

Consumo según telemetría local real (tokens):

| Rol / ámbito | Sesiones | Entrada nueva | Caché | Salida |
|---|---:|---:|---:|---:|
| QA + verificación | 6 | 270.231 | 4.388.992 | 53.958 |
| Review | 5 | 102.352 | 700.800 | 7.417 |
| Coordinador | — | 185.432 | 13.048.576 | 36.981 |

Antigravity no expone uso legible.

Duración registrada:

| Fase / rol | Duración |
|---|---|
| Implementación | 255 s (fase 1) + 141 s (correcciones de review del owner) |
| QA | 416 s + 315 s |
| Review | 134 s + 89 s |

### 14.5 Intervenciones humanas

- 1 gate de fase (mover #36 a `Ready Development`).
- Autorización, «Ready» y revisión con dos casos.
- Aprobación de merge separada.

### 14.6 Conclusiones, limitaciones y decisión

**Conclusiones:**

- Autonomía del coordinador sin trabajo técnico.
- El contexto del coordinador domina el consumo.
- Reutilizar al implementador para correcciones acotadas.
- QA y review siempre en sesión nueva.
- Modelos distintos aportan modos de fallo distintos y no sustituyen la revisión humana.

**Limitaciones:**

- **T3**: sin `executedModel` ni telemetría de tokens nativa; el worktree parte del commit padre; sin historial del padre; gate del Project humano.
- **Agentic Harness**: falta `.agents/tracker.local.yaml` y `AGENTS.md` en este repositorio; defecto preexistente en `${HERMES_HOME}/skills` registrado en #38.

**Decisión:**

- Evaluación práctica inicial de T3 finalizada satisfactoriamente; sin release ni cambios de integración con T3; validación de eficiencia del harness simplificado primero en sesión nueva y después diseño definitivo en [#42](https://github.com/jmartinlabs/agentic-harness-plugin/issues/42) (§15).

## 15. Decisiones P0 y estado del backlog (2026-11-27)

- **Prioridad P0**: la eficiencia del harness ([#39](https://github.com/jmartinlabs/agentic-harness-plugin/issues/39)) prevalece sobre la integración con T3. El workflow nativo quedó fusionado en [PR #41](https://github.com/jmartinlabs/agentic-harness-plugin/pull/41) (`d7dbc63`): estados, tipos, sub-issues y dependencias nativas; retirada de `work-issue`, Project y recibos; y *handoff* selectivo.
- **Integración T3 diferida**: queda pospuesta hasta validar la eficiencia del harness simplificado en sesión nueva. La issue única [#42](https://github.com/jmartinlabs/agentic-harness-plugin/issues/42) absorbe #23 y #25 con `.agents/harnesses/t3.json` propio y Agentic Harness como primer consumidor, sin excepciones ni modelos globales; sin implementación por ahora.
- **GLM 5.3 como QA**: evaluación trasladada a [#39](https://github.com/jmartinlabs/agentic-harness-plugin/issues/39).
- **Estado del backlog**:
  - **Absorbidas en [#42](https://github.com/jmartinlabs/agentic-harness-plugin/issues/42)**: #23 y #25.
  - **`Not planned`**: #18, #24, #26 y #27.
  - **`Done`**: #19–#21.
  - **Se cierran al integrar esta PR**: #34 y #17.
  - **Candidato**: #38.
