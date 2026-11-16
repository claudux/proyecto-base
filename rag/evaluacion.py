"""Precisión y recall del recuperador sobre etiquetas fijadas de antemano."""

import json
from datetime import datetime, timezone

from .consulta import recuperar
from .indice import MODELO_EMBEDDING, RAIZ, SOLAPAMIENTO, TAMANO_CHUNK, cargar_indice


CARPETA = RAIZ / "evaluaciones" / "unidad_2_5"
CASOS = CARPETA / "casos_recuperacion.json"


def metricas(ids_recuperados: list[str], ids_relevantes: set[str]) -> tuple[float, float | None]:
    """Recall no aplica a preguntas sin fragmentos relevantes etiquetados."""
    aciertos = len(set(ids_recuperados) & ids_relevantes)
    precision = aciertos / len(ids_recuperados) if ids_recuperados else 0.0
    recall = aciertos / len(ids_relevantes) if ids_relevantes else None
    return precision, recall


def evaluar(k: int = 2) -> tuple[dict, str]:
    if k < 1:
        raise ValueError("k debe ser mayor que cero.")
    casos = json.loads(CASOS.read_text(encoding="utf-8"))
    if len(casos) < 20:
        raise ValueError("El conjunto necesita al menos veinte preguntas.")
    db = cargar_indice()
    ids_indexados = set(db.get(include=[])["ids"])
    resultados = []
    for caso in casos:
        relevantes = set(caso["ids_relevantes"])
        if not relevantes <= ids_indexados:
            raise ValueError(f"Etiquetas inexistentes: {sorted(relevantes - ids_indexados)}")
        documentos, tiempos = recuperar(db, caso["pregunta"], k)
        recuperados = [d.id for d in documentos]
        precision, recall = metricas(recuperados, relevantes)
        resultados.append({
            "pregunta": caso["pregunta"],
            "ids_relevantes": sorted(relevantes),
            "ids_recuperados": recuperados,
            "precision": precision,
            "recall": recall,
            "tiempos_ms": tiempos,
        })
    recalls = [r["recall"] for r in resultados if r["recall"] is not None]
    informe = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "configuracion": {
            "k": k, "tamano_chunk": TAMANO_CHUNK,
            "solapamiento": SOLAPAMIENTO, "modelo_embedding": MODELO_EMBEDDING,
        },
        "preguntas": len(casos),
        "precision_promedio": sum(r["precision"] for r in resultados) / len(resultados),
        "recall_promedio": sum(recalls) / len(recalls) if recalls else None,
        "casos": resultados,
    }
    nombre = f"recuperacion_{datetime.now(timezone.utc):%Y%m%dT%H%M%S%fZ}_k{k}.json"
    ruta = CARPETA / nombre
    ruta.write_text(json.dumps(informe, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return informe, str(ruta)
