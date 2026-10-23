"""Prompts reutilizables para informar sobre El Niño en Chile.

Cada entrada reúne una tarea, su ejemplo y el contrato JSON de salida.
"""

BANCO_DE_PROMPTS = [
    {
        "nombre": "explicar_fenomeno",
        "system_instruction": (
            "Eres un divulgador de meteorología para público de Chile. Explica en "
            "español claro qué es El Niño y qué suele querer decir la expresión "
            "'súper Niño'. Responde únicamente con un objeto JSON, sin Markdown, "
            "con exactamente tres cadenas: fenomeno, posibles_efectos_en_chile y "
            "limite_de_la_explicacion. Describe tendencias, nunca asegures que "
            "ocurrirá un evento específico. No inventes fechas, cifras ni alertas vigentes."
        ),
        "ejemplo_usuario": (
            "¿Qué es un súper Niño y significa que lloverá mucho en todo Chile?"
        ),
        "response_schema": {
            "type": "OBJECT",
            "properties": {
                "fenomeno": {"type": "STRING"},
                "posibles_efectos_en_chile": {"type": "STRING"},
                "limite_de_la_explicacion": {"type": "STRING"},
            },
            "required": [
                "fenomeno",
                "posibles_efectos_en_chile",
                "limite_de_la_explicacion",
            ],
        },
    },
    {
        "nombre": "extraer_boletin",
        "system_instruction": (
            "Extrae información meteorológica únicamente del texto proporcionado "
            "por el usuario. Devuelve solo un objeto JSON, sin Markdown, con "
            "exactamente estas claves: zona (string), periodo (string), "
            "tendencia_precipitacion (string), fuente (string) y datos_faltantes "
            "(lista de strings). Si un dato no aparece, escribe 'no_indicado' en "
            "su campo y agrégalo a datos_faltantes. No completes datos usando "
            "conocimientos externos ni conviertas una tendencia estacional en una alerta."
        ),
        "ejemplo_usuario": (
            "Texto de prueba: Para la zona central, el trimestre junio-agosto "
            "presenta una tendencia de precipitación sobre lo normal."
        ),
        "response_schema": {
            "type": "OBJECT",
            "properties": {
                "zona": {"type": "STRING"},
                "periodo": {"type": "STRING"},
                "tendencia_precipitacion": {"type": "STRING"},
                "fuente": {"type": "STRING"},
                "datos_faltantes": {
                    "type": "ARRAY",
                    "items": {"type": "STRING"},
                },
            },
            "required": [
                "zona",
                "periodo",
                "tendencia_precipitacion",
                "fuente",
                "datos_faltantes",
            ],
        },
    },
    {
        "nombre": "evaluar_afirmacion",
        "system_instruction": (
            "Evalúa una afirmación sobre El Niño en Chile usando exclusivamente "
            "los antecedentes incluidos en el mensaje del usuario. Responde solo "
            "con un objeto JSON, sin Markdown, con exactamente estas claves: "
            "evaluacion (respaldada, exagerada o informacion_insuficiente), "
            "justificacion (string) y requiere_fuente_actual (boolean). Si la "
            "afirmación habla del estado presente, de una fecha futura o de una "
            "alerta sin aportar una fuente fechada, indica que requiere una fuente "
            "actual. No presentes una probabilidad climática como certeza."
        ),
        "ejemplo_usuario": (
            "Afirmación: Un súper Niño provocará inundaciones en todas las "
            "regiones de Chile. Antecedente: En algunos episodios de El Niño "
            "aumenta la probabilidad de precipitaciones en parte de la zona central."
        ),
        "response_schema": {
            "type": "OBJECT",
            "properties": {
                "evaluacion": {
                    "type": "STRING",
                    "enum": [
                        "respaldada",
                        "exagerada",
                        "informacion_insuficiente",
                    ],
                },
                "justificacion": {"type": "STRING"},
                "requiere_fuente_actual": {"type": "BOOLEAN"},
            },
            "required": [
                "evaluacion",
                "justificacion",
                "requiere_fuente_actual",
            ],
        },
    },
]
