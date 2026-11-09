# Agente académico con herramientas — Unidad 2.4

## Propósito y alcance

El agente responde preguntas sobre indicadores académicos agregados mediante
cuatro herramientas. El catálogo de `datos_agente_academico.py` contiene datos
**ficticios** y coherentes con los ejemplos previos: aprobación (68 % y 74 %),
asistencia (82 % y 85 %) y retención (90 % y 92 %) para 2024 y 2025. Cada
indicador tiene una definición y un identificador de fuente. Los identificadores
no apuntan a documentos institucionales reales.

La Unidad 2.3 usa una cadena que clasifica y sigue rutas prefijadas. Aquí el
modelo recibe herramientas con descripciones de uso y decide cuáles invocar en
cada turno. `AgentExecutor` limita el ciclo a seis iteraciones o 60 segundos y
devuelve `intermediate_steps` para revisar la secuencia ejecutada. El agente
incluye una respuesta de información insuficiente cuando no encuentra respaldo.

## Componentes

| Archivo | Responsabilidad |
| --- | --- |
| `datos_agente_academico.py` | Catálogo ficticio de tasas, definiciones y fuentes. |
| `herramientas_academicas.py` | Cuatro herramientas `@tool` con contratos separados. |
| `agente_academico.py` | Prompt, ejecutor, memoria por sesión y registro JSONL. |
| `modelo_agente_simulado.py` | Modelo determinista para comprobar el ciclo sin red. |
| `ejemplo_agente_academico.py` | Tres consultas con traza visible; opción `--real`. |
| `tests/test_agente_academico.py` | Verificación de herramientas, agente, memoria y trazas. |

| Herramienta | Entrada | Uso esperado | Resultado |
| --- | --- | --- | --- |
| `consultar_indicador` | Indicador y año opcional | Consultar una cifra o períodos disponibles. | Porcentaje, año y fuente. |
| `consultar_definicion` | Indicador | Preguntar por significado o exclusiones. | Definición y fuente. |
| `calcular_variacion` | Indicador, año inicial y final | Comparar dos tasas. | Diferencia en **puntos porcentuales** o dato faltante. |
| `consultar_fuente` | Código de fuente | Preguntar por procedencia y alcance. | Identificación de la fuente ficticia. |

Las herramientas de varios argumentos declaran `args_schema` con descripciones
por campo. El cálculo usa números del catálogo y resta aritmética; no evalúa
expresiones proporcionadas por el modelo. Un indicador o período desconocido
produce una observación explícita de ausencia. Las herramientas no escriben
datos ni consultan servicios externos.

## Práctica de la sesión 3: dos herramientas como mínimo

La consigna pide al menos dos herramientas del dominio, un agente construido con
`create_tool_calling_agent` y `AgentExecutor`, y dos invocaciones reales que se
verifiquen en `intermediate_steps`. Esta implementación usa cuatro herramientas
y tres consultas. Las trazas de la ejecución con Gemini muestran:

| Consulta | Acciones observadas con Gemini | Dato de la respuesta |
| --- | --- | --- |
| Aprobación en 2025 | `consultar_indicador` | 74 %, FICHA-A ficticia. |
| Definición de retención | `consultar_definicion` | Continuidad de matrícula, FICHA-C ficticia. |
| Variación y ficha de aprobación | `calcular_variacion` → `consultar_fuente` | 6 puntos porcentuales, FICHA-A ficticia. |

Las tres invocaciones se realizaron con el modelo configurado en `.env`
(`gemini-3.5-flash-lite`) el 8 de noviembre de 2026. El archivo
`evaluaciones/unidad_2_4/trazas_gemini.jsonl` conserva la entrada, acciones,
argumentos, observaciones y respuesta de cada caso. La secuencia refleja las
decisiones de esa ejecución; otra llamada al modelo podría elegir otra ruta.

Para reproducir la demostración sin credenciales:

```powershell
.\.venv\Scripts\python.exe -X utf8 ejemplo_agente_academico.py
```

El modelo simulado sigue reglas programadas para las tres preguntas de ejemplo.
Comprueba la integración y el formato de la traza, pero **no** valida la elección
de herramientas por Gemini. Para ejecutar las tres preguntas con Gemini, con
`.env` configurado y consumo de cuota:

