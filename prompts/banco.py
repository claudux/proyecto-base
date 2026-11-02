"""Banco de prompts académicos con datos y documentos ficticios.

Cada entrada reúne una tarea, una consulta de ejemplo y su contrato JSON.
No se usan datos de ninguna institución real.
"""

BANCO_DE_PROMPTS = [
    {
        "nombre": "explicar_indicador",
        "system_instruction": (
            "Explica el indicador académico usando exclusivamente el contexto "
            "proporcionado. Devuelve solo un objeto JSON, sin Markdown, con "
            "exactamente estas cadenas: indicador, definicion y fuente. "
            "Si la definición o la fuente no está en el contexto, escribe "
            "'no_indicado' en el campo correspondiente. No inventes normas "
            "institucionales ni atribuyas datos ficticios a una institución real."
        ),
        "ejemplo_usuario": (
            "Contexto ficticio: La tasa de aprobación es el porcentaje de "
            "estudiantes aprobados respecto de los evaluados en un período. "
            "Fuente: Reglamento académico ficticio H. "
            "Pregunta: ¿Qué significa la tasa de aprobación según este contexto?"
        ),
        "response_schema": {
            "type": "OBJECT",
            "properties": {
                "indicador": {"type": "STRING"},
                "definicion": {"type": "STRING"},
                "fuente": {"type": "STRING"},
            },
            "required": ["indicador", "definicion", "fuente"],
        },
    },
    {
        "nombre": "extraer_indicador",
        "system_instruction": (
            "Extrae datos académicos únicamente del contexto proporcionado. "
            "Devuelve solo un objeto JSON, sin Markdown, con exactamente estas "
            "claves: indicador (string), periodo (string), valor (string), "
            "unidad (string), fuente (string) y datos_faltantes (lista de strings). "
            "Si un dato no aparece, escribe 'no_indicado' en su campo y "
            "agrégalo a datos_faltantes. Conserva la unidad y no calcules cifras "
            "que el contexto no proporciona."
        ),
        "ejemplo_usuario": (
            "Contexto ficticio: La tasa de aprobación fue 74 % en 2025. "
            "Fuente: Ficha académica ficticia A. "
            "Extrae el indicador, período, valor, unidad y fuente."
        ),
        "response_schema": {
            "type": "OBJECT",
            "properties": {
                "indicador": {"type": "STRING"},
                "periodo": {"type": "STRING"},
                "valor": {"type": "STRING"},
                "unidad": {"type": "STRING"},
                "fuente": {"type": "STRING"},
                "datos_faltantes": {
                    "type": "ARRAY",
                    "items": {"type": "STRING"},
                },
            },
            "required": [
                "indicador", "periodo", "valor", "unidad", "fuente", "datos_faltantes"
            ],
        },
    },
    {
        "nombre": "evaluar_afirmacion_academica",
        "system_instruction": (
            "Evalúa una afirmación académica usando exclusivamente el contexto "
            "proporcionado. Devuelve solo un objeto JSON, sin Markdown, con "
            "exactamente estas claves: evaluacion (respaldada, contradicha o "
            "informacion_insuficiente), justificacion (string) y "
            "requiere_dato_adicional (boolean). Si falta el período, indicador "
            "o documento necesario, indica información insuficiente. Distingue "
            "porcentajes de puntos porcentuales y no inventes cifras."
        ),
        "ejemplo_usuario": (
            "Contexto ficticio: La tasa de aprobación fue 68 % en 2024 y "
            "74 % en 2025. Fuente: Ficha académica ficticia A. "
            "Afirmación: La tasa de aprobación de 2026 fue 80 %."
        ),
        "response_schema": {
            "type": "OBJECT",
            "properties": {
                "evaluacion": {
                    "type": "STRING",
                    "enum": [
                        "respaldada", "contradicha", "informacion_insuficiente"
                    ],
                },
                "justificacion": {"type": "STRING"},
                "requiere_dato_adicional": {"type": "BOOLEAN"},
            },
            "required": [
                "evaluacion", "justificacion", "requiere_dato_adicional"
            ],
        },
    },
]
