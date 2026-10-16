import os

import requests
from dotenv import load_dotenv


load_dotenv()


# prepara y valida los datos de la petición, no hace llamadas de red.
def armar_peticion(pregunta):
    if not isinstance(pregunta, str) or not pregunta.strip():
        raise ValueError("La pregunta no puede estar vacía")

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("Falta configurar GEMINI_API_KEY en el archivo .env")

    modelo = os.getenv("GEMINI_MODEL") or "gemini-3.6-flash"
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{modelo}:generateContent"
    body = {"contents": [{"parts": [{"text": pregunta}]}]}
    return url, body, api_key


# envía la petición y convierte fallos de transporte o HTTP en errores claros.
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

    try:
        respuesta.raise_for_status()
    except requests.exceptions.HTTPError as error:
        raise RuntimeError(
            f"El servicio respondió con un error HTTP {respuesta.status_code}."
        ) from error

    try:
        return respuesta.json()
    except requests.exceptions.JSONDecodeError as error:
        raise RuntimeError(
            "La respuesta del servicio no llegó en el formato esperado."
        ) from error


# extrae el texto del JSON, no conoce la clave ni cómo se hizo la petición.
def extraer_texto(datos):
    try:
        texto = datos["candidates"][0]["content"]["parts"][0]["text"]
    except (KeyError, IndexError, TypeError) as error:
        raise RuntimeError(
            "La respuesta no trae el texto generado en el lugar esperado."
        ) from error

    if not texto:
        raise RuntimeError("La respuesta no contiene texto generado.")
    return texto


# coordina las tres responsabilidades anteriores sin repetir su lógica.
def obtener_dato_de_prueba(pregunta):
    url, body, api_key = armar_peticion(pregunta)
    datos = enviar_peticion(url, body, api_key)
    return extraer_texto(datos)


if __name__ == "__main__":
    print(obtener_dato_de_prueba("Confirma en una frase corta que esta conexión funciona"))
