"""Casos donde una normalización incorrecta distorsiona la comparación."""

import pytest

from pipeline_texto import limpiar_texto, procesar_texto


def test_conserva_acentos_numeros_y_separa_puntuacion():
    assert procesar_texto("  Aprobación, 2025: 74 %  ") == [
        "aprobación", "2025", "74"
    ]


def test_texto_solo_puntuacion_queda_vacio():
    assert procesar_texto("¡¡¡...!!!") == []


def test_entrada_no_textual_falla_con_mensaje_claro():
    with pytest.raises(TypeError, match="espera str"):
        limpiar_texto(None)
