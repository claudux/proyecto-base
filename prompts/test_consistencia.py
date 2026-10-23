"""Prueba cada prompt tres veces contra Gemini y guarda los resultados reales.

Ejecutar desde la raíz del proyecto: python -m prompts.test_consistencia
"""

import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path

from prompts.banco import BANCO_DE_PROMPTS
from src.consumir_gemini import (
    MODELO_PREDETERMINADO,
    armar_peticion,
    enviar_peticion,
    extraer_texto,
    parsear_respuesta_json,
)


REPETICIONES = 3
PAUSA_SEGUNDOS = 2
RUTA_REGISTRO = Path(__file__).with_name("registro_resultados.json")


def probar_banco():
    """Cuenta solo las respuestas que cumplen el esquema de su prompt."""
    registro = {
        "fecha_utc": datetime.now(timezone.utc).isoformat(),
        "modelo": os.getenv("GEMINI_MODEL") or MODELO_PREDETERMINADO,
        "repeticiones_por_prompt": REPETICIONES,
        "resultados": {},
    }

    for indice_prompt, prompt in enumerate(BANCO_DE_PROMPTS):
        fallos = []
        exitos = 0
        for intento in range(1, REPETICIONES + 1):
            if indice_prompt or intento > 1:
                time.sleep(PAUSA_SEGUNDOS)
            try:
                url, body, api_key = armar_peticion(
                    prompt["ejemplo_usuario"],
                    prompt["system_instruction"],
                    prompt["response_schema"],
                )
                respuesta = enviar_peticion(url, body, api_key)
                texto = extraer_texto(respuesta)
                parsear_respuesta_json(texto, prompt["response_schema"])
                exitos += 1
            except (RuntimeError, ValueError) as error:
                fallos.append({"intento": intento, "motivo": str(error)})
                print(f"  {prompt['nombre']}, intento {intento}: {error}")

        registro["resultados"][prompt["nombre"]] = {
            "exitos": exitos,
            "fallos": len(fallos),
            "intentos": REPETICIONES,
            "detalle_fallos": fallos,
        }
        print(f"{prompt['nombre']}: {exitos}/{REPETICIONES} respuestas válidas")

    RUTA_REGISTRO.write_text(
        json.dumps(registro, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Registro guardado en {RUTA_REGISTRO}")
    return registro


if __name__ == "__main__":
    probar_banco()
