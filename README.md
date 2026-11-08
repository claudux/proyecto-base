# Asistente académico con Gemini y LangChain

Prototipo Python para consultar indicadores educativos agregados y definiciones
académicas en lenguaje natural. Usa Gemini mediante un cliente REST modular y
LangChain para orquestar consultas y ejecutar un agente con herramientas. Los
datos, documentos y fuentes incluidos en el repositorio son **ficticios**:
permiten probar el software, pero no representan a una institución real ni
deben usarse para decisiones académicas.

El objetivo del proyecto es responder preguntas como «¿cómo cambió la tasa de
aprobación entre dos períodos?» y «¿qué documento define ese indicador?», con
datos, unidades y fuentes explícitas. La integración de fuentes institucionales
autorizadas y su verificación automática siguen pendientes.

## Funcionalidades

- Construye peticiones a `models.generateContent` con la pregunta del usuario,
  una instrucción de sistema opcional y un esquema JSON opcional.
- Envía la clave mediante la cabecera `x-goog-api-key`, sin incluirla en el código
  ni en la URL.
- Extrae el texto y los metadatos de tokens de la respuesta, y calcula un costo
  estimado con las tarifas configuradas para el modelo elegido.
- Interpreta y valida respuestas JSON: claves, tipos y valores permitidos.
- Incluye tres prompts académicos estructurados: explicar un indicador, extraer
  un dato y evaluar si una afirmación está respaldada por el contexto.
- Clasifica y enruta preguntas académicas mediante LangChain; cada ruta combina
  extracción, análisis, redacción y revisión, con manejo de fallos.
- Permite que un agente elija entre cuatro herramientas académicas, conserve
  memoria por sesión y registre las acciones que ejecutó antes de responder.

El modelo predeterminado es `gemini-3.5-flash-lite`, según la
[decisión de arquitectura](docs/decision-arquitectura.md). La variable
`GEMINI_MODEL` permite elegir otro modelo; si se cambia, también deben revisarse
las tarifas usadas en el cálculo de costo.

## Estado actual y guía de la Unidad 2.4

La etapa actual implementa un agente académico sobre un catálogo local y
**ficticio**. La práctica de la sesión 3 queda respaldada por tres consultas
ejecutadas con Gemini: dos usan herramientas diferentes por separado y una
combina dos herramientas. La elección se comprueba en `intermediate_steps` y
queda registrada en las trazas. El agente también tiene memoria entre turnos de
una misma sesión y un límite explícito de iteraciones.

Estos son los documentos y archivos principales de la entrega, con sus rutas
desde la raíz del repositorio:

| Ruta | Qué consultar allí |
| --- | --- |
| [`docs/agente-unidad-2-4.md`](docs/agente-unidad-2-4.md) | Diseño del agente, contratos de las cuatro herramientas, práctica de la sesión 3, memoria, comandos y límites técnicos. |
| [`docs/limites-autonomia-agente.md`](docs/limites-autonomia-agente.md) | Riesgo de cada herramienta, supervisión humana, revisión de trazas y respuesta ante fallos. |
| [`evaluaciones/unidad_2_4/trazas_gemini.jsonl`](evaluaciones/unidad_2_4/trazas_gemini.jsonl) | Evidencia de las tres consultas con Gemini: entrada, herramientas elegidas, argumentos, observaciones y respuesta. |
| [`evaluaciones/unidad_2_4/trazas_simulado.jsonl`](evaluaciones/unidad_2_4/trazas_simulado.jsonl) | Evidencia equivalente del modelo determinista usado para la demostración local. |
| [`tests/test_agente_academico.py`](tests/test_agente_academico.py) | Pruebas sin red de herramientas, cálculo, validación, memoria, aislamiento de sesiones y trazas. |
| [`README.md`](README.md) | Instalación, ejecución, estructura y estado general del proyecto. |

