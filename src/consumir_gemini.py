import json
import os
import re
import time
from math import isfinite

import requests
from dotenv import load_dotenv


load_dotenv()
# Modelo y precios elegidos en docs/decision-arquitectura.md.
# Si GEMINI_MODEL cambia, también deben revisarse estos precios.
MODELO_PREDETERMINADO = "gemini-3.5-flash-lite"
PRECIO_ENTRADA_POR_TOKEN = 0.30 / 1_000_000
PRECIO_SALIDA_POR_TOKEN = 2.50 / 1_000_000


# Prepara y valida los datos de la petición, sin hacer llamadas de red.
def armar_peticion(pregunta, system_instruction=None, response_schema=None):
    # Valida que la pregunta no esté vacía y que la clave de API esté configurada.
    if not isinstance(pregunta, str) or not pregunta.strip():
        raise ValueError("La pregunta no puede estar vacía.")
    if system_instruction is not None and (
        not isinstance(system_instruction, str) or not system_instruction.strip()
    ):
        raise ValueError("La instrucción de sistema no puede estar vacía.")
    if response_schema is not None and not isinstance(response_schema, dict):
        raise ValueError("El esquema de respuesta debe ser un diccionario.")

    api_key = os.getenv("GEMINI_API_KEY")
    # Valida que la clave de API esté configurada en el archivo .env.
    if not api_key:
        raise RuntimeError("Falta configurar GEMINI_API_KEY en el archivo .env.")
    # Valida que la clave de API tenga un formato básico esperado.
    if not isinstance(api_key, str) or not api_key.strip():
        raise ValueError("La clave de API no tiene un formato válido.")

    modelo = os.getenv("GEMINI_MODEL") or MODELO_PREDETERMINADO
    url = (
        f"https://generativelanguage.googleapis.com/"
        f"v1beta/models/{modelo}:generateContent"
    )
    body = {
        "contents": [
            {
                "parts": [
                    {
                        "text": pregunta,
                    }
                ]
            }
        ]
    }
    if system_instruction is not None:
        body["systemInstruction"] = {"parts": [{"text": system_instruction}]}
    if response_schema is not None:
        body["generationConfig"] = {
            "responseMimeType": "application/json",
            "responseSchema": response_schema,
        }

    return url, body, api_key


# Envía la petición y transforma fallos de red, HTTP o JSON en errores claros.
def enviar_peticion(url, body, api_key):
    try:
        respuesta = requests.post(
            url,
            json=body,
            headers={"x-goog-api-key": api_key},
            timeout=30,
        )
    except requests.exceptions.RequestException as error:
        raise RuntimeError(
            "No se pudo conectar con el servicio. Intenta de nuevo en unos segundos."
        ) from error
    # Valida que la respuesta HTTP sea exitosa y que el contenido sea JSON.
    try:
        respuesta.raise_for_status()
    except requests.exceptions.HTTPError as error:
        raise RuntimeError(
            f"El servicio respondió con un error HTTP {respuesta.status_code}."
        ) from error
    #
    try:
        return respuesta.json()
    except requests.exceptions.JSONDecodeError as error:
        raise RuntimeError(
            "La respuesta del servicio no llegó en el formato esperado."
        ) from error


# Extrae el texto generado desde la respuesta JSON.
def extraer_texto(datos):
    # Valida que la respuesta contenga el texto generado en la estructura esperada.
    try:
        texto = datos["candidates"][0]["content"]["parts"][0]["text"]
    except (KeyError, IndexError, TypeError) as error:
        raise RuntimeError(
            "La respuesta no trae el texto generado en el lugar esperado."
        ) from error
    
    if not texto:
        raise RuntimeError("La respuesta no contiene texto generado.")

    return texto


def validar_estructura(valor, esquema, ruta="respuesta"):
    """Valida los datos recibidos; el esquema de la API no sustituye esta revisión."""
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


def parsear_respuesta_json(texto, esquema):
    """Acepta JSON puro o un único bloque Markdown y verifica su estructura."""
    if not isinstance(texto, str):
        raise ValueError("La respuesta debe ser texto.")
    limpio = re.sub(r"^```(?:json)?\s*|\s*```$", "", texto.strip(), flags=re.IGNORECASE)
    try:
        datos = json.loads(limpio)
    except json.JSONDecodeError as error:
        raise ValueError("La respuesta del modelo no es JSON válido.") from error
    validar_estructura(datos, esquema)
    return datos


# Extrae los tokens usados en la misma petición real.
def extraer_uso_de_tokens(datos):
    try:
        uso = datos["usageMetadata"]
        # Almacena los conteos de tokens en variables separadas para mayor claridad.
        tokens_entrada = uso["promptTokenCount"]
        tokens_salida = uso["candidatesTokenCount"]
        tokens_razonamiento = uso.get("thoughtsTokenCount", 0)
        tokens_totales = uso["totalTokenCount"]
    except (KeyError, TypeError) as error:
        raise RuntimeError(
            "La respuesta no trae los metadatos de uso de tokens esperados."
        ) from error
    # Almacena los conteos en un diccionario para su posterior uso.
    conteos = {
        "entrada": tokens_entrada,
        "salida": tokens_salida,
        "razonamiento": tokens_razonamiento,
        "total": tokens_totales,
    }

    if any(
        not isinstance(valor, int) or isinstance(valor, bool) or valor < 0
        for valor in conteos.values()
    ):
        raise RuntimeError("Los metadatos de tokens contienen valores inválidos.")

    return conteos


# Calcula el costo usando los tokens reales devueltos por Gemini.
def calcular_costo(datos, precio_entrada, precio_salida):
    # Valida que los precios por token sean números no negativos.
    if not all(
        isfinite(precio) and precio >= 0
        for precio in (precio_entrada, precio_salida)
    ):
        raise ValueError("Los precios por token deben ser números no negativos.")

    tokens = extraer_uso_de_tokens(datos)

    tokens_de_salida = (
        tokens["salida"] + tokens["razonamiento"]
    )

    return (
        tokens["entrada"] * precio_entrada
        + tokens_de_salida * precio_salida
    )


# Función coordinadora para obtener solo el texto.
def obtener_dato_de_prueba(pregunta):
    url, body, api_key = armar_peticion(pregunta)
    datos = enviar_peticion(url, body, api_key)
    return extraer_texto(datos)

# Ejemplo manual: la prueba de consistencia está en prompts/test_consistencia.py.
if __name__ == "__main__":
    pregunta = "¿Qué es El Niño? Responde en dos oraciones."
    try:
        url, body, api_key = armar_peticion(pregunta)
        inicio = time.perf_counter()
        datos = enviar_peticion(url, body, api_key)
        print(extraer_texto(datos))
        print(f"Latencia: {time.perf_counter() - inicio:.2f} segundos")
        print(
            "Costo estimado: USD "
            f"{calcular_costo(datos, PRECIO_ENTRADA_POR_TOKEN, PRECIO_SALIDA_POR_TOKEN):.8f}"
        )
    except (RuntimeError, ValueError) as error:
        raise SystemExit(f"Error: {error}") from error
