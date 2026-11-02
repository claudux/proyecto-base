"""Consulta académica ficticia con LangChain; --real consume la API Gemini."""

import argparse

from langchain_core.messages import AIMessage
from langchain_core.runnables import RunnableLambda

from orquestacion_academica import construir_cadena, procesar_consulta


PREGUNTA = "¿Cómo cambió la tasa de aprobación entre 2024 y 2025?"
CONTEXTO = (
    "La tasa de aprobación fue 68 % en 2024 y 74 % en 2025. "
    "La tasa se define como estudiantes aprobados divididos por estudiantes "
    "evaluados, multiplicado por 100."
)
FUENTE = "Ficha académica ficticia A"


def modelo_simulado():
    """Respuestas fijas para observar las etapas sin red ni credenciales."""
    def responder(entrada):
        texto = entrada.to_string()
        if "Clasifica la pregunta académica" in texto:
            return AIMessage(content="indicador")
        if "Extrae solo cifras" in texto:
            return AIMessage(content="2024: 68 %; 2025: 74 %.")
        if "Analiza la evidencia" in texto:
            return AIMessage(content="74 - 68 = 6 puntos porcentuales de aumento.")
        if "Revisa el borrador" in texto:
            return AIMessage(content="La tasa de aprobación aumentó 6 puntos porcentuales, de 68 % en 2024 a 74 % en 2025. Fuente: Ficha académica ficticia A. Datos ficticios.")
        return AIMessage(content="La aprobación subió 6 puntos porcentuales. Fuente: Ficha académica ficticia A.")

    return RunnableLambda(responder)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--real", action="store_true", help="Consulta Gemini y consume cuota")
    args = parser.parse_args()
    if args.real:
        from dotenv import load_dotenv
        from langchain_google_genai import ChatGoogleGenerativeAI

        from cliente_gemini.configuracion import Configuracion

        load_dotenv()
        configuracion = Configuracion.desde_entorno()
        modelo = ChatGoogleGenerativeAI(
            model=configuracion.modelo, google_api_key=configuracion.api_key, temperature=0
        )
    else:
        modelo = modelo_simulado()
    print(procesar_consulta(construir_cadena(modelo), PREGUNTA, CONTEXTO, FUENTE))


if __name__ == "__main__":
    main()
