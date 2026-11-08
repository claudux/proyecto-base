"""Cuatro herramientas de solo lectura sobre el catálogo académico ficticio."""

import unicodedata

from langchain_core.tools import tool
from pydantic import BaseModel, Field

from datos_agente_academico import FUENTES, INDICADORES


def _normalizar(texto: str) -> str:
    sin_acentos = unicodedata.normalize("NFKD", texto.casefold())
    return "".join(caracter for caracter in sin_acentos if not unicodedata.combining(caracter)).strip()


def _indicador(nombre: str):
    clave = _normalizar(nombre).removeprefix("tasa de ")
    return INDICADORES.get(clave)


class ArgumentosIndicador(BaseModel):
    indicador: str = Field(description="Nombre: aprobación, asistencia o retención.")
    periodo: int | None = Field(default=None, description="Año solicitado; omitir para ver todos los disponibles.")


@tool(args_schema=ArgumentosIndicador)
def consultar_indicador(indicador: str, periodo: int | None = None) -> str:
    """Consulta valores y períodos de un indicador académico ficticio. Usar para preguntas sobre cifras."""
    registro = _indicador(indicador)
    if registro is None:
        return "Indicador no disponible en el catálogo ficticio."
    if periodo is not None:
        valor = registro.valores.get(periodo)
        if valor is None:
            return f"No hay dato de {registro.nombre} para {periodo}."
        return f"{registro.nombre}, {periodo}: {valor} %. Fuente: {registro.fuente_id} (ficticia)."
    valores = "; ".join(f"{año}: {valor} %" for año, valor in sorted(registro.valores.items()))
    return f"{registro.nombre}: {valores}. Fuente: {registro.fuente_id} (ficticia)."


@tool
def consultar_definicion(indicador: str) -> str:
    """Consulta la definición y exclusiones de un indicador académico ficticio. Usar para preguntas conceptuales."""
    registro = _indicador(indicador)
    if registro is None:
        return "Definición no disponible en el catálogo ficticio."
    return f"{registro.nombre}: {registro.definicion} Fuente: {registro.fuente_id} (ficticia)."


class ArgumentosVariacion(BaseModel):
    indicador: str = Field(description="Nombre del indicador porcentual que se comparará.")
    periodo_inicial: int = Field(description="Año de referencia inicial.")
    periodo_final: int = Field(description="Año de referencia final.")


@tool(args_schema=ArgumentosVariacion)
def calcular_variacion(indicador: str, periodo_inicial: int, periodo_final: int) -> str:
    """Calcula la diferencia entre dos tasas disponibles, en puntos porcentuales. Usar para cambios entre períodos."""
    registro = _indicador(indicador)
    if registro is None:
        return "No se puede calcular: indicador no disponible."
    inicial = registro.valores.get(periodo_inicial)
    final = registro.valores.get(periodo_final)
    if inicial is None or final is None:
        return "No se puede calcular: falta al menos uno de los períodos solicitados."
    diferencia = final - inicial
    sentido = "aumentó" if diferencia > 0 else "disminuyó" if diferencia < 0 else "no cambió"
    return (
        f"{registro.nombre} {sentido} {abs(diferencia)} puntos porcentuales "
        f"({inicial} % en {periodo_inicial}; {final} % en {periodo_final}). "
        f"Fuente: {registro.fuente_id} (ficticia)."
    )


@tool
def consultar_fuente(fuente_id: str) -> str:
    """Consulta la identificación y alcance de una fuente ficticia por su código. Usar para preguntas sobre procedencia."""
    return FUENTES.get(fuente_id.strip().upper(), "Fuente no disponible en el catálogo ficticio.")


HERRAMIENTAS = (consultar_indicador, consultar_definicion, calcular_variacion, consultar_fuente)
