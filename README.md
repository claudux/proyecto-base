# Miniaplicación Gemini: consultas sobre El Niño en Chile

Proyecto Python que consume la API REST de Gemini. Su estado actual reúne un
cliente de consultas, medición de uso y costo estimado, y un banco de prompts para
explicar el fenómeno de El Niño en Chile, extraer datos de textos meteorológicos
y evaluar afirmaciones. Es un prototipo educativo; no emite pronósticos ni alertas.

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

## Estructura del repositorio

| Ruta | Contenido |
| --- | --- |
| `src/consumir_gemini.py` | Cliente REST, validación de respuestas y cálculo de costo. |
| `src/url_rota.py` | Ejercicio previo de manejo de errores de red. |
| `prompts/banco.py` | Tres prompts con instrucciones, entradas de ejemplo y esquemas JSON. |
| `prompts/test_consistencia.py` | Ejecución repetida del banco contra Gemini. |
| `prompts/registro_resultados.json` | Último registro generado por la prueba. |
| `docs/` | Diagrama, decisión de arquitectura y respaldos de pruebas. |
| `requirements.txt` | Dependencias del entorno Python. |
| `.env.example` | Plantilla de configuración sin credenciales reales. |

## Instalación y configuración

Desde la raíz del repositorio, en PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Edita `.env` y reemplaza `tu_llave_aqui` por tu clave de Gemini. El archivo
`.env` está excluido por `.gitignore`; no debe agregarse al repositorio. La
configuración de ejemplo ya indica el modelo elegido.

## Ejecución

Para una consulta de ejemplo y su costo estimado:

```powershell
.\.venv\Scripts\python.exe -m src.consumir_gemini
```

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

## Alcance de los resultados

Las tendencias climáticas no describen necesariamente lo que ocurrirá en una
región o fecha concretas. Para información meteorológica vigente, consulta los
boletines de la Dirección Meteorológica de Chile. Los costos mostrados por el
prototipo son estimaciones basadas en los tokens reportados por la API, no cargos
facturados.
