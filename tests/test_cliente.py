"""Pruebas de la interfaz pública con transporte y tiempo controlados."""

from unittest.mock import Mock

import pytest

from cliente_gemini.cliente import ClienteGemini
from cliente_gemini.errores import ErrorAutenticacion, ErrorProveedor, ErrorServicioAgotado, ErrorTemporal
from cliente_gemini.reintentos import Reintentador


def test_consulta_normal_registra_una_sola_operacion(configuracion, respuesta_valida):
    transporte = Mock()
    transporte.enviar_peticion.return_value = respuesta_valida
    cliente = ClienteGemini(configuracion, transporte=transporte)

    assert cliente.consultar_modelo("¿Qué es la tasa de aprobación?") == "Respuesta simulada"
    assert len(cliente.registro_costos.operaciones) == 1
    assert cliente.registro_costos.costo_total_sesion == pytest.approx(0.00105)
    transporte.enviar_peticion.assert_called_once()


def test_reintento_exitoso_no_duplica_costo(configuracion, respuesta_valida):
    transporte = Mock()
    transporte.enviar_peticion.side_effect = [ErrorTemporal("429"), respuesta_valida]
    dormir = Mock()
    cliente = ClienteGemini(
        configuracion,
        transporte=transporte,
        reintentador=Reintentador(dormir=dormir, aleatorio=lambda _a, _b: 0),
    )

    assert cliente.consultar_modelo("Pregunta") == "Respuesta simulada"
    assert transporte.enviar_peticion.call_count == 2
    assert len(cliente.registro_costos.operaciones) == 1
    dormir.assert_called_once_with(2)


def test_agotamiento_se_convierte_en_error_publico(configuracion):
    transporte = Mock()
    transporte.enviar_peticion.side_effect = ErrorTemporal("503")
    cliente = ClienteGemini(
        configuracion,
        transporte=transporte,
        reintentador=Reintentador(dormir=Mock()),
    )

    with pytest.raises(ErrorServicioAgotado, match="varios intentos"):
        cliente.consultar_modelo("Pregunta")

    assert transporte.enviar_peticion.call_count == 3
    assert cliente.registro_costos.operaciones == []


def test_autenticacion_se_propaga_sin_reintento(configuracion):
    transporte = Mock()
    transporte.enviar_peticion.side_effect = ErrorAutenticacion("clave inválida")
    cliente = ClienteGemini(configuracion, transporte=transporte)

    with pytest.raises(ErrorAutenticacion):
        cliente.consultar_modelo("Pregunta")

    transporte.enviar_peticion.assert_called_once()


def test_schema_y_system_instruction_llegan_al_transporte(configuracion, respuesta_valida):
    esquema = {"type": "OBJECT", "properties": {"dato": {"type": "STRING"}}, "required": ["dato"]}
    respuesta_valida["candidates"][0]["content"]["parts"][0]["text"] = '{"dato": "válido"}'
    transporte = Mock()
    transporte.enviar_peticion.return_value = respuesta_valida
    cliente = ClienteGemini(configuracion, transporte=transporte)

    assert cliente.consultar_modelo("Pregunta", "Instrucción", esquema) == '{"dato": "válido"}'
    cuerpo = transporte.enviar_peticion.call_args.args[0]
    assert cuerpo["systemInstruction"]["parts"][0]["text"] == "Instrucción"
    assert cuerpo["generationConfig"]["responseSchema"] == esquema


def test_metadata_invalida_falla_con_mensaje_claro(configuracion, respuesta_valida):
    respuesta_valida.pop("usageMetadata")
    transporte = Mock()
    transporte.enviar_peticion.return_value = respuesta_valida

    with pytest.raises(ErrorProveedor, match="usageMetadata"):
        ClienteGemini(configuracion, transporte=transporte).consultar_modelo("Pregunta")
