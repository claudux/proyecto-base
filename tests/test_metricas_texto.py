"""Las métricas cuentan tokens, pero no sustituyen la revisión factual."""

import pytest

from metricas_texto import (
    calcular_metricas,
    calcular_metricas_crudas,
    calcular_precision_cobertura_f1,
    contar_coincidencias,
)


def test_coincidencias_respetan_repeticiones():
    assert contar_coincidencias(["el", "gato"], ["el", "gato", "gato"]) == 2
    resultado = calcular_precision_cobertura_f1(
        ["el", "gato"], ["el", "gato", "gato"]
    )
    assert resultado["precision"] == pytest.approx(2 / 3)
    assert resultado["cobertura"] == 1


def test_pipeline_corrige_diferencias_de_formato():
    referencia = "La Aprobación fue 74 %."
    respuesta = "la aprobación fue 74 %"
    assert calcular_metricas_crudas(referencia, respuesta)["f1"] < 1
    assert calcular_metricas(referencia, respuesta)["f1"] == 1


def test_texto_vacio_no_produce_division_por_cero():
    assert calcular_metricas("¡¡¡...!!!", "respuesta") == {
        "precision": 0.0, "cobertura": 0.0, "f1": 0.0
    }


def test_una_negacion_ausente_puede_tener_f1_alto():
    referencia = "La tasa no incluye convalidaciones."
    respuesta = "La tasa incluye convalidaciones."
    assert calcular_metricas(referencia, respuesta)["f1"] > 0.8