El código de esta etapa se encuentra en
[`datos_agente_academico.py`](datos_agente_academico.py),
[`herramientas_academicas.py`](herramientas_academicas.py),
[`agente_academico.py`](agente_academico.py),
[`modelo_agente_simulado.py`](modelo_agente_simulado.py) y
[`ejemplo_agente_academico.py`](ejemplo_agente_academico.py). El primero define
los datos ficticios; el segundo, las herramientas; el tercero, el ejecutor, la
memoria y el registro. Los dos últimos permiten una demostración local o con
Gemini.

## Objetivo y alcance actual

La aplicación busca consultar indicadores educativos agregados y documentación
institucional mediante lenguaje natural. Una respuesta útil debe mostrar los
períodos comparados, el cálculo y su unidad, la fuente documental y las
limitaciones de la información disponible.

Un caso de uso previsto es preguntar cómo cambió la tasa de aprobación entre
dos períodos y qué documento institucional define ese indicador. Una respuesta
útil debería identificar los períodos comparados, mostrar los datos utilizados,
indicar la fuente documental y reconocer si falta información para responder.
El repositorio todavía no integra datos ni documentos institucionales reales.
Los ejemplos académicos proporcionan contextos de prueba controlados.

El Gate 1 entrega la base técnica verificable: configuración del entorno,
consumo de la API, manejo de errores, separación de responsabilidades,
procesamiento y validación de respuestas estructuradas, medición de uso y costo,
y pruebas de consistencia de prompts. Estos componentes se reutilizan ahora con
ejemplos académicos ficticios. La prueba de formato no demuestra todavía la
exactitud de una respuesta ni la trazabilidad de sus fuentes.

En las siguientes etapas se prevé incorporar fuentes académicas autorizadas y
validar las respuestas frente a esos datos y documentos.
La solución final deberá reunir estas capacidades en un flujo utilizable y
evaluar tanto su funcionamiento como la calidad de las respuestas. La base de
consumo y validación construida en este Gate se conserva para esa evolución.

## Estructura del repositorio

| Ruta | Contenido |
| --- | --- |
| `src/consumir_gemini.py` | Cliente REST, validación de respuestas y cálculo de costo. |
| `src/url_rota.py` | Ejercicio previo de manejo de errores de red. |
| `prompts/banco.py` | Tres prompts académicos con entradas ficticias y esquemas JSON. |
| `prompts/test_consistencia.py` | Ejecución repetida del banco contra Gemini. |
| `prompts/registro_resultados_gate1.json` | Registro histórico de una versión anterior del banco; no corresponde a los prompts actuales. |
| `prompts/registro_resultados.json` | Registro del banco actual, generado al ejecutar su prueba de consistencia. |
| `cliente_gemini/` | Cliente modular del Módulo 2: configuración, transporte, reintentos, respuestas y costos. |
| `tests/` | Pruebas automatizadas del cliente, pipeline, orquestación y agente; no necesitan red ni credencial real. |
| `ejemplo_academico_mock.py` | Ejemplo académico con datos y respuesta simulados. |
| `ejemplo_cliente_modulo2.py`, `ejemplo_banco_modulo2.py` y `ejecutar_banco_modulo2.py` | Ejemplos de consulta real mediante el cliente modular. |
| `pipeline_texto.py` y `metricas_texto.py` | Normalización y métricas léxicas de la Unidad 2.2. |
| `casos_academicos.py` y `evaluar_unidad_2_2.py` | Veinte casos ficticios, consultas reales y registro reanudable de resultados. |
| `evaluaciones/unidad_2_2/` | Respuestas, métricas y revisión manual de la Unidad 2.2. |
| `docs/` | Arquitectura, diseño, verificaciones y límites de cada etapa; los documentos de la Unidad 2.4 se detallan en la guía anterior. |
| `requirements.txt` | Dependencias del entorno Python. |
| `orquestacion_academica.py` y `ejemplo_langchain_academico.py` | Flujo académico LCEL de la Unidad 2.3 y demostración local o con Gemini. |
| `datos_agente_academico.py`, `herramientas_academicas.py` y `agente_academico.py` | Catálogo ficticio, cuatro herramientas y agente de la Unidad 2.4. |
| `modelo_agente_simulado.py` y `ejemplo_agente_academico.py` | Demostración del agente sin red o con Gemini, con traza de acciones. |
| `docs/agente-unidad-2-4.md` y `docs/limites-autonomia-agente.md` | Diseño, evidencia de la sesión 3 y límites de autonomía. |
| `evaluaciones/unidad_2_4/` | Trazas separadas de la ejecución con Gemini y la demostración simulada. |
| `.env.example` | Plantilla de configuración sin credenciales reales. |

