"""Extracción y validación local de respuestas del modelo."""

import json
import re
from math import isfinite
from typing import Any

from .errores import ErrorProveedor


def extraer_texto(datos: dict[str, Any]) -> str:
    try:
        texto = datos["candidates"][0]["content"]["parts"][0]["text"]
    except (KeyError, IndexError, TypeError) as error:
        raise ErrorProveedor("La respuesta no contiene texto en el formato esperado.") from error
    if not isinstance(texto, str) or not texto.strip():
        raise ErrorProveedor("La respuesta no contiene texto generado.")
    return texto


def validar_estructura(valor: Any, esquema: dict[str, Any], ruta: str = "respuesta") -> None:
    """Valida la salida, aunque se haya pedido un esquema al proveedor."""
    tipo = esquema["type"]
    if tipo == "OBJECT":
        if not isinstance(valor, dict):
            raise ValueError(f"{ruta} debe ser un objeto.")
        propiedades = esquema["properties"]
        requeridas = set(esquema.get("required", []))
        if not requeridas.issubset(valor) or set(valor) - set(propiedades):
            raise ValueError(f"{ruta} tiene claves faltantes o inesperadas.")
        for clave, dato in valor.items():
            validar_estructura(dato, propiedades[clave], f"{ruta}.{clave}")
    elif tipo == "ARRAY":
        if not isinstance(valor, list):
            raise ValueError(f"{ruta} debe ser una lista.")
        for indice, dato in enumerate(valor):
            validar_estructura(dato, esquema["items"], f"{ruta}[{indice}]")
    elif tipo == "STRING":
        if not isinstance(valor, str):
            raise ValueError(f"{ruta} debe ser texto.")
    elif tipo == "BOOLEAN":
        if not isinstance(valor, bool):
            raise ValueError(f"{ruta} debe ser booleano.")
    elif tipo == "NUMBER":
        if isinstance(valor, bool) or not isinstance(valor, (int, float)) or not isfinite(valor):
            raise ValueError(f"{ruta} debe ser un número finito.")
    else:
        raise ValueError(f"Tipo de esquema no admitido: {tipo}.")
    if "enum" in esquema and valor not in esquema["enum"]:
        raise ValueError(f"{ruta} tiene un valor no permitido.")


def parsear_respuesta_json(texto: str, esquema: dict[str, Any]) -> Any:
    limpio = re.sub(r"^```(?:json)?\s*|\s*```$", "", texto.strip(), flags=re.IGNORECASE)
    try:
        datos = json.loads(limpio)
    except json.JSONDecodeError as error:
        raise ValueError("La respuesta del modelo no es JSON válido.") from error
    validar_estructura(datos, esquema)
    return datos
