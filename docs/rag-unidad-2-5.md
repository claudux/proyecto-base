# RAG documental — Unidad 2.5

## Alcance

El corpus de `rag/corpus/` contiene diez documentos **ficticios**, relacionados
con el catálogo de `datos_agente_academico.py` y las capacidades ya existentes.
Sirven para demostrar recuperación y citas; no son fuentes institucionales.
Las cifras estructuradas y sus cálculos deben seguir comprobándose con las
herramientas del agente antes de utilizar una respuesta para decisiones reales.

## Flujo

1. `python -m rag.cli comparar` muestra dos tamaños de chunk sin usar red.
2. `python -m rag.cli indexar` divide los documentos, asigna IDs como
   `01_aprobacion.md:0`, obtiene embeddings de Gemini y guarda Chroma en
   `rag/almacen/`. El manifiesto registra modelo, parámetros, cantidad y huella
   del corpus. El comando se detiene si el índice ya existe para evitar duplicados.
3. `python -m rag.cli consultar "¿Qué es la retención?" --k 2` vuelve a abrir el
   índice, genera el embedding de la pregunta, recupera chunks y envía un contexto
   numerado al cliente Gemini. El prompt pide citas y reconoce información ausente.
4. `python -m rag.cli evaluar --k 2` compara los IDs recuperados con las 22
   preguntas etiquetadas en `evaluaciones/unidad_2_5/casos_recuperacion.json`.
   También conviene correrlo con `--k 1` y `--k 3`.

Todos los comandos se ejecutan desde la raíz del repositorio con el Python del
entorno virtual. Indexar, consultar y evaluar necesitan `GEMINI_API_KEY` en `.env`
y consumen cuota. `comparar` y las pruebas automatizadas no necesitan credencial.

## Decisiones y límites

- Se usa chunking recursivo de 500 caracteres con solapamiento de 50. Los diez
  textos actuales caben en un chunk cada uno, lo que hace inequívocos los IDs y
  permite comparar 150 frente a 500 caracteres antes de indexar.
- El índice y el manifiesto están ignorados por Git. Si cambian corpus, modelo o
  parámetros, hay que retirar el índice anterior y volver a indexar. La carga
  detecta un corpus desactualizado y no crea silenciosamente un índice vacío.
- Precisión@k divide aciertos entre recuperados; recall@k divide aciertos entre
  relevantes. Para dos preguntas sin respuesta, recall es `null` y se excluye
  del promedio. Su precisión es cero porque no hay documentos relevantes, pero
  esto **no** mide si la respuesta final se abstuvo correctamente.
- `registros_latencia_costo.jsonl` se genera solo para consultas reales. Incluye
  tiempos de embedding, búsqueda y generación, tokens de generación y costo
  estimado del cliente existente. El costo de embeddings es `null`: esta
  integración no entrega aquí su uso de tokens. No se debe presentar el importe
  registrado como costo total facturado del RAG.
- `revision_citas` detecta números inexistentes y respuestas sin citas. Una cita
  numéricamente válida tampoco comprueba que el contenido afirmado esté
  respaldado por el texto; esa revisión sigue siendo manual.
- Los informes de evaluación llevan fecha en el nombre para permitir comparar
  corridas. Se deben fijar las etiquetas antes de ejecutar el recuperador y no
  cambiarlas para mejorar artificialmente una métrica.

## Verificación manual del 10 de noviembre de 2026

Se ejecutó la indexación con embeddings reales y se recargó el índice en procesos
separados. Resultado: diez documentos y diez chunks. La comparación local produjo
44 chunks con tamaño 150 y diez con tamaño 500. La suite completa terminó con
48 pruebas aprobadas; `pip check` no encontró incompatibilidades.

| k | Precisión media | Recall medio | Preguntas |
| --- | ---: | ---: | ---: |
| 1 | 0,909 | 1,000 | 22 |
| 2 | 0,455 | 1,000 | 22 |
| 3 | 0,303 | 1,000 | 22 |

Se comprobaron respuestas reales sobre la variación de aprobación y la
definición de retención, ambas con citas existentes. Ante la pregunta sobre el
rector, ausente del corpus, el modelo respondió que faltaba evidencia. También
se comparó la misma pregunta con `k=2` y `k=3`: los tokens de entrada de la
generación fueron 328 y 448. La salida y el costo total variaron entre llamadas,
así que esta comparación solo demuestra el aumento de contexto enviado.
