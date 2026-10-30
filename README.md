# Miniaplicación Gemini: consultas sobre El Niño en Chile

Proyecto Python que consume la API REST de Gemini. Su estado actual reúne un
cliente de consultas, medición de uso y costo estimado, y un banco de prompts para
explicar el fenómeno de El Niño en Chile, extraer datos de textos meteorológicos
y evaluar afirmaciones. Es un prototipo educativo; no emite pronósticos ni alertas.

Este caso de prueba permite verificar la base técnica del Gate 1. La visión del
proyecto final es un asistente de consulta de información académica, descrito más
adelante en este documento.

El proyecto también incorpora un cliente modular desarrollado para el Módulo 2.
La implementación del Gate 1 se conserva para que ambas etapas puedan revisarse
por separado mientras llega su evaluación.

## Funcionalidades

- Construye peticiones a `models.generateContent` con la pregunta del usuario,
  una instrucción de sistema opcional y un esquema JSON opcional.
- Envía la clave mediante la cabecera `x-goog-api-key`, sin incluirla en el código
  ni en la URL.
- Extrae el texto y los metadatos de tokens de la respuesta, y calcula un costo
  estimado con las tarifas configuradas para el modelo elegido.
- Interpreta y valida respuestas JSON: claves, tipos y valores permitidos.
- Prueba tres prompts con tres llamadas reales por prompt y registra el resultado
  de cada ejecución.

El modelo predeterminado es `gemini-3.5-flash-lite`, según la
[decisión de arquitectura](docs/decision-arquitectura.md). La variable
`GEMINI_MODEL` permite elegir otro modelo; si se cambia, también deben revisarse
las tarifas usadas en el cálculo de costo.

## Visión del proyecto final y alcance del Gate 1

Al completar la ficha de alineación técnica, tenía identificado el problema que
quería abordar, pero aún no conocía con claridad el contenido ni la progresión
del curso. Por eso planteé como objetivo inicial, de manera tentativa, un
asistente de gestión académica. Con lo aprendido en el Módulo 1, esa visión se
puede precisar: desarrollar una aplicación que permita consultar indicadores
educativos agregados y documentación institucional mediante lenguaje natural,
con respuestas fundamentadas en la información disponible para apoyar la toma
de decisiones.

Un caso de uso previsto es preguntar cómo cambió la tasa de aprobación entre
dos períodos y qué documento institucional define ese indicador. Una respuesta
útil debería identificar los períodos comparados, mostrar los datos utilizados,
indicar la fuente documental y reconocer si falta información para responder.
Esta funcionalidad académica es una meta del proyecto final; este repositorio
todavía no integra datos académicos ni documentos institucionales.

El Gate 1 entrega la base técnica verificable: configuración del entorno,
consumo de la API, manejo de errores, separación de responsabilidades,
procesamiento y validación de respuestas estructuradas, medición de uso y costo,
y pruebas de consistencia de prompts. Los ejemplos sobre El Niño en Chile
permiten comprobar esas capacidades con un tema acotado. Su resultado no
demuestra todavía la exactitud de una respuesta académica ni la trazabilidad de
sus fuentes.

En las siguientes etapas se prevé incorporar fuentes académicas autorizadas,
adaptar los prompts y validar las respuestas frente a esos datos y documentos.
La solución final deberá reunir estas capacidades en un flujo utilizable y
evaluar tanto su funcionamiento como la calidad de las respuestas. La base de
consumo y validación construida en este Gate se conserva para esa evolución.

## Estructura del repositorio

