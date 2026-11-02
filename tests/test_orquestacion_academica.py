"""Pruebas de rutas, pasos y errores de la chain sin red."""

from langchain_core.messages import AIMessage
from langchain_core.runnables import RunnableLambda

from orquestacion_academica import (
    ERROR_GENERAL,
    ERROR_RUTA,
    SIN_DATOS,
    construir_cadena,
    construir_clasificador,
    construir_ruta,
    procesar_consulta,
)


ENTRADA = {
    "pregunta": "¿Cómo cambió la aprobación?",
    "contexto": "68 % en 2024 y 74 % en 2025.",
    "fuente": "Ficha ficticia A",
}


def test_clasificador_normaliza_y_descarta_categoria_imprevista():
    modelo = RunnableLambda(lambda _: AIMessage(content="  InDiCaDoR. \n"))
    assert construir_clasificador(modelo).invoke(ENTRADA) == "indicador"
    modelo_ambiguo = RunnableLambda(lambda _: AIMessage(content="tal vez indicador"))
    assert construir_clasificador(modelo_ambiguo).invoke(ENTRADA) == "sin_datos"


def test_enrutamiento_conserva_entrada_y_elige_cada_ruta():
    modelo_no_usado = RunnableLambda(lambda _: AIMessage(content="no debe llamarse"))
    for categoria, esperado in (
        ("indicador", "ruta indicador"),
        ("definicion", "ruta definición"),
        ("sin_datos", SIN_DATOS),
    ):
        cadena = construir_cadena(
            modelo_no_usado,
            clasificador=RunnableLambda(lambda _, c=categoria: c),
            ruta_indicador=RunnableLambda(lambda d: "ruta indicador: " + d["fuente"]),
            ruta_definicion=RunnableLambda(lambda d: "ruta definición: " + d["fuente"]),
        )
        assert cadena.invoke(ENTRADA).startswith(esperado)


def test_ruta_ejecuta_cuatro_pasos_en_orden_y_transfiere_sus_salidas():
    etapas = []

    def modelo(entrada):
        prompt = entrada.to_string()
        if "Extrae solo cifras" in prompt:
            etapas.append("extraer")
            return AIMessage(content="2024: 68 %; 2025: 74 %")
        if "Analiza la evidencia" in prompt:
            etapas.append("analizar")
            assert "2024: 68 %; 2025: 74 %" in prompt
            return AIMessage(content="74 - 68 = 6 puntos porcentuales")
        if "Responde la pregunta usando" in prompt:
            etapas.append("redactar")
            assert "2024: 68 %; 2025: 74 %" in prompt
            assert "74 - 68 = 6 puntos porcentuales" in prompt
            return AIMessage(content="Subió 6 puntos porcentuales.")
        etapas.append("revisar")
        assert "Subió 6 puntos porcentuales." in prompt
        return AIMessage(content="Subió 6 puntos porcentuales. Fuente: Ficha ficticia A.")

    resultado = construir_ruta(RunnableLambda(modelo), "indicador").invoke(ENTRADA)
    assert etapas == ["extraer", "analizar", "redactar", "revisar"]
    assert "Fuente: Ficha ficticia A" in resultado


def test_fallo_en_ruta_usa_fallback_y_fallo_en_clasificador_usa_salida_general(caplog):
    def fallar(_):
        raise ConnectionError("fallo simulado")

    ruta = construir_ruta(RunnableLambda(fallar), "indicador")
    assert ruta.invoke(ENTRADA.copy()) == ERROR_RUTA
    assert "Falló la ruta indicador" in caplog.text

    cadena = construir_cadena(
        RunnableLambda(fallar),
        ruta_indicador=RunnableLambda(lambda _: "indicador"),
        ruta_definicion=RunnableLambda(lambda _: "definición"),
    )
    assert procesar_consulta(cadena, **ENTRADA) == ERROR_GENERAL
    assert "Falló la orquestación" in caplog.text


def test_contexto_o_fuente_ausente_no_consulta_el_modelo():
    cadena = RunnableLambda(lambda _: (_ for _ in ()).throw(AssertionError("no invocar")))
    assert procesar_consulta(cadena, ENTRADA["pregunta"], "", ENTRADA["fuente"]) == SIN_DATOS
    assert procesar_consulta(cadena, ENTRADA["pregunta"], ENTRADA["contexto"], "") == SIN_DATOS