## Instalación desde el repositorio

Necesitas Git y Python; para las consultas reales también necesitas una clave de
API de Gemini. El proyecto se verificó con Python 3.14.6. Las dependencias de
`requirements.txt` incluyen `langchain-classic`, necesario para
`AgentExecutor` y `create_tool_calling_agent` en esta etapa. En PowerShell:

1. Clona el repositorio y entra en su carpeta:

   ```powershell
   git clone https://github.com/claudux/proyecto-base.git
   Set-Location proyecto-base
   ```

2. Crea un entorno virtual e instala las dependencias declaradas:

   ```powershell
   python -m venv .venv
   .\.venv\Scripts\python.exe -m pip install -r requirements.txt
   .\.venv\Scripts\python.exe -m pip check
   ```

3. Crea tu configuración local:

   ```powershell
   Copy-Item .env.example .env
   notepad .env
   ```

   Reemplaza `tu_llave_aqui` por tu clave en `GEMINI_API_KEY`. El modelo
   configurado en la plantilla es `gemini-3.5-flash-lite`. `.env` está excluido
   por `.gitignore` y no debe añadirse al repositorio.

## Ejecución

Para ejecutar una consulta académica ficticia y mostrar su costo estimado:

```powershell
.\.venv\Scripts\python.exe -m src.consumir_gemini
```

Una ejecución correcta muestra la respuesta de Gemini, la latencia y el costo
estimado. El ejemplo aporta explícitamente cifras y fuente ficticias; Gemini no
consulta una base institucional. Si la consulta falla, el programa termina con
código de salida distinto de cero y muestra el motivo.

Para ejecutar el banco de prompts:

```powershell
.\.venv\Scripts\python.exe -m prompts.test_consistencia
```

La prueba realiza nueve llamadas reales en total y crea o sobrescribe
`prompts/registro_resultados.json` con la fecha, el modelo, los éxitos y los
motivos de los fallos. Consume cuota de la API. **El banco académico aún no se ha
ejecutado contra Gemini**; el registro histórico de una versión anterior se
conserva por separado. La prueba comprueba formato y esquema JSON, no la
exactitud de cifras o definiciones.

## Módulo 2: cliente modular y ejemplo académico

El cliente del Módulo 2 ofrece una entrada pública,
`ClienteGemini.consultar_modelo(...)`, que construye la petición, la envía y
devuelve el texto procesado. Clasifica 401/403 como errores de autenticación sin
reintento; trata 429, 5xx, timeout y fallos de conexión como temporales. Para
estos últimos aplica hasta tres intentos con backoff exponencial, techo y jitter.
También registra los tokens y el costo estimado por operación y por sesión.
El [diseño del cliente](docs/diseno-modulo2.md) explica sus componentes y el
contrato de errores.

Las pruebas de `tests/` usan respuestas y esperas simuladas. Para ejecutarlas
desde la raíz del proyecto, sin `.env` y sin consumir cuota de la API:

```powershell
.\.venv\Scripts\python.exe -m pytest tests -q
```

El ejemplo `ejemplo_academico_mock.py` conecta esta base técnica con la visión
del proyecto final. Presenta tasas de aprobación **ficticias** de 68 % en 2024
y 74 % en 2025, una definición y una fuente documental igualmente ficticias.
La respuesta simulada informa un aumento de **6 puntos porcentuales**, muestra
la fuente y advierte que no describe a una institución real. Se ejecuta sin
clave de API:

