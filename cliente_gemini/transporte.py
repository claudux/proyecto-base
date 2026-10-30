"""Único punto que conoce requests y los códigos HTTP del proveedor."""

from typing import Any, Protocol

import requests

from .configuracion import Configuracion
from .errores import ErrorAutenticacion, ErrorProveedor, ErrorTemporal


class SesionHTTP(Protocol):
    """Contrato mínimo para inyectar una sesión falsa en pruebas."""

    def post(self, url: str, **kwargs: Any) -> requests.Response: ...


def _retry_after_segundos(valor: str | None) -> float | None:
    # El encabezado admite también fechas HTTP; esta versión interpreta segundos.
    if valor is None:
        return None
    try:
        segundos = float(valor)
    except ValueError:
        return None
    return segundos if 0 <= segundos < float("inf") else None


class TransporteGemini:
    def __init__(self, configuracion: Configuracion, sesion: SesionHTTP | None = None) -> None:
        self._configuracion = configuracion
        self._sesion = sesion if sesion is not None else requests.Session()

    def enviar_peticion(self, cuerpo: dict[str, Any]) -> dict[str, Any]:
        url = (
            "https://generativelanguage.googleapis.com/v1beta/models/"
            f"{self._configuracion.modelo}:generateContent"
        )
        try:
            respuesta = self._sesion.post(
                url,
                json=cuerpo,
                headers={"x-goog-api-key": self._configuracion.api_key},
                timeout=self._configuracion.timeout_segundos,
            )
        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as error:
            raise ErrorTemporal("No se pudo contactar al proveedor.") from error
        except requests.exceptions.RequestException as error:
            raise ErrorProveedor("Falló la petición al proveedor.") from error

        estado = respuesta.status_code
        if estado in (401, 403):
            raise ErrorAutenticacion("Credencial inválida o sin permiso. Revisa GEMINI_API_KEY.")
        if estado == 429:
            raise ErrorTemporal(
                "Límite de uso alcanzado.",
                retry_after=_retry_after_segundos(respuesta.headers.get("Retry-After")),
            )
        if estado >= 500:
            raise ErrorTemporal(f"El proveedor respondió HTTP {estado}.")
        if estado >= 400:
            raise ErrorProveedor(f"El proveedor rechazó la petición con HTTP {estado}.")

        try:
            datos = respuesta.json()
        except ValueError as error:
            raise ErrorProveedor("La respuesta del proveedor no es JSON válido.") from error
        if not isinstance(datos, dict):
            raise ErrorProveedor("La respuesta del proveedor debe ser un objeto JSON.")
        return datos
