"""Coincidencia de palabras con repeticiones; no evalúa significado."""

from collections import Counter

from pipeline_texto import procesar_texto


def contar_coincidencias(
    tokens_referencia: list[str], tokens_respuesta: list[str]
) -> int:
    """Cuenta la intersección de los dos multiconjuntos de tokens."""
    return sum((Counter(tokens_referencia) & Counter(tokens_respuesta)).values())


def calcular_precision_cobertura_f1(
    tokens_referencia: list[str], tokens_respuesta: list[str]
) -> dict[str, float]:
    """Devuelve cero si alguno de los textos no contiene tokens."""
    if not tokens_referencia or not tokens_respuesta:
        return {"precision": 0.0, "cobertura": 0.0, "f1": 0.0}

    coincidencias = contar_coincidencias(tokens_referencia, tokens_respuesta)
    precision = coincidencias / len(tokens_respuesta)
    cobertura = coincidencias / len(tokens_referencia)
    f1 = 2 * precision * cobertura / (precision + cobertura) if coincidencias else 0.0
    return {"precision": precision, "cobertura": cobertura, "f1": f1}


def calcular_metricas(referencia: str, respuesta: str) -> dict[str, float]:
    """Aplica el pipeline a ambos textos antes de compararlos."""
    return calcular_precision_cobertura_f1(
        procesar_texto(referencia), procesar_texto(respuesta)
    )


def calcular_metricas_crudas(referencia: str, respuesta: str) -> dict[str, float]:
    """Línea base sin normalización para observar el efecto del pipeline."""
    return calcular_precision_cobertura_f1(referencia.split(), respuesta.split())
