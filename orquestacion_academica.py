"""Flujo LCEL de consulta académica sobre un contexto aportado por el usuario.

Este módulo no busca documentos ni valida la veracidad del contexto. Los pasos
son inyectables para probar el enrutamiento y los fallos sin usar la API.
"""

import logging

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableBranch, RunnableLambda, RunnablePassthrough


LOG = logging.getLogger(__name__)
SIN_DATOS = "No hay información suficiente en el contexto proporcionado para responder."
ERROR_GENERAL = "No pudimos procesar la consulta en este momento. Intenta más tarde."
ERROR_RUTA = "No se pudo completar el análisis. Revisa la fuente proporcionada e intenta más tarde."


def normalizar_categoria(texto: str) -> str:
    """Un resultado inesperado toma la ruta segura de información insuficiente."""
    if not isinstance(texto, str):
        raise TypeError("La categoría debe ser texto.")
    categoria = texto.strip().lower().rstrip(".:")
    return categoria if categoria in {"indicador", "definicion"} else "sin_datos"


def construir_clasificador(modelo):
    plantilla = PromptTemplate.from_template(
        "Clasifica la pregunta académica en una sola palabra: indicador, "
        "definicion o sin_datos. Usa indicador para cifras, tasas o comparaciones; "
        "definicion para el significado de un concepto; sin_datos para otro tema. "
        "No respondas la pregunta.\nPregunta: {pregunta}"
    )
    return plantilla | modelo | StrOutputParser() | RunnableLambda(normalizar_categoria)


def _paso(modelo, instruccion: str):
    return PromptTemplate.from_template(instruccion) | modelo | StrOutputParser()


def construir_ruta(modelo, tipo: str):
    """Extrae, analiza, redacta y revisa la respuesta de la ruta elegida."""
    if tipo == "indicador":
        enfoque = (
            "Extrae solo cifras, períodos, unidades y definición del indicador "
            "pertinentes. Distingue porcentaje de puntos porcentuales."
        )
        criterio_analisis = (
            "Compara únicamente los períodos disponibles. Si ambas tasas están "
            "en porcentaje, resta sus valores y expresa la variación en puntos "
            "porcentuales. Si falta algún dato, escribe FALTAN DATOS."
        )
    elif tipo == "definicion":
        enfoque = "Extrae la definición pertinente y sus condiciones o exclusiones."
        criterio_analisis = (
            "Identifica qué significa el concepto y qué condiciones o exclusiones "
            "indica la evidencia. Si no aparece la definición, escribe FALTAN DATOS."
        )
    else:
        raise ValueError("Ruta académica desconocida")

    extraer = _paso(
        modelo,
        "Trabajas solo con el contexto suministrado. {enfoque} "
        "Si falta evidencia, escribe FALTAN DATOS.\n"
        "Pregunta: {pregunta}\nContexto: {contexto}",
    )
    analizar = _paso(
        modelo,
        "Analiza la evidencia para responder la pregunta. {criterio_analisis} "
        "No añadas cifras ni reglas que no aparezcan en la evidencia.\n"
        "Pregunta: {pregunta}\nEvidencia: {evidencia}",
    )
    redactar = _paso(
        modelo,
        "Responde la pregunta usando exclusivamente la evidencia y su análisis. "
        "Si alguno dice FALTAN DATOS, explica qué falta sin inventar. "
        "Incluye la fuente indicada.\nPregunta: {pregunta}\n"
        "Evidencia: {evidencia}\nAnálisis: {analisis}\nFuente: {fuente}",
    )
    revisar = _paso(
        modelo,
        "Revisa el borrador contra la evidencia y el contexto original. "
        "Corrige cifras, unidades y afirmaciones sin respaldo. "
        "Si no hay sustento suficiente, responde que faltan datos. "
        "Conserva la fuente y aclara que es ficticia si corresponde. "
        "Entrega solo la respuesta final.\nPregunta: {pregunta}\n"
        "Contexto: {contexto}\nEvidencia: {evidencia}\n"
        "Análisis: {analisis}\n"
        "Borrador: {borrador}\nFuente: {fuente}",
    )

    cadena = (
        RunnablePassthrough.assign(enfoque=lambda _: enfoque)
        | RunnablePassthrough.assign(evidencia=extraer)
        | RunnablePassthrough.assign(criterio_analisis=lambda _: criterio_analisis)
        | RunnablePassthrough.assign(analisis=analizar)
        | RunnablePassthrough.assign(borrador=redactar)
        | revisar
    )
    def alternativa(datos):
        LOG.error("Falló la ruta %s: %s", tipo, datos["error"])
        return ERROR_RUTA

    return cadena.with_fallbacks(
        [RunnableLambda(alternativa)], exception_key="error"
    )


def construir_cadena(modelo, *, clasificador=None, ruta_indicador=None, ruta_definicion=None):
    """Conserva entrada y categoría para escoger una de tres rutas."""
    clasificador = clasificador if clasificador is not None else construir_clasificador(modelo)
    ruta_indicador = ruta_indicador if ruta_indicador is not None else construir_ruta(modelo, "indicador")
    ruta_definicion = ruta_definicion if ruta_definicion is not None else construir_ruta(modelo, "definicion")
    bifurcacion = RunnableBranch(
        (lambda datos: datos["categoria"] == "indicador", ruta_indicador),
        (lambda datos: datos["categoria"] == "definicion", ruta_definicion),
        RunnableLambda(lambda _: SIN_DATOS),
    )
    return RunnablePassthrough.assign(categoria=clasificador) | bifurcacion


def procesar_consulta(cadena, pregunta: str, contexto: str, fuente: str) -> str:
    """Valida la entrada y contiene fallos anteriores a la bifurcación."""
    if not all(isinstance(valor, str) for valor in (pregunta, contexto, fuente)):
        raise TypeError("La pregunta, el contexto y la fuente deben ser texto.")
    if not pregunta.strip():
        raise ValueError("La pregunta no puede estar vacía.")
    if not contexto.strip() or not fuente.strip():
        return SIN_DATOS
    try:
        return cadena.invoke({"pregunta": pregunta, "contexto": contexto, "fuente": fuente})
    except Exception:
        LOG.exception("Falló la orquestación de la consulta académica")
        return ERROR_GENERAL
