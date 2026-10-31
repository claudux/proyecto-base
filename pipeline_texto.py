"""Normalización sencilla de texto español para evaluación léxica."""

import re


def limpiar_texto(texto: str) -> str:
    """Pasa a minúsculas, separa puntuación y normaliza espacios."""
    if not isinstance(texto, str):
        raise TypeError(f"limpiar_texto espera str, no {type(texto).__name__}")
    texto = re.sub(r"[^\w\s]", " ", texto.lower())
    return re.sub(r"\s+", " ", texto).strip()


def tokenizar(texto_limpio: str) -> list[str]:
    """Separa por espacios un texto ya normalizado."""
    if not isinstance(texto_limpio, str):
        raise TypeError("tokenizar espera str")
    return texto_limpio.split()


def procesar_texto(texto: str) -> list[str]:
    """Aplica la misma preparación a referencia y respuesta."""
    return tokenizar(limpiar_texto(texto))
