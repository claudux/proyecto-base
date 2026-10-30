"""Datos mínimos comunes; ninguna prueba necesita una credencial real."""

import pytest

from cliente_gemini.configuracion import Configuracion


@pytest.fixture
def configuracion() -> Configuracion:
    return Configuracion(api_key="clave_falsa_para_pruebas")


@pytest.fixture
def respuesta_valida() -> dict:
    return {
        "candidates": [{"content": {"parts": [{"text": "Respuesta simulada"}]}}],
        "usageMetadata": {
            "promptTokenCount": 1000,
            "candidatesTokenCount": 200,
            "thoughtsTokenCount": 100,
            "totalTokenCount": 1300,
        },
    }