```powershell
.\.venv\Scripts\python.exe ejemplo_academico_mock.py
```

El ejemplo usa un transporte simulado que devuelve una respuesta con el formato
de Gemini. El cliente valida el esquema JSON y calcula un costo a partir de
tokens simulados. Esto comprueba el flujo del software, pero no demuestra que
Gemini haya generado la respuesta, que existan datos académicos integrados ni
que la fuente se haya verificado contra un documento real.

Para realizar consultas reales con el cliente modular, configura `.env` como
se indica arriba y ejecuta, según el alcance que quieras comprobar:

```powershell
.\.venv\Scripts\python.exe ejemplo_cliente_modulo2.py
.\.venv\Scripts\python.exe ejemplo_banco_modulo2.py
.\.venv\Scripts\python.exe ejecutar_banco_modulo2.py
```

El último comando hace tres llamadas reales, una por cada prompt académico de
`prompts/banco.py`, consume cuota y no modifica
`prompts/registro_resultados.json`. Las pruebas actuales verifican el reintento
con respuestas 429 simuladas; la prueba con un 429 real continúa pendiente.

### Unidad 2.2: evaluación de respuestas académicas

El pipeline de `pipeline_texto.py` convierte a minúsculas, separa puntuación,
normaliza espacios y tokeniza. `metricas_texto.py` compara referencia y respuesta
con `Counter`, contando repeticiones para calcular precisión, cobertura y F1.
Las métricas describen coincidencia de palabras; no comprueban por sí solas que
una cifra, una unidad o una afirmación sea correcta.

`casos_academicos.py` contiene **20 preguntas sencillas** sobre indicadores y
definiciones académicas. Todas las cifras, las fuentes y los documentos son
ficticios. Cada caso guarda una referencia escrita antes de consultar el modelo.
El script de evaluación usa `ClienteGemini.consultar_modelo` con ese contexto y
guarda cada respuesta en
[`resultados_metricas.json`](evaluaciones/unidad_2_2/resultados_metricas.json)
inmediatamente después de recibirla. Si la ejecución se interrumpe, una nueva
ejecución omite los casos ya guardados. Requiere la clave configurada en `.env`
y consume cuota de la API:

```powershell
.\.venv\Scripts\python.exe evaluar_unidad_2_2.py
```

Para limitar una ejecución a tres consultas nuevas, se puede agregar
`--limite 3`. Las tres primeras entradas conservan métricas del texto crudo y
del texto procesado. Por ejemplo, en A03 el F1 pasó de **0,800** a **1,000**
tras normalizar el formato. La ejecución registrada obtuvo **20/20 respuestas**,
con F1 promedio **0,755** y costo total estimado **USD 0,00205410**. Estos
números describen una única muestra de respuestas a datos inventados; no son
una evaluación de exactitud institucional ni un cargo facturado.

Se revisaron manualmente **12 casos**: los cinco F1 más bajos, los cinco más
altos y dos adicionales por omisión y negación. La
[`revision_manual.json`](evaluaciones/unidad_2_2/revision_manual.json) registra
corrección factual, completitud, contradicción y la justificación de cada caso.
El documento de [límites de la métrica](docs/limites_metrica.md) explica los
hallazgos: hubo respuestas correctas con F1 bajo y una respuesta con F1 alto
que confundió porcentajes con puntos porcentuales. Los cálculos y las fuentes
deberán verificarse contra datos autorizados cuando se integre el proyecto final.

Las pruebas de este pipeline y las métricas se incluyen en el mismo comando de
`pytest` mostrado arriba; no necesitan API ni credenciales.

### Unidad 2.3: orquestación académica con LangChain

El flujo en `orquestacion_academica.py` adapta las piezas de las lecciones al
asistente previsto. Una plantilla clasifica la pregunta como **indicador**,
**definición** o **sin datos**. `RunnableBranch` selecciona la ruta. En las dos
rutas académicas, cuatro pasos encadenados extraen evidencia del contexto,
analizan los datos o la definición, redactan una respuesta y revisan el borrador
contra el texto original. La salida de cada
paso alimenta al siguiente mediante `RunnablePassthrough.assign`. Una categoría
imprevista produce la respuesta de información insuficiente. Cada ruta tiene un
fallback con registro de error; un fallo anterior al enrutamiento se maneja en
`procesar_consulta`.

