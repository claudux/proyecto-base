# ADR-001: Elección del modelo de IA para la miniaplicación Gemini

**Fecha de documentación:** 20 de octubre de 2026  
**Estado:** Aceptada provisionalmente para el prototipo  
**Ámbito:** Módulo Python de consulta a Gemini mediante API REST  
**Decisión:** Utilizar `gemini-3.5-flash-lite` como modelo predeterminado.

## 1. Modelo elegido

Se selecciona **Gemini 3.5 Flash-Lite** (`gemini-3.5-flash-lite`) como modelo predeterminado de la miniaplicación.

La aplicación envía una pregunta a la API de Gemini, extrae el texto generado, consulta los metadatos de tokens y estima el costo de la petición. Para comparar los candidatos se utilizó una tarea matemática sencilla:

> Calcula el doble de (4 * 5). Responde únicamente con el resultado numérico.

**Resultado esperado:** `40`.

La elección corresponde al alcance actual del prototipo y podrá revisarse si la aplicación requiere respuestas más complejas o un tiempo de respuesta menor.

## 2. Diagrama de arquitectura

[Ver el diagrama de arquitectura del Bloque 8](./diagrama_arquitectura.png).

El diagrama documenta el flujo principal:

1. `armar_peticion(pregunta, system_instruction=None, response_schema=None)` valida la entrada, obtiene `GEMINI_API_KEY` y `GEMINI_MODEL` desde el entorno (cargados mediante `.env`) y genera `url`, `body` y `api_key`. Si recibe una instrucción o un esquema, los añade a `systemInstruction` y `generationConfig` respectivamente.
2. `enviar_peticion(url, body, api_key)` usa la credencial en la cabecera `x-goog-api-key`, envía la solicitud HTTP y devuelve el JSON procesado.
3. `extraer_texto(datos)` recupera el texto de `candidates[0].content.parts[0].text`.
4. `extraer_uso_de_tokens(datos)` lee `usageMetadata` y devuelve los conteos de entrada, salida, razonamiento y total.
5. `calcular_costo(datos, precio_entrada, precio_salida)` obtiene los conteos de tokens nuevamente y estima el costo de entrada más salida y razonamiento.
6. `parsear_respuesta_json(texto, esquema)` interpreta el texto y delega a `validar_estructura` la comprobación de claves, tipos y valores permitidos. El banco y su prueba de consistencia viven en `prompts/`.

Los errores de red, HTTP, JSON y datos inválidos se transforman en excepciones comprensibles mediante validaciones y bloques `try/except`. La credencial **no debe incluirse en el repositorio**: el archivo `.env` debe permanecer ignorado por Git.

## 3. Comparación de candidatos

### Tarifas de referencia

Tarifas **estándar de pago** publicadas por Google, expresadas en USD. Consulta: **20 de octubre de 2026**.

| Criterio | Gemini 3.5 Flash-Lite | Gemini 3.6 Flash |
|---|---:|---:|
| Identificador del modelo | `gemini-3.5-flash-lite` | `gemini-3.6-flash` |
| Entrada por 1.000 tokens | USD 0,00030 | USD 0,00075 |
| Salida por 1.000 tokens, incluido razonamiento | USD 0,00250 | USD 0,00375 |
| Entrada por 1 millón de tokens | USD 0,30 | USD 0,75 |
| Salida por 1 millón de tokens, incluido razonamiento | USD 2,50 | USD 3,75 |

