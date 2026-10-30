"""Las esperas se capturan con un mock y nunca bloquean las pruebas."""

from unittest.mock import Mock

import pytest

from cliente_gemini.errores import ErrorAutenticacion, ErrorTemporal
from cliente_gemini.reintentos import PoliticaReintentos, Reintentador


def test_reintenta_dos_veces_y_devuelve_el_resultado():
    operacion = Mock(side_effect=[ErrorTemporal("429"), ErrorTemporal("503"), "ok"])
    dormir = Mock()
    reintentador = Reintentador(dormir=dormir, aleatorio=lambda _a, _b: 0)

    assert reintentador.ejecutar(operacion) == "ok"
    assert operacion.call_count == 3
    assert [llamada.args[0] for llamada in dormir.call_args_list] == [2, 4]


def test_no_reintenta_errores_de_autenticacion():
    operacion = Mock(side_effect=ErrorAutenticacion("sin permiso"))
    dormir = Mock()

    with pytest.raises(ErrorAutenticacion):
        Reintentador(dormir=dormir).ejecutar(operacion)

    operacion.assert_called_once()
    dormir.assert_not_called()


def test_agotamiento_propaga_el_mismo_error():
    error = ErrorTemporal("sigue limitado")
    operacion = Mock(side_effect=error)
    dormir = Mock()

    with pytest.raises(ErrorTemporal) as captura:
        Reintentador(dormir=dormir, aleatorio=lambda _a, _b: 0).ejecutar(operacion)

    assert captura.value is error
    assert operacion.call_count == 3
    assert dormir.call_count == 2


def test_retry_after_tiene_prioridad():
    operacion = Mock(side_effect=[ErrorTemporal("429", retry_after=8), "ok"])
    dormir = Mock()

    assert Reintentador(dormir=dormir, aleatorio=lambda _a, _b: 0).ejecutar(operacion) == "ok"
    dormir.assert_called_once_with(8)


def test_el_techo_incluye_el_jitter():
    politica = PoliticaReintentos(intentos=2, espera_base=2, espera_maxima=2, jitter_proporcion=0.5)
    dormir = Mock()
    operacion = Mock(side_effect=[ErrorTemporal("503"), "ok"])

    Reintentador(politica, dormir=dormir, aleatorio=lambda _a, limite: limite).ejecutar(operacion)

    dormir.assert_called_once_with(2)