Para observarlo sin clave ni llamadas a la API:

```powershell
.\.venv\Scripts\python.exe ejemplo_langchain_academico.py
```

El ejemplo usa la ficha **ficticia** de aprobación de 2024 y 2025 y un modelo
simulado con respuestas fijas. Para ejecutar el mismo flujo con Gemini, una vez
configurada `.env`:

```powershell
.\.venv\Scripts\python.exe ejemplo_langchain_academico.py --real
```

La opción `--real` consume cuota: la clasificación más los cuatro pasos de la ruta
elegida hacen normalmente cinco llamadas. Usa `GEMINI_MODEL` y `GEMINI_API_KEY`
de `.env`. Esta integración LangChain es una vía de orquestación separada del
cliente REST del Módulo 2: todavía no contabiliza tokens ni costos. Sus prompts
solo restringen al modelo al contexto proporcionado; no verifican que las
afirmaciones finales coincidan con una fuente autorizada. El proyecto aún necesita
conectar documentos e indicadores reales autorizados, validar cifras y citas de
forma programática y evaluar respuestas antes de usarlas para decisiones.

La [captura de la prueba de ejecución](docs/prueba_langchain.png) muestra la
salida del ejemplo local, las pruebas automatizadas y una consulta con Gemini.

Las pruebas de `tests/test_orquestacion_academica.py` cubren normalización,
enrutamiento, orden de los cuatro pasos, falta de datos y fallos de ruta y
clasificación. Se ejecutan con el comando `pytest` anterior, sin red.

### Unidad 2.4: agente académico con herramientas

El catálogo ficticio de `datos_agente_academico.py` define aprobación,
asistencia y retención para 2024 y 2025, con definiciones y fuentes identificadas.
`herramientas_academicas.py` expone cuatro herramientas con funciones distintas:

| Herramienta | Pregunta que resuelve |
| --- | --- |
| `consultar_indicador` | Cifras y períodos disponibles. |
| `consultar_definicion` | Significado y exclusiones de un indicador. |
| `calcular_variacion` | Diferencia entre dos tasas, en puntos porcentuales. |
| `consultar_fuente` | Identificación y alcance de una fuente ficticia. |

`agente_academico.py` construye el agente con `create_tool_calling_agent` y
`AgentExecutor`, conserva el historial por `session_id`, limita el ciclo a seis
iteraciones y registra las acciones de `intermediate_steps` en JSONL. El modelo
simulado de `modelo_agente_simulado.py` permite comprobar el flujo sin red. La
descripción de cada componente y el contrato de las herramientas están en
[`docs/agente-unidad-2-4.md`](docs/agente-unidad-2-4.md).

La práctica de la sesión 3 pide al menos dos herramientas propias y dos
invocaciones reales verificadas mediante `intermediate_steps`. Se realizaron
tres consultas con Gemini: la primera eligió `consultar_indicador`, la segunda
`consultar_definicion` y la tercera usó `calcular_variacion` seguido de
`consultar_fuente`. La evidencia está en
[`trazas_gemini.jsonl`](evaluaciones/unidad_2_4/trazas_gemini.jsonl).

```powershell
.\.venv\Scripts\python.exe -X utf8 ejemplo_agente_academico.py
```

Este comando no requiere clave ni red. Escribe su evidencia en
[`trazas_simulado.jsonl`](evaluaciones/unidad_2_4/trazas_simulado.jsonl). Para
repetir las tres consultas con Gemini y consumir cuota de la API:

```powershell
.\.venv\Scripts\python.exe -X utf8 ejemplo_agente_academico.py --real
```