**Fuente oficial:** [Google AI for Developers – Gemini Developer API pricing](https://ai.google.dev/gemini-api/docs/pricing?hl=es). Las tarifas indicadas para Gemini 3.6 Flash se anuncian hasta el **31 de diciembre de 2026**; deben verificarse nuevamente para períodos posteriores.

### Mediciones de la miniaplicación

Misma pregunta de prueba en ambos modelos; cuatro intentos por candidato. La latencia se mide con `time.perf_counter()` alrededor de `enviar_peticion` y, por tanto, representa el tiempo de la solicitud hasta procesar la respuesta JSON, no el tiempo hasta el primer token de streaming.

| Indicador | Gemini 3.5 Flash-Lite | Gemini 3.6 Flash |
|---|---:|---:|
| Intentos | 4 | 4 |
| Respuestas exitosas | 4 | 3 |
| Respuestas correctas (`40`) | 4 de 4 exitosas | 3 de 3 exitosas |
| Fallos observados | 0 | 1 (HTTP 503) |
| Latencia de los intentos exitosos | 7,08 / 7,86 / 6,35 / 19,29 s | 2,15 / 3,44 / 2,48 s |
| **Latencia promedio de éxitos** | **10,14 s** | **2,69 s** |
| Tokens totales por respuesta exitosa | 22 / 22 / 22 / 22 | 154 / 162 / 161 |
| Promedio de tokens totales por éxito | 22 | 159 |
| Costo estimado total de respuestas exitosas | USD 0,00004400 | USD 0,00160875 |
| **Costo estimado por respuesta exitosa** | **USD 0,00001100** | **USD 0,00053625** |

[Ver captura de la ejecución de las pruebas](./pruebas_consumo.png).

**Interpretación de los resultados:**

- **Costo:** Flash-Lite presentó un costo estimado aproximadamente 48,75 veces menor por respuesta exitosa en esta prueba.
- **Latencia:** Flash obtuvo un promedio de 2,69 segundos frente a 10,14 segundos de Flash-Lite; fue aproximadamente 3,77 veces más rápido en la muestra de peticiones exitosas.
- **Calidad para el caso evaluado:** todos los resultados exitosos fueron correctos. Al tratarse de una operación muy simple, la prueba no demuestra diferencias de calidad en tareas exigentes.
- **Disponibilidad observada:** Flash presentó un HTTP 503 en uno de cuatro intentos. La muestra es insuficiente para concluir que su disponibilidad general sea inferior.

**Limitaciones:** solo se realizaron cuatro intentos por modelo; un intento de Flash-Lite tardó 19,29 segundos y afecta el promedio. Los costos son **estimaciones basadas en `usageMetadata` y en las tarifas configuradas**, no comprobantes de facturación real. No se registró el desglose de tokens de entrada, salida y razonamiento por intento en la captura, por lo que no es posible explicar con certeza toda la diferencia de consumo. El uso del mismo enunciado no garantiza un consumo idéntico entre modelos.

## 4. Justificación de la elección

Se prioriza el **costo por respuesta útil**, dado que el alcance actual es una miniaplicación educativa que realiza consultas sencillas y cuyo requisito es entregar la respuesta correcta, no generar explicaciones extensas ni ejecutar razonamiento complejo.

En las pruebas realizadas, ambos modelos respondieron correctamente siempre que entregaron una respuesta. Gemini 3.5 Flash-Lite resolvió las cuatro peticiones, utilizó 22 tokens totales por éxito y presentó un costo estimado promedio de **USD 0,00001100** por respuesta exitosa. Su desventaja fue la mayor latencia media (**10,14 segundos**).

En el contexto del prototipo, esta demora es aceptable como compromiso provisional frente a la diferencia de costo observada. La decisión cambiaría si se establece un objetivo de latencia estricto o si pruebas más amplias muestran que el modelo elegido no cumple la calidad requerida.

## 5. Alternativa descartada y por qué

Se descarta **Gemini 3.6 Flash** (`gemini-3.6-flash`) **como modelo predeterminado para esta versión**.

Aunque fue más rápido en las peticiones exitosas (**2,69 segundos de media**), para la operación utilizada **no aportó una mejora observable de exactitud** y presentó un costo estimado por respuesta exitosa muy superior (**USD 0,00053625**). Además, una de sus cuatro solicitudes respondió HTTP 503; se registra como incidencia puntual y no como prueba de menor fiabilidad permanente.

Por estos motivos, su ventaja de latencia no compensa, por ahora, el aumento de costo para el requisito concreto del prototipo. **No se descarta su uso futuro** si la aplicación incorpora tareas más complejas o exige tiempos de respuesta menores.

## 6. Seguimiento de la decisión

Antes de considerar esta decisión definitiva para producción, se recomienda repetir la evaluación con más ejecuciones, alternar el orden de los modelos, registrar separadamente tokens de entrada, salida y razonamiento, y comprobar la calidad mediante varias preguntas representativas. También conviene medir mediana y percentiles de latencia, así como el tratamiento de errores HTTP 429/503.

**Resultado del ADR:** `gemini-3.5-flash-lite` queda documentado como modelo predeterminado para el prototipo, con reevaluación pendiente al aumentar el alcance de la aplicación.

## 7. Aplicación de la decisión en la Unidad U1.5

El código y `.env.example` usan `gemini-3.5-flash-lite` como predeterminado. El
archivo `.env` local también se configuró con ese modelo para la ejecución de la
prueba. `GEMINI_MODEL` permite cambiarlo explícitamente; en ese caso deben
revisarse las tarifas usadas por el ejemplo de estimación de costo.

La separación de responsabilidades es deliberada: el banco describe las tareas,
`armar_peticion` construye la solicitud, `enviar_peticion` se ocupa de HTTP y
`parsear_respuesta_json` valida los datos recibidos. Así se pueden agregar
prompts sin editar el cliente HTTP ni duplicar lógica de validación.
