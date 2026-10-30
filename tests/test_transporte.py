"""La frontera HTTP se prueba mediante una sesión inyectada y respuestas falsas."""

from unittest.mock import Mock

import pytest
import requests

from cliente_gemini.errores import ErrorAutenticacion, ErrorProveedor, ErrorTemporal
from cliente_gemini.transporte import TransporteGemini


def respuesta_http(estado: int, datos: dict | None = None, retry_after: str | None = None) -> Mock:
    respuesta = Mock(spec=requests.Response)
    respuesta.status_code = estado
    respuesta.headers = {"Retry-After": retry_after} if retry_after is not None else {}
    respuesta.json.return_value = datos if datos is not None else {"ok": True}
    return respuesta


@pytest.mark.parametrize("estado", [401, 403])
def test_credencial_invalida_no_es_temporal(configuracion, estado):
    sesion = Mock()
    sesion.post.return_value = respuesta_http(estado)

    with pytest.raises(ErrorAutenticacion, match="Credencial inválida"):
        TransporteGemini(configuracion, sesion).enviar_peticion({"contents": []})

    sesion.post.assert_called_once()


def test_429_conserva_retry_after(configuracion):
    sesion = Mock()
    sesion.post.return_value = respuesta_http(429, retry_after="7")

    with pytest.raises(ErrorTemporal) as captura:
        TransporteGemini(configuracion, sesion).enviar_peticion({})

    assert captura.value.retry_after == 7


@pytest.mark.parametrize("estado", [500, 503])
def test_error_del_proveedor_es_temporal(configuracion, estado):
    sesion = Mock()
    sesion.post.return_value = respuesta_http(estado)

    with pytest.raises(ErrorTemporal):
        TransporteGemini(configuracion, sesion).enviar_peticion({})


@pytest.mark.parametrize("error", [requests.exceptions.Timeout(), requests.exceptions.ConnectionError()])
def test_timeout_y_conexion_son_temporales(configuracion, error):
    sesion = Mock()
    sesion.post.side_effect = error

    with pytest.raises(ErrorTemporal):
        TransporteGemini(configuracion, sesion).enviar_peticion({})


def test_400_no_se_reintenta(configuracion):
    sesion = Mock()
    sesion.post.return_value = respuesta_http(400)

    with pytest.raises(ErrorProveedor, match="HTTP 400"):
        TransporteGemini(configuracion, sesion).enviar_peticion({})


def test_exito_devuelve_json_y_envia_clave_por_cabecera(configuracion):
    sesion = Mock()
    sesion.post.return_value = respuesta_http(200, {"respuesta": "ok"})
    transporte = TransporteGemini(configuracion, sesion)

    assert transporte.enviar_peticion({"contents": []}) == {"respuesta": "ok"}
    argumentos, opciones = sesion.post.call_args
    assert "clave_falsa_para_pruebas" not in argumentos[0]
    assert opciones["headers"] == {"x-goog-api-key": "clave_falsa_para_pruebas"}
    assert opciones["timeout"] == 30


def test_json_invalido_se_informa_sin_reintento(configuracion):
    sesion = Mock()
    sesion.post.return_value = respuesta_http(200)
    sesion.post.return_value.json.side_effect = ValueError("JSON inválido")

    with pytest.raises(ErrorProveedor, match="JSON válido"):
        TransporteGemini(configuracion, sesion).enviar_peticion({})
