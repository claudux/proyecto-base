# Límites de la evaluación léxica — Unidad 2.2

## Qué mide

La precisión, cobertura y F1 comparan las palabras de una respuesta con una
referencia escrita previamente, contando repeticiones después de normalizar
mayúsculas, puntuación y espacios. Miden coincidencia léxica, no veracidad ni
comprensión de la pregunta. El archivo
[`resultados_metricas.json`](../evaluaciones/unidad_2_2/resultados_metricas.json)
conserva las respuestas y los cálculos; la
[`revision_manual.json`](../evaluaciones/unidad_2_2/revision_manual.json)
registra el juicio humano por caso.

## Modos de falla conocidos

- **Respuesta correcta con F1 bajo.** En A18 (F1 0,437), el modelo dijo que no
  se informaron las edades, que es precisamente la respuesta correcta. En A19
  (F1 0,595) reconoció que no existe el dato de 2026. Las paráfrasis redujeron
  la coincidencia de palabras sin volver incorrectas esas respuestas.
- **Error de unidad con F1 alto.** En A11 (F1 0,897), el contexto mostraba que
  la deserción pasó de 12 % a 9 %. La referencia dice **3 puntos porcentuales**;
  el modelo respondió **3 %**. Un F1 alto no distingue estas magnitudes.
- **Cálculo omitido.** En A15 y A16, el contexto entregaba 18 de 20 cursos y
  40 de 200 estudiantes, respectivamente. El modelo afirmó que el porcentaje
  no estaba especificado, aunque podía calcular 90 % y 20 %. Sus F1 fueron
  0,571 y 0,519. La métrica señala diferencias, pero no explica la causa.
- **Dato omitido con F1 relativamente alto.** En A04 (F1 0,846), el modelo
  identificó bien 2025 como el año con mayor aprobación, pero omitió el 74 %
  presente en la referencia. La revisión manual marcó completitud parcial.
- **Negaciones y cifras requieren atención aunque coincidan muchas palabras.**
  En A20 el modelo conservó correctamente la exclusión de convalidaciones.
  Una negación ausente podría invertir el sentido con un cambio pequeño en F1;
  por eso este tipo de respuesta siempre necesita lectura humana.

## Muestra revisada

El 30 de octubre de 2026 se generaron **20 respuestas reales** mediante
`ClienteGemini.consultar_modelo`, con el modelo `gemini-3.5-flash-lite` y
contextos académicos explícitamente ficticios. Las referencias se definieron
antes de llamar al modelo. El F1 promedio fue **0,755** y el costo total
estimado fue **USD 0,00205410**; son resultados de esta única ejecución, no una
medida general de calidad ni un cargo facturado.

Se revisaron **12 respuestas**: las cinco con F1 más bajo (A18, A09, A16, A15,
A19), las cinco con F1 más alto (A11, A14, A17, A01, A03) y dos casos adicionales
(A04 por omisión y A20 por negación). Cada registro incluye corrección factual,
completitud, contradicción y una nota. La revisión encontró respuestas útiles
con F1 bajo y al menos un error relevante con F1 alto.

## Recomendación de uso

Usar F1 para ordenar casos y comparar versiones sobre el mismo conjunto de
referencias. Revisar manualmente las respuestas con cifras, unidades, fechas,
negaciones, fuentes o datos faltantes, sin aplicar un umbral de F1 como criterio
único de aprobación. Para un asistente académico futuro, verificar los cálculos
y la procedencia contra datos y documentos autorizados antes de mostrar una
respuesta como fundamentada. Esta evaluación todavía usa datos ficticios y no
demuestra desempeño con información institucional real.
