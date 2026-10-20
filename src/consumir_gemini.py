import os
import time
from math import isfinite

import requests
from dotenv import load_dotenv


load_dotenv()
# Consideraciones
# Precios estándar de Gemini 3.6 Flash en USD por token.
# Corresponden a USD 0.75 / 1M tokens de entrada y USD 3.75 / 1M de salida.
# Si se cambia el modelo o el proveedor, estos precios deben actualizarse.
PRECIO_ENTRADA_POR_TOKEN = 0.75 / 1_000_000
PRECIO_SALIDA_POR_TOKEN = 3.75 / 1_000_000


# Prepara y valida los datos de la petición, sin hacer llamadas de red.
def armar_peticion(pregunta):
    # Valida que la pregunta no esté vacía y que la clave de API esté configurada.
    if not isinstance(pregunta, str) or not pregunta.strip():
        raise ValueError("La pregunta no puede estar vacía.")

    api_key = os.getenv("GEMINI_API_KEY")
    # Valida que la clave de API esté configurada en el archivo .env.
    if not api_key:
        raise RuntimeError("Falta configurar GEMINI_API_KEY en el archivo .env.")
    # Valida que la clave de API tenga un formato básico esperado.
    if not isinstance(api_key, str) or not api_key.strip():
        raise ValueError("La clave de API no tiene un formato válido.")

    modelo = os.getenv("GEMINI_MODEL") or "gemini-3.6-flash"
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

# Función principal para ejecutar el script de prueba
if __name__ == "__main__":

    pregunta = (
        "Calcula el doble de (4 * 5). "
        "Responde únicamente con el resultado numérico."
    )

    modelos = {
        "gemini-3.5-flash-lite": {
            "entrada": 0.30 / 1_000_000,
            "salida": 2.50 / 1_000_000,
        },
        "gemini-3.6-flash": {
            "entrada": 0.75 / 1_000_000,
            "salida": 3.75 / 1_000_000,
        },
    }

    repeticiones = 4

    for modelo, precios in modelos.items():

        # Cambia el modelo solo durante la ejecución
        os.environ["GEMINI_MODEL"] = modelo

        latencias = []
        costos = []
        correctas = 0

        print(f"\n{'=' * 45}")
        print(f"MODELO: {modelo}")
        print(f"{'=' * 45}")

        for i in range(repeticiones):

            try:
                url, body, api_key = armar_peticion(pregunta)

                inicio = time.perf_counter()
                datos = enviar_peticion(url, body, api_key)
                latencia = time.perf_counter() - inicio

                texto = extraer_texto(datos).strip()
                tokens = extraer_uso_de_tokens(datos)

                costo = calcular_costo(
                    datos,
                    precios["entrada"],
                    precios["salida"],
                )

                latencias.append(latencia)
                costos.append(costo)

                if texto == "40":
                    correctas += 1

                print(f"\nIntento {i + 1}")
                print(f"Respuesta: {texto}")
                print(f"Latencia: {latencia:.2f} segundos")
                print(f"Tokens totales: {tokens['total']}")
                print(f"Costo estimado: USD {costo:.8f}")

            except (RuntimeError, ValueError) as error:
                print(f"\nIntento {i + 1}: ERROR - {error}")

        if latencias:
            promedio = sum(latencias) / len(latencias)
            costo_total = sum(costos)

            print("\n--- RESUMEN ---")
            print(f"Modelo: {modelo}")
            print(f"Pruebas exitosas: {len(latencias)}")
            print(f"Respuestas correctas: {correctas}")
            print(f"Latencia promedio: {promedio:.2f} segundos")
            print(f"Costo total estimado: USD {costo_total:.8f}")
        else:
            print("\nNo hubo pruebas exitosas.")
