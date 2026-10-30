"""El costo se calcula a partir de usageMetadata y se aísla por instancia."""

import pytest

from cliente_gemini.configuracion import Tarifas
from cliente_gemini.costos import RegistroCostos
from cliente_gemini.errores import ErrorProveedor


def test_registra_precio_de_entrada_salida_y_razonamiento(respuesta_valida):
    registro = RegistroCostos(Tarifas(0.30, 2.50))

    primera = registro.registrar(respuesta_valida)
    segunda = registro.registrar(respuesta_valida)

    assert primera.usd_estimados == pytest.approx(0.00105)
    assert segunda.usd_estimados == pytest.approx(primera.usd_estimados)
    assert registro.costo_total_sesion == pytest.approx(0.00210)
    assert registro.ultima_operacion is segunda


def test_registros_de_distintos_clientes_no_comparten_total(respuesta_valida):
    primero = RegistroCostos(Tarifas())
    segundo = RegistroCostos(Tarifas())

    primero.registrar(respuesta_valida)

    assert primero.costo_total_sesion > 0
    assert segundo.costo_total_sesion == 0


def test_metadata_ausente_no_se_cuenta_como_costo_cero():
    registro = RegistroCostos(Tarifas())

    with pytest.raises(ErrorProveedor, match="usageMetadata"):
        registro.registrar({"candidates": []})

    assert registro.operaciones == []
