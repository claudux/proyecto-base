# Decisión de personalización — asistente académico ficticio

## 1. El problema

El flujo de la Unidad 2.3 clasifica cada pregunta en `indicador`, `definicion`
o `sin_datos` para elegir su ruta. Necesita una categoría válida y consistente,
incluso cuando la pregunta académica menciona un dato que no está disponible.
El clasificador actual pide una sola palabra y normaliza salidas inesperadas a
`sin_datos`; por eso una salida mal formada puede cambiar la ruta. Esta tarea es
de comportamiento de clasificación. Las respuestas sobre cifras y fuentes
siguen siendo una tarea documental distinta, atendida por el RAG de la Unidad
2.5.

Las 20 respuestas de la Unidad 2.2 evalúan respuestas académicas, **no** 20
salidas de este clasificador. El repositorio tampoco contiene una medición de
fallos de formato de 20 clasificaciones reales. No se afirma que el umbral del
curso (3 de 20) ya se haya alcanzado.

## 2. Resultado del método de decisión

El método del curso exige cinco valores booleanos. Para no convertir datos
desconocidos en hechos, la tabla marca **No acreditado** donde falta una
medición. Si se introducen esos valores como `False` de forma conservadora, el
puntaje es **RAG 0, fine-tuning completo 0 y PEFT 0: empate**. Este resultado
no valida ni descarta una técnica; muestra que aún falta evidencia para una
decisión de inversión.

| Pregunta del método | Valor para esta tarea | Evidencia o dato pendiente |
| --- | --- | --- |
| ¿Cambia la información al menos una vez al mes? | No | La categoría depende de la intención de la pregunta; la vigencia de fuentes corresponde al RAG. |
| ¿Fallan al menos 3 de 20 respuestas en formato o tono? | No acreditado (`False` provisional) | Faltan 20 salidas reales del clasificador, revisadas con un criterio único. |
| ¿Hay al menos 200 ejemplos etiquetados y revisados? | No | Este laboratorio prepara 15 pares ficticios, cinco por categoría. |
| ¿Hay máximo dos entrenamientos o se requiere iterar en menos de un día? | No acreditado (`False` provisional) | No hay presupuesto ni plazo de iteración documentados para tuning. |
| ¿Se necesitan dos o más variantes? | No | El flujo actual define un solo clasificador y tres rutas. |

El valor `False` provisional evita inventar un `True`; **no significa que se
haya medido la ausencia de fallos ni que exista presupuesto ilimitado**. Hay
empate a cero, y no se presenta la primera técnica del diccionario como ganadora.

## 3. Técnica elegida y por qué

**PEFT queda elegido como candidato de personalización para este laboratorio**,
porque la mejora buscada sería un patrón de clasificación, no conocimiento
documental. Es una elección cualitativa para preparar datos, no una aprobación
para entrenar o integrar un modelo. El puntaje empatado y la ausencia de una
tasa de fallos impiden afirmar que PEFT ya sea necesario. La decisión operativa
actual es conservar el clasificador por prompt y su normalización, medirlo con
20 preguntas nuevas y comparar primero una salida JSON restringida por esquema.

RAG sigue siendo la técnica del proyecto para recuperar documentos y fuentes;
no reemplaza al clasificador. El fine-tuning completo requeriría justificar más
datos y costo. El soft-prompting no forma parte de la ruta gestionada usada en
este repositorio. La API actual con `GEMINI_API_KEY` no ofrece tuning; para
entrenar habría que evaluar Gemini Enterprise Agent Platform y un modelo
admitido. El dataset de este laboratorio no modifica el flujo de la Unidad 2.3:
sus ejemplos tienen salida JSON y el clasificador integrado aún espera texto de
una palabra.

## 4. Qué se necesitaría para ejecutarla

Se prepararon **15 pares válidos y ficticios**, cinco para cada categoría. El
validador comprueba formato, claves, categorías y duplicados; dos pares rotos
se usan solo para probarlo. El umbral de **200 pares** es un criterio
orientativo del curso, no un mínimo oficial del proveedor. Para llegar a 200
faltan **185 pares**. Un reparto casi uniforme sería 67 `indicador`, 67
`definicion` y 66 `sin_datos`: desde los cinco actuales faltan 62, 62 y 61,
respectivamente.

Antes de cualquier entrenamiento se necesitan además **20 preguntas de
evaluación separadas** de los ejemplos de entrenamiento, 20 salidas reales del
clasificador actual para medir incumplimientos, revisión humana de etiquetas y
casos límite, definición de presupuesto y verificación de acceso a una
plataforma de tuning compatible. La evaluación debe comprobar tanto la
categoría correcta como el formato; obtener JSON válido no demuestra que la
ruta elegida sea correcta. Ningún ejemplo contiene datos institucionales reales.
