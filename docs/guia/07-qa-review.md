# Parte VII — QA y review

Explica cómo verificar de forma independiente cualquier candidato antes de integrarlo, qué distingue a la QA ejecutable de una revisión técnica interna o externa y cómo gestionar rechazos y reanudaciones. Acude a este capítulo al cerrar una implementación o al revisar hallazgos antes de solicitar aprobación de merge.

## Principio de independencia

Quien implementa un cambio nunca aprueba su propia entrega. La verificación recae en el rol `qa-review` ([qa-review.md](../../roles/qa-review.md)) o en un ejecutor y contexto independientes ([dynamic-agents.md](../../methodology/dynamic-agents.md), sección *Critical technical review*). La independencia no exige un modelo distinto, aunque debe preferirse la ruta configurada cuando exista.

Un `PASS` declarado por el autor, un manifiesto autogenerado o el resultado verde de la puerta rápida de CI no sustituyen a la QA independiente ([ci-policy.md](../../methodology/ci-policy.md), sección *Evidence validity and independent QA*). Tampoco un silencio del revisor equivale a aprobación.

## Actividades y validez de la evidencia

El especialista de QA mantiene cuatro actividades diferenciadas en su informe para no mezclar lo observado con lo ejecutado:

1. **Auditoría documental y de código:** conformidad con la especificación y criterios de aceptación, rutas negativas o de error, regresiones y límites financieros, de seguridad o persistencia.
2. **Revisión de commits y PR:** comprobación del candidato exacto (`SHA`), alcance del diff, historial y publicación.
3. **Revisión de evidencia CI:** resultados de CI existentes que QA consulta (sin presentarlos como pruebas ejecutadas por QA).
4. **QA ejecutable:** pruebas o sondas realmente lanzadas en un entorno autorizado sobre el candidato limpio.

Para que la evidencia sea válida debe registrar el commit exacto (`SHA`), la base actual, cualquier cambio sucio o sin rastrear, el comando ejecutado, versiones de herramientas, plataforma y salida real. Si cambian el candidato, la base, las dependencias o el entorno, QA reevalúa el impacto y repite las comprobaciones afectadas. Si QA trabaja en solo lectura y necesita comandos o ediciones protegidas, devuelve los hallazgos y la operación bloqueada al coordinador para que la ejecute un actor autorizado.

## Review interno y review externo

Además de QA, el coordinador puede solicitar una revisión técnica crítica:

- **Review interno:** dentro del mismo cliente, mediante un subagente o contexto separado, para inspeccionar riesgos antes o después de QA.
- **Review externo:** ejecutado por CLI en otro cliente bajo [dynamic-agents-external-clients.md](../../methodology/dynamic-agents-external-clients.md), por ejemplo `codex review` / `codex exec` en `read-only` u `opencode run --agent review`.

Existe una única autorización permanente (*standing authorization*): un coordinador en **Claude Code** puede lanzar **Codex CLI** como revisor externo de solo lectura sin pedir permiso cada vez cuando exista riesgo de seguridad, persistencia, finanzas o integridad de datos (o petición explícita del usuario), siempre que `external.codex.tasks.review` sea `automatic` en `.agents/harnesses/claude.json`. Cualquier otra dirección o tipo de tarea externa requiere petición explícita del dueño. Antes de aceptar un review externo hay que verificar que `HEAD` coincide con el candidato y que el modelo observado corresponde al configurado; sus hallazgos (`VERIFIED`, `NOT VERIFIED`, `UNRUN`) son evidencia adicional, nunca un sustituto de QA ni una autorización de merge.

## Ejecución fuera del host (contenedores)

Cuando la suite decisiva no puede ejecutarse en el host local por dependencias nativas o diferencias de plataforma ([ci-policy.md](../../methodology/ci-policy.md), sección *Executing the decisive suite off-host*), se ejecuta en un contenedor con arquitectura nativa de destino, sobre una copia limpia del checkout sin puertos publicados y provisionada con las versiones fijadas en CI.

Conviene evitar errores habituales documentados en esa política: empaquetar sin metadatos de macOS (`COPYFILE_DISABLE=1`), añadir `safe.directory` si cambia el UID en el contenedor, capturar el código de salida de cada paso por separado (sin encadenar con `&&`), auditar todos los binarios lanzados por los *fixtures*, instalar el navegador y sus librerías de sistema en pasos separados y reejecutar un fallo aislado antes de calificarlo como *flake* por contención.

## Rechazo, correcciones y reanudación

Si QA o el revisor rechazan el candidato:

1. El coordinador devuelve al trabajador de implementación únicamente los hallazgos verificados y los criterios de aceptación pendientes, referenciando el *work packet* original.
2. Se reutiliza al mismo trabajador mientras su contexto sea útil; si hay cambio de dueño, se exige confirmación de parada y *checkpoint* previo.
3. Si tras dos intentos comparables no aparece nueva evidencia, se detiene la depuración, se guarda *checkpoint* y se pide al usuario una nueva hipótesis o una decisión de alcance ([SKILL.md](../../skills/orchestrate/SKILL.md), sección *Efficiency and communication*).
4. Cada corrección produce un nuevo candidato (`SHA`), invalida la evidencia previa afectada y requiere nueva verificación antes de pedir aprobación explícita de merge ([approvals.md](../../methodology/approvals.md)).

## Fuentes canónicas

- [Rol QA / Review](../../roles/qa-review.md)
- [Política de CI y validez de evidencia](../../methodology/ci-policy.md)
- [Gestión dinámica de agentes](../../methodology/dynamic-agents.md)
- [Delegación en clientes externos](../../methodology/dynamic-agents-external-clients.md)
- [Aprobaciones y puertas protegidas](../../methodology/approvals.md)
- [Orquestación principal](../../skills/orchestrate/SKILL.md)
