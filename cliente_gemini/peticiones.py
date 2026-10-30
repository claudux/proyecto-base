"""Construcción y validación del contrato de entrada de Gemini."""

from typing import Any


def armar_peticion(
    pregunta: str,
    system_instruction: str | None = None,
    response_schema: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if not isinstance(pregunta, str) or not pregunta.strip():
        raise ValueError("La pregunta no puede estar vacía.")
    if system_instruction is not None and (
        not isinstance(system_instruction, str) or not system_instruction.strip()
    ):
        raise ValueError("La instrucción de sistema no puede estar vacía.")
    if response_schema is not None and not isinstance(response_schema, dict):
        raise ValueError("El esquema de respuesta debe ser un diccionario.")

    cuerpo: dict[str, Any] = {"contents": [{"parts": [{"text": pregunta}]}]}
    if system_instruction is not None:
        cuerpo["systemInstruction"] = {"parts": [{"text": system_instruction}]}
    if response_schema is not None:
        cuerpo["generationConfig"] = {
            "responseMimeType": "application/json",
            "responseSchema": response_schema,
        }
    return cuerpo
