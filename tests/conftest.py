"""Datos mínimos comunes; ninguna prueba necesita una credencial real."""

import shutil
import tempfile
from pathlib import Path

import pytest

from cliente_gemini.configuracion import Configuracion


@pytest.fixture
def carpeta_temporal():
    """Carpeta única en el proyecto; evita perfiles temporales sin acceso.

    La limpieza es de esfuerzo razonable y nunca oculta un fallo de la prueba.
    """
    raiz = Path(__file__).resolve().parents[1]
    ruta = Path(tempfile.mkdtemp(prefix=".rag-test-", dir=raiz))
    try:
        yield ruta
    finally:
        shutil.rmtree(ruta, ignore_errors=True)


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