```powershell
.\.venv\Scripts\python.exe -X utf8 ejemplo_agente_academico.py --real
```

En el modo predeterminado, cada ejecución agrega tres registros al archivo JSONL
correspondiente. La
consola muestra el contenido de `intermediate_steps` como
`herramienta(argumentos) -> observación`; no muestra el razonamiento privado del
modelo. Los archivos `trazas_simulado.jsonl` y `trazas_gemini.jsonl` separan
claramente ambos tipos de evidencia.

### Comprobación de memoria entre dos preguntas

La demostración de memoria usa una sola sesión para estas preguntas:

1. «¿Cómo estuvo la aprobación del año 2025?»
2. «¿Y la retención?»

La segunda pregunta cambia de indicador y omite el año. En la ejecución con
Gemini del 9 de noviembre de 2026, el agente consultó aprobación con
`periodo=2025` en el primer turno y retención con `periodo=2025` en el segundo.
Respondió 74 % y 92 %, respectivamente. Ambas entradas y sus acciones están en
[`trazas_memoria_gemini.jsonl`](../evaluaciones/unidad_2_4/trazas_memoria_gemini.jsonl).
La demostración local equivalente se guarda en
[`trazas_memoria_simulado.jsonl`](../evaluaciones/unidad_2_4/trazas_memoria_simulado.jsonl).

```powershell
.\.venv\Scripts\python.exe -X utf8 ejemplo_agente_academico.py --memoria
.\.venv\Scripts\python.exe -X utf8 ejemplo_agente_academico.py --memoria --real
```

El segundo comando consume cuota. Sin `--memoria`, las tres consultas originales
siguen usando sesiones independientes y sus trazas separadas. La prueba
automatizada comprueba además que una sesión nueva no recibe el año de otra.

## Memoria y registro

`AgenteAcademico.consultar(pregunta, session_id)` obtiene el historial de esa
sesión y pasa una copia de sus mensajes a `chat_history` antes de invocar el
ejecutor. Al terminar, añade `HumanMessage` con la pregunta y `AIMessage` con la
respuesta final. Así, antes del segundo turno hay dos mensajes previos; después,
hay cuatro. El `agent_scratchpad` conserva las acciones del turno en curso y no
se incorpora al historial entre turnos. Las sesiones se aíslan por identificador
y `cerrar_sesion` descarta un historial.

La lección muestra este patrón mediante `RunnableWithMessageHistory` e
`InMemoryChatMessageHistory`. Esta implementación realiza el mismo paso de
lectura, inyección y guardado de forma explícita, con `HistorialSesion`, evitando
depender de esas clases marcadas como obsoletas en la versión instalada. La
memoria vive en el proceso: un reinicio la elimina y una conversación larga
aumenta los tokens enviados en llamadas sucesivas. El año recordado es contexto
conversacional; el valor de retención se consultó de nuevo en el catálogo.

Tras cada interacción completada, el agente puede añadir una línea JSON UTF-8
con fecha UTC, sesión, entrada, acciones y respuesta. El texto final se extrae
de los bloques de contenido del proveedor antes de mostrarlo o guardarlo; así
no se registran sus metadatos internos. En un uso con datos personales se deberá
definir retención, acceso y reducción de contenido antes de habilitar trazas.
El registro no es una fuente de verdad académica: documenta lo que hizo el agente.

## Verificación y límites conocidos

```powershell
.\.venv\Scripts\python.exe -m pytest tests -q
```

Las pruebas usan un modelo simulado y no requieren API. Cubren selección y
orden de herramientas, datos ausentes, unidad de variación, validación de
argumentos, aislamiento de sesiones, referencia entre turnos y escritura de
trazas. La revisión de respuestas de Gemini sigue siendo necesaria: un modelo
puede omitir una herramienta o redactar una conclusión incompatible con su
observación. El agente aún no integra RAG, control de acceso ni verificación
automática contra documentos autorizados.

El historial se guarda como mensajes en memoria por sesión y se pasa al prompt
de `AgentExecutor` en cada consulta. Antes de una versión de producción se deberá
añadir persistencia y probar de nuevo el aislamiento de sesiones. El cliente
LangChain de este ejemplo tampoco usa el registro de costos del cliente REST del
Módulo 2. El número de llamadas varía según las herramientas que el modelo elija.
