# Decisión de personalización — ejercicio didáctico de tickets

## 1. El problema

Un clasificador de tickets debe convertir mensajes libres en un JSON con
`intencion` y `prioridad`, usando siempre una de cinco intenciones y una de tres
prioridades. El problema ilustrado es la consistencia de esa clasificación y de
su formato; no requiere consultar información que cambie con el tiempo.

Este caso es **didáctico y ficticio**. El material de la actividad aporta siete
ejemplos, pero no una medición de 20 respuestas de un clasificador real.

## 2. Resultado del método de decisión

Para mostrar cómo se aplica el método del curso, se usa el siguiente **escenario
hipotético**, no un resultado medido: se supone que 4 de 20 respuestas incumplen
el formato, que el equipo permite como máximo dos intentos de entrenamiento y
que solo necesita una versión del clasificador.

| Pregunta del método | Respuesta del escenario | Fundamento |
| --- | --- | --- |
| ¿Cambia la información al menos una vez al mes? | No | La tarea es asignar etiquetas fijas a mensajes. |
| ¿Fallan al menos 3 de 20 respuestas en formato o tono? | Sí | Supuesto didáctico: 4 de 20 fallan. No se ha medido. |
| ¿Hay al menos 200 ejemplos etiquetados y revisados? | No | El dataset preparado tiene 15 pares ficticios. |
| ¿Hay máximo dos entrenamientos o hace falta iterar en menos de un día? | Sí | Supuesto didáctico: máximo dos intentos. |
| ¿Se necesitan dos o más variantes? | No | El escenario supone un solo clasificador. |

Con las ponderaciones del curso, **PEFT obtiene 3 puntos, RAG 2 y fine-tuning
completo 1**. El puntaje depende de los dos supuestos identificados arriba; no
constituye evidencia de rendimiento del modelo.

## 3. Técnica elegida y por qué

En el escenario descrito, **PEFT** es la técnica candidata para enseñar un
comportamiento de salida estable con menos costo que un ajuste completo. RAG no
resuelve el formato de un clasificador y el ajuste completo no se justifica con
15 pares. Antes de entrenar conviene comparar con una instrucción clara y un
esquema JSON, que pueden resolver la tarea sin personalizar pesos.

Esta elección es un ejercicio de decisión, **no una orden de entrenamiento**.
La documentación vigente de Google indica que el tuning no está disponible con
una clave de Gemini API o AI Studio; requiere Gemini Enterprise Agent Platform.
Además, el modelo `gemini-2.0-flash` del ejemplo del curso no debe asumirse como
modelo de tuning vigente.

## 4. Qué se necesitaría para ejecutarla

Hay **15 pares válidos**, tres por cada intención. Para alcanzar el criterio
orientativo de **200 ejemplos** que usa esta actividad faltarían **185 pares**:
37 más por intención para llegar a 40 en cada una. También se necesitaría un
conjunto de evaluación separado, por ejemplo 20 tickets que no aparezcan en el
entrenamiento, y una revisión humana de prioridades para evitar etiquetas
contradictorias. Se debe comprobar la disponibilidad, el modelo admitido y el
costo de tuning en la plataforma elegida antes de enviar cualquier trabajo.

El archivo `dataset_tuning.py` de esta carpeta construye los 15 pares, imprime
el balance y verifica dos casos rotos sin incorporarlos al entrenamiento.