Cada ejecución agrega tres registros al archivo JSONL correspondiente. El
modelo simulado sigue reglas programadas; solo la traza real muestra la
selección hecha por Gemini en una ejecución concreta. Las pruebas del agente
están en [`tests/test_agente_academico.py`](tests/test_agente_academico.py) y
se incluyen en el comando general de `pytest`. En la verificación de esta
entrega pasaron **44 pruebas** sin llamadas a la API.

El [documento de límites de autonomía](docs/limites-autonomia-agente.md)
clasifica las cuatro herramientas como operaciones de solo lectura o cálculo,
define la revisión de trazas y un procedimiento ante respuestas inesperadas.
Las herramientas actuales no realizan escrituras ni acciones institucionales.
El historial se pierde al reiniciar el proceso; además, las clases de memoria
usadas para esta práctica emiten avisos de obsolescencia en la versión instalada
de LangChain. El agente aún no incorpora RAG, no verifica respuestas contra
fuentes autorizadas y no contabiliza costos mediante el cliente REST del
Módulo 2. Estos límites están desarrollados en los dos documentos de esta etapa.

## Historial de avances

Los siguientes hitos proceden de los commits existentes. Desde el cierre
técnico del Gate 1, los avances se presentan como parte del Módulo 2:

| Etapa | Fecha | Avance | Commits |
| --- | --- | --- | --- |
| Módulo 1 · Core | 2026-10-09 | Creación de la estructura inicial, plantilla de entorno y reglas de exclusión. | `98ce847` |
| Módulo 1 · Core | 2026-10-11 | Configuración de dependencias y respaldo de la prueba en Postman. | `174ef9d`, `92464a2`, `7229804` |
| Módulo 1 · Core | 2026-10-12 | Primera versión del consumo del servicio y ejercicio de error de red. | `377bf63` |
| Módulo 1 · Core | 2026-10-16 | Refactorización del cliente, manejo de excepciones y comentarios sobre responsabilidades. | `7251cd2`, `34b9054` |
| Módulo 1 · Core | 2026-10-19 | Incorporación del diagrama de arquitectura. | `9419341` |
| Módulo 1 · Core | 2026-10-20 | Medición de tokens y costo, actualización del diagrama y documentación de la elección del modelo. | `75d9cef`, `4f7d490` |
| Módulo 1 · Core | 2026-10-23 | Primer banco de prompts, validación JSON y prueba de consistencia. El banco vigente se adaptó después al caso académico. | `a6fcc4d` |
| Módulo 1 · Gate 1 | 2026-10-23 | Verificación técnica, dependencias reproducibles y documentación de instalación y ejecución. | `666f827`, `80b7cae`, `b13e9be`, `ec7d86e`, `8ec48e9` |
| Módulo 2 · Core | 2026-10-30 | Vinculación de la base del Gate 1 con la visión del asistente académico. | `8446984` |
| Módulo 2 · Core | 2026-10-30 | Integración del cliente modular, pruebas unitarias y ejemplo académico simulado. | `89af54b` |
| Módulo 2 · Core | 2026-10-30 | Actualización del historial del README para distinguir el Gate 1 de los avances del Módulo 2. | `48f021b`, `a59220f` |
| Módulo 2 · Core | 2026-10-30 | Evaluación de 20 respuestas académicas con métricas, pruebas y revisión manual documentada. | `f66ea30` |
| Módulo 2 · Unidad 2.3 | 2026-11-02 | Orquestación académica con LangChain, adaptación del banco de prompts, pruebas y captura de ejecución. | `d87634f` |
| Módulo 2 · Unidad 2.4 | 2026-11-08 | Agente académico con cuatro herramientas, memoria por sesión, trazas de Gemini, pruebas y documentación de autonomía; actualización del README. | `67f855a` |

## Alcance de los resultados

Todas las cifras y fuentes académicas del repositorio son ficticias. Antes de
usar respuestas para apoyar decisiones reales se necesitan fuentes autorizadas,
control de acceso, verificación programática de datos y citas, y evaluación con
casos institucionales. Los costos mostrados son estimaciones basadas en los
tokens reportados por la API, no cargos facturados.
