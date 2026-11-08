# Límites de autonomía del agente académico

## Herramientas y nivel de riesgo

| Herramienta | Nivel | Motivo |
| --- | --- | --- |
| `consultar_indicador` | Bajo, solo lectura | Lee cifras ficticias del catálogo local. |
| `consultar_definicion` | Bajo, solo lectura | Lee una definición ficticia; no altera registros. |
| `calcular_variacion` | Bajo, cálculo local | Resta valores ficticios disponibles; no escribe ni envía acciones. |
| `consultar_fuente` | Bajo, solo lectura | Devuelve el nombre y alcance de una fuente ficticia local. |

Ninguna herramienta puede modificar un expediente, aprobar una decisión, enviar
un mensaje ni mover dinero. Por eso no existe un paso de aprobación humana dentro
de las cuatro funciones actuales. Exigir aprobación para una operación que solo
lee o calcula daría una señal equivocada sobre el riesgo real. Si se incorpora
una herramienta de escritura, se deberá clasificar su efecto y colocar la
aprobación **antes** de ejecutarla, con denegación predeterminada y registro de la
decisión. Esa capacidad no está implementada ni se declara como existente.

## Supervisión de las respuestas

El agente puede decidir qué herramienta consultar, pero sus respuestas solo
pueden presentarse como demostración con datos ficticios. No autoriza decisiones
académicas. Una revisión humana debe comprobar cifras, años, unidad, negaciones,
fuente y si la conclusión coincide con las observaciones antes de usar una
respuesta fuera de la práctica. Los prompts reducen errores, pero no verifican
por sí mismos que el texto final sea fiel a los datos.

## Revisión de trazas

Revisar las tres trazas de la práctica antes de entregar. Durante el desarrollo,
revisar semanalmente una muestra de interacciones y todas las consultas que
informen datos ausentes, repitan herramientas consecutivamente o terminen por
límite de iteraciones. En cada registro comparar entrada, nombres y argumentos
de herramientas, observaciones, respuesta y fuente citada. Una llamada repetida
puede ser legítima; se examinan también sus argumentos antes de tratarla como
fallo.

Las trazas de `evaluaciones/unidad_2_4/` contienen preguntas predeterminadas con
datos ficticios. Si se procesan consultas personales, restringir el acceso y la
retención de esos registros; no incorporarlos automáticamente a una entrega.

## Respuesta ante un comportamiento inesperado

1. Detener la demostración con Gemini si aparece una cifra inventada, una fuente
   no disponible o una secuencia repetitiva sin progreso.
2. Revisar la traza concreta y reproducir la entrada con el catálogo actual.
3. Identificar si el fallo provino del dato, del esquema, de la descripción de
   la herramienta, de la elección del modelo o de la redacción final.
4. Corregir la pieza correspondiente y añadir un caso de regresión cuando el
   fallo pueda comprobarse de forma estable.
5. Volver a ejecutar la prueba local y la consulta afectada; revisar la nueva
   traza antes de reanudar la demostración.

Si en el futuro una herramienta de escritura actuara sin aprobación, desactivarla
de inmediato, revisar todas sus invocaciones y aplicar la política de respuesta
institucional pertinente. El agente actual no dispone de esa clase de acción.
