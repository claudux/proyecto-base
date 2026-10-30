"""Demuestra el cliente con datos académicos ficticios y una respuesta simulada.

No consulta Gemini ni necesita una credencial real. La respuesta del proveedor
se reemplaza por un Mock; el cliente conserva su flujo normal de validación y
registro de costo estimado.
"""

import json
from unittest.mock import Mock

from cliente_gemini import ClienteGemini, Configuracion


def main() -> None:
    datos_ficticios = {
        "periodo_inicial": 2024,
        "tasa_inicial": 68,
        "periodo_final": 2025,
        "tasa_final": 74,
        "fuente": "Ficha de indicadores académicos de ejemplo (ficticia)",
        "definicion": (
            "Estudiantes que aprobaron divididos por estudiantes evaluados, "
            "multiplicado por 100."
        ),
    }
    pregunta = (
        "Con estos datos ficticios, ¿cómo cambió la tasa de aprobación entre "
        f"{datos_ficticios['periodo_inicial']} ({datos_ficticios['tasa_inicial']} %) "
        f"y {datos_ficticios['periodo_final']} ({datos_ficticios['tasa_final']} %)? "
        f"Fuente: {datos_ficticios['fuente']}. "
        f"Definición del indicador: {datos_ficticios['definicion']}"
    )
    esquema = {
        "type": "OBJECT",
        "properties": {
            "periodo_inicial": {"type": "NUMBER"},
            "periodo_final": {"type": "NUMBER"},
            "tasa_inicial": {"type": "NUMBER"},
            "tasa_final": {"type": "NUMBER"},
            "variacion_puntos_porcentuales": {"type": "NUMBER"},
            "fuente": {"type": "STRING"},
            "definicion": {"type": "STRING"},
            "limitacion": {"type": "STRING"},
        },
        "required": [
            "periodo_inicial",
            "periodo_final",
            "tasa_inicial",
            "tasa_final",
            "variacion_puntos_porcentuales",
            "fuente",
            "definicion",
            "limitacion",
        ],
    }
    resultado_simulado = {
        **datos_ficticios,
        "variacion_puntos_porcentuales": (
            datos_ficticios["tasa_final"] - datos_ficticios["tasa_inicial"]
        ),
        "limitacion": (
            "Estos datos y esta fuente son ficticios; no describen a una institución real."
        ),
    }
    respuesta_simulada = {
        "candidates": [
            {
                "content": {
                    "parts": [
                        {"text": json.dumps(resultado_simulado, ensure_ascii=False)}
                    ]
                }
            }
        ],
        "usageMetadata": {
            "promptTokenCount": 120,
            "candidatesTokenCount": 60,
            "thoughtsTokenCount": 0,
            "totalTokenCount": 180,
        },
    }

    transporte_simulado = Mock()
    transporte_simulado.enviar_peticion.return_value = respuesta_simulada
    cliente = ClienteGemini(
        Configuracion(api_key="clave_falsa_para_ejemplo"),
        transporte=transporte_simulado,
    )
    texto = cliente.consultar_modelo(
        pregunta,
        system_instruction=(
            "Responde solo con los datos proporcionados. Indica la fuente, "
            "la definición del indicador y los límites de la información."
        ),
        response_schema=esquema,
    )

    print("Ejemplo académico con datos y respuesta simulados")
    print(json.dumps(json.loads(texto), ensure_ascii=False, indent=2))
    print(
        "Costo estimado con tokens simulados: "
        f"USD {cliente.registro_costos.costo_total_sesion:.8f}"
    )


if __name__ == "__main__":
    main()
