"""Tres consultas del agente; --real usa Gemini y consume cuota de API."""

import argparse
from pathlib import Path

from agente_academico import AgenteAcademico


PREGUNTAS = (
    "¿Cuál fue la tasa de aprobación en 2025?",
    "¿Qué significa la tasa de retención?",
    "¿Cuánto aumentó la tasa de aprobación entre 2024 y 2025 y qué ficha respalda el dato?",
)
PREGUNTAS_MEMORIA = (
    "¿Cómo estuvo la aprobación del año 2025?",
    "¿Y la retención?",
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
    parser.add_argument("--memoria", action="store_true", help="Ejecuta dos preguntas en una misma sesión")
    args = parser.parse_args()
    modo = "gemini" if args.real else "simulado"
    nombre_traza = f"trazas_memoria_{modo}.jsonl" if args.memoria else f"trazas_{modo}.jsonl"
    ruta = Path("evaluaciones/unidad_2_4") / nombre_traza
    agente = AgenteAcademico(crear_modelo(args.real), archivo_trazas=ruta)
    preguntas = PREGUNTAS_MEMORIA if args.memoria else PREGUNTAS
    for numero, pregunta in enumerate(preguntas, start=1):
        session_id = f"memoria-{modo}" if args.memoria else f"ejemplo-{modo}-{numero}"
        resultado = agente.consultar(pregunta, session_id=session_id)
        print(f"\nConsulta {numero}: {pregunta}")
        for accion, observacion in resultado["intermediate_steps"]:
            print(f"  {accion.tool}({accion.tool_input}) -> {observacion}")
        print(f"  Respuesta: {resultado['output']}")
    print(f"\nTrazas: {ruta}")


if __name__ == "__main__":
    main()
