"""Pruebas del contrato de herramientas y del ciclo completo sin red."""

import json

import pytest
from pydantic import ValidationError

from agente_academico import AgenteAcademico, _texto_respuesta
from herramientas_academicas import (
    calcular_variacion,
    consultar_definicion,
    consultar_fuente,
    consultar_indicador,
)
from modelo_agente_simulado import ModeloAgenteSimulado


def test_herramientas_consultan_el_mismo_catalogo_y_reconocen_ausencias():
    assert "74 %" in consultar_indicador.invoke({"indicador": "Aprobación", "periodo": 2025})
    assert "convalidaciones" in consultar_definicion.invoke({"indicador": "aprobación"})
    assert "ficticia" in consultar_fuente.invoke({"fuente_id": "FICHA-A"})
    assert "No hay dato" in consultar_indicador.invoke({"indicador": "aprobación", "periodo": 2026})
    assert "no disponible" in consultar_definicion.invoke({"indicador": "edad promedio"})


def test_variacion_calcula_puntos_porcentuales_y_rechaza_periodos_ausentes():
    assert "aumentó 6 puntos porcentuales" in calcular_variacion.invoke({
        "indicador": "aprobación", "periodo_inicial": 2024, "periodo_final": 2025,
    })
    assert "disminuyó 6 puntos porcentuales" in calcular_variacion.invoke({
        "indicador": "aprobación", "periodo_inicial": 2025, "periodo_final": 2024,
    })
    assert "falta al menos uno" in calcular_variacion.invoke({
        "indicador": "aprobación", "periodo_inicial": 2025, "periodo_final": 2026,
    })


def test_esquema_rechaza_argumentos_invalidos():
    with pytest.raises(ValidationError):
        consultar_indicador.invoke({"indicador": "aprobación", "periodo": "no es un año"})
    with pytest.raises(ValidationError):
        calcular_variacion.invoke({"indicador": "aprobación", "periodo_inicial": 2024})


def test_agente_registra_seleccion_secuencia_y_sesiones_aisladas(tmp_path):
    ruta = tmp_path / "trazas.jsonl"
    agente = AgenteAcademico(ModeloAgenteSimulado(), archivo_trazas=ruta)

    consultas = (
        ("¿Cuál fue la tasa de aprobación en 2025?", ["consultar_indicador"]),
        ("¿Qué significa la tasa de retención?", ["consultar_definicion"]),
        (
            "¿Cuánto aumentó la tasa de aprobación entre 2024 y 2025 y qué ficha respalda el dato?",
            ["calcular_variacion", "consultar_fuente"],
        ),
    )
    for numero, (pregunta, esperadas) in enumerate(consultas):
        resultado = agente.consultar(pregunta, session_id=f"sesion-{numero}")
        assert [accion.tool for accion, _ in resultado["intermediate_steps"]] == esperadas
        assert "ficticia" in resultado["output"]

    assert len(agente.obtener_historial("sesion-0").messages) == 2
    assert len(agente.obtener_historial("sesion-1").messages) == 2
    assert len(agente.obtener_historial("sesion-2").messages) == 2
    registros = [json.loads(linea) for linea in ruta.read_text(encoding="utf-8").splitlines()]
    assert len(registros) == 3
    assert [accion["herramienta"] for accion in registros[2]["acciones"]] == consultas[2][1]
    assert "puntos porcentuales" in registros[2]["respuesta_final"]
    agente.cerrar_sesion("sesion-0")
    assert "sesion-0" not in agente.historiales


def test_entrada_invalida_y_consulta_sin_herramientas():
    agente = AgenteAcademico(ModeloAgenteSimulado())
    with pytest.raises(ValueError):
        agente.consultar("  ", "sesion")
    with pytest.raises(ValueError):
        agente.consultar("Pregunta", "")
    resultado = agente.consultar("¿Cuál es la edad promedio?", "sesion")
    assert resultado["intermediate_steps"] == []
    assert "No hay información suficiente" in resultado["output"]


def test_memoria_resuelve_referencia_en_misma_sesion_sin_mezclar_otra():
    agente = AgenteAcademico(ModeloAgenteSimulado())
    agente.consultar("¿Cuál fue la tasa de aprobación en 2025?", "a")
    seguimiento = agente.consultar("¿Y en 2024?", "a")
    otra_sesion = agente.consultar("¿Y en 2024?", "b")
    assert "68 %" in seguimiento["output"]
    assert [accion.tool for accion, _ in seguimiento["intermediate_steps"]] == ["consultar_indicador"]
    assert otra_sesion["intermediate_steps"] == []
    assert len(agente.obtener_historial("a").messages) == 4
    assert len(agente.obtener_historial("b").messages) == 2


def test_memoria_conserva_periodo_al_cambiar_de_indicador():
    agente = AgenteAcademico(ModeloAgenteSimulado())
    agente.consultar("¿Cómo estuvo la aprobación del año 2025?", "misma")
    seguimiento = agente.consultar("¿Y la retención?", "misma")
    sin_contexto = agente.consultar("¿Y la retención?", "nueva")

    accion = seguimiento["intermediate_steps"][0][0]
    assert accion.tool == "consultar_indicador"
    assert accion.tool_input == {"indicador": "retención", "periodo": 2025}
    assert "92 %" in seguimiento["output"]
    assert [type(m).__name__ for m in seguimiento["chat_history"]] == ["HumanMessage", "AIMessage"]
    assert sin_contexto["intermediate_steps"][0][0].tool_input == {"indicador": "retención"}
    assert len(agente.obtener_historial("misma").messages) == 4


def test_salida_de_gemini_conserva_texto_sin_metadatos():
    bloques = [{"type": "text", "text": "Respuesta académica", "extras": {"signature": "interno"}}]
    assert _texto_respuesta(bloques) == "Respuesta académica"
    with pytest.raises(TypeError):
        _texto_respuesta([{"type": "metadata", "signature": "interno"}])
