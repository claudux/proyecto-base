"""Tres consultas del agente; --real usa Gemini y consume cuota de API."""

import argparse
from pathlib import Path

from agente_academico import AgenteAcademico


PREGUNTAS = (
    "¿Cuál fue la tasa de aprobación en 2025?",
    "¿Qué significa la tasa de retención?",
    "¿Cuánto aumentó la tasa de aprobación entre 2024 y 2025 y qué ficha respalda el dato?",
)


def crear_modelo(real: bool):
    if not real:
        from modelo_agente_simulado import ModeloAgenteSimulado

        return ModeloAgenteSimulado()

    from langchain_google_genai import ChatGoogleGenerativeAI

    from cliente_gemini.configuracion import Configuracion

    config = Configuracion.desde_entorno()
    return ChatGoogleGenerativeAI(
        model=config.modelo, google_api_key=config.api_key
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--real", action="store_true", help="Usa Gemini y consume cuota de API")
    args = parser.parse_args()
    modo = "gemini" if args.real else "simulado"
    ruta = Path("evaluaciones/unidad_2_4") / f"trazas_{modo}.jsonl"
    agente = AgenteAcademico(crear_modelo(args.real), archivo_trazas=ruta)
    for numero, pregunta in enumerate(PREGUNTAS, start=1):
        resultado = agente.consultar(pregunta, session_id=f"ejemplo-{modo}-{numero}")
        print(f"\nConsulta {numero}: {pregunta}")
        for accion, observacion in resultado["intermediate_steps"]:
            print(f"  {accion.tool}({accion.tool_input}) -> {observacion}")
        print(f"  Respuesta: {resultado['output']}")
    print(f"\nTrazas: {ruta}")


if __name__ == "__main__":
    main()
