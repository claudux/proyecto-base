"""Recuperación semántica, generación con citas y registro de uso real."""

import json
import re
import time
from datetime import datetime, timezone

from cliente_gemini import ClienteGemini, Configuracion

from .indice import RAIZ, cargar_indice


INSTRUCCION = (
    "Responde solo con el contexto recuperado. Cita cada afirmación factual con "
    "el número del fragmento entre corchetes, por ejemplo [1]. Si no hay evidencia "
    "suficiente, dilo explícitamente. Todo el corpus es ficticio."
)


def recuperar(db, pregunta: str, k: int):
    if not pregunta.strip() or k < 1:
        raise ValueError("La pregunta no puede estar vacía y k debe ser positivo.")
    inicio = time.perf_counter()
    vector = db.embeddings.embed_query(pregunta)
    ms_embedding = (time.perf_counter() - inicio) * 1000
    inicio = time.perf_counter()
    documentos = db.similarity_search_by_vector(vector, k=k)
    ms_busqueda = (time.perf_counter() - inicio) * 1000
    return documentos, {"embedding_consulta": round(ms_embedding, 2), "busqueda": round(ms_busqueda, 2)}


def formatear_contexto(documentos):
    citas = {}
    bloques = []
    for numero, documento in enumerate(documentos, start=1):
        fuente = documento.metadata.get("fuente")
        if not fuente or not documento.id:
            raise ValueError("Un chunk no tiene fuente o ID; revisa la indexación.")
        citas[numero] = {"id": documento.id, "fuente": fuente}
        bloques.append(f"[{numero}] Fuente: {fuente}; ID: {documento.id}\n{documento.page_content}")
    return "\n\n".join(bloques), citas


def revisar_citas(respuesta: str, citas: dict) -> dict:
    grupos = re.findall(r"\[([0-9]+(?:\s*,\s*[0-9]+)*)\]", respuesta)
    numeros = {int(n) for grupo in grupos for n in grupo.split(",")}
    return {
        "citadas": sorted(numeros),
        "invalidas": sorted(numeros - citas.keys()),
        "sin_citas": not numeros,
    }


def consultar(pregunta: str, k: int = 2) -> dict:
    inicio_total = time.perf_counter()
    db = cargar_indice()
    documentos, tiempos = recuperar(db, pregunta, k)
    contexto, citas = formatear_contexto(documentos)
    cliente = ClienteGemini(Configuracion.desde_entorno())
    inicio = time.perf_counter()
    respuesta = cliente.consultar_modelo(
        f"Contexto:\n{contexto}\n\nPregunta: {pregunta}",
        system_instruction=INSTRUCCION,
    )
    tiempos["generacion"] = round((time.perf_counter() - inicio) * 1000, 2)
    tiempos["etapas_medidas"] = round(sum(tiempos.values()), 2)
    tiempos["total"] = round((time.perf_counter() - inicio_total) * 1000, 2)
    operacion = cliente.registro_costos.ultima_operacion
    registro = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "pregunta": pregunta,
        "k": k,
        "ids_recuperados": [d.id for d in documentos],
        "citas": citas,
        "respuesta": respuesta,
        "revision_citas": revisar_citas(respuesta, citas),
        "tiempos_ms": tiempos,
        "tokens_generacion": {
            "entrada": operacion.tokens_entrada,
            "salida": operacion.tokens_salida,
            "razonamiento": operacion.tokens_razonamiento,
        },
        "usd_generacion_estimado": operacion.usd_estimados,
        "usd_embeddings": None,
    }
    carpeta = RAIZ / "evaluaciones" / "unidad_2_5"
    carpeta.mkdir(parents=True, exist_ok=True)
    with (carpeta / "registros_latencia_costo.jsonl").open("a", encoding="utf-8") as archivo:
        archivo.write(json.dumps(registro, ensure_ascii=False) + "\n")
    return registro