| Ruta | Contenido |
| --- | --- |
| `src/consumir_gemini.py` | Cliente REST, validación de respuestas y cálculo de costo. |
| `src/url_rota.py` | Ejercicio previo de manejo de errores de red. |
| `prompts/banco.py` | Tres prompts con instrucciones, entradas de ejemplo y esquemas JSON. |
| `prompts/test_consistencia.py` | Ejecución repetida del banco contra Gemini. |
| `prompts/registro_resultados.json` | Último registro generado por la prueba. |
| `cliente_gemini/` | Cliente modular del Módulo 2: configuración, transporte, reintentos, respuestas y costos. |
| `tests/` | Pruebas unitarias del cliente modular, sin red ni credencial real. |
| `ejemplo_academico_mock.py` | Ejemplo académico con datos y respuesta simulados. |
| `ejemplo_cliente_modulo2.py`, `ejemplo_banco_modulo2.py` y `ejecutar_banco_modulo2.py` | Ejemplos de consulta real mediante el cliente modular. |
| `docs/` | Diagrama y decisión de arquitectura del Gate 1, diseño del cliente modular y registros de verificación. |
| `requirements.txt` | Dependencias del entorno Python. |
| `.env.example` | Plantilla de configuración sin credenciales reales. |

## Instalación desde el repositorio

Necesitas Git y Python; para las consultas reales también necesitas una clave de
API de Gemini. El proyecto se verificó con Python 3.14.6. En PowerShell:

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

Para ejecutar una consulta y mostrar su costo estimado:

```powershell
.\.venv\Scripts\python.exe -m src.consumir_gemini
```

Una ejecución correcta muestra la respuesta de Gemini, la latencia y el costo
estimado. Si la consulta falla, el programa termina con código de salida distinto
de cero y muestra el motivo.

Para ejecutar el banco de prompts:

```powershell
.\.venv\Scripts\python.exe -m prompts.test_consistencia
```

La prueba realiza nueve llamadas reales en total y sobrescribe
`prompts/registro_resultados.json` con la fecha, el modelo, los éxitos y los
motivos de los fallos. La ejecución consume cuota de la API. El registro actual
muestra **3/3 respuestas estructuralmente válidas por prompt** con
`gemini-3.5-flash-lite`. Esta medición comprueba el formato y el esquema JSON;
no certifica la exactitud científica del contenido generado.

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

El último comando hace tres llamadas reales, una por cada prompt del banco
existente en `prompts/banco.py`, consume cuota y no modifica
`prompts/registro_resultados.json`. El Gate 1 sigue en evaluación; sus archivos
en `src/` y `prompts/` no se sustituyeron. La prueba con un 429 real y su registro
continúan pendientes; las pruebas actuales verifican el reintento con respuestas
429 simuladas.

## Historial de avances

Los siguientes hitos proceden de los commits existentes en Git:

| Fecha | Avance | Commits |
| --- | --- | --- |
| 2026-10-09 | Creación de la estructura inicial, plantilla de entorno y reglas de exclusión. | `98ce847` |
| 2026-10-11 | Configuración de dependencias y respaldo de la prueba en Postman. | `174ef9d`, `92464a2`, `7229804` |
| 2026-10-12 | Primera versión del consumo del servicio y ejercicio de error de red. | `377bf63` |
| 2026-10-16 | Refactorización del cliente, manejo de excepciones y comentarios sobre responsabilidades. | `7251cd2`, `34b9054` |
| 2026-10-19 | Incorporación del diagrama de arquitectura. | `9419341` |
| 2026-10-20 | Medición de tokens y costo, actualización del diagrama y documentación de la elección del modelo. | `75d9cef`, `4f7d490` |
| 2026-10-23 | Incorporación del banco de prompts sobre El Niño en Chile, validación JSON, prueba de consistencia, registro de resultados y documentación actualizada. | `a6fcc4d` |
| 2026-10-23 | Preparación del Gate 1: fallo detectable en la ejecución, dependencias directas y registro de verificación local. | `80b7cae` |

## Alcance de los resultados

Las tendencias climáticas no describen necesariamente lo que ocurrirá en una
región o fecha concretas. Para información meteorológica vigente, consulta los
boletines de la Dirección Meteorológica de Chile. Los costos mostrados por el
prototipo son estimaciones basadas en los tokens reportados por la API, no cargos
facturados.
