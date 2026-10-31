"""Genera y evalúa respuestas reales para 20 casos académicos ficticios.

La ejecución guarda cada caso inmediatamente y puede reanudarse. El archivo de
resultados contiene respuestas del modelo, no conclusiones de revisión humana.
"""

import argparse
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean

from casos_academicos import CASOS
from cliente_gemini import ClienteGemini, Configuracion
from metricas_texto import calcular_metricas, calcular_metricas_crudas


RUTA_RESULTADOS = Path(__file__).parent / "evaluaciones" / "unidad_2_2" / "resultados_metricas.json"
VERSION_CASOS = 1
INSTRUCCION = (
    "Eres un asistente académico en una prueba con datos ficticios. "
    "Responde en español en una o dos frases breves usando únicamente el contexto. "
    "Incluye la fuente tal como aparece en el contexto. "
    "Si falta un dato, dilo claramente. No inventes cifras ni documentos."
)


def _ahora_utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def _cargar(modelo: str) -> dict:
    if not RUTA_RESULTADOS.exists():
        return {"version_casos": VERSION_CASOS, "modelo": modelo, "casos": []}
    datos = json.loads(RUTA_RESULTADOS.read_text(encoding="utf-8"))
    if datos.get("version_casos") != VERSION_CASOS or datos.get("modelo") != modelo:
        raise ValueError("El archivo existente usa otra versión de casos o modelo.")
    if not isinstance(datos.get("casos"), list):
        raise ValueError("El archivo existente no contiene una lista de casos.")
    referencias = {caso.id: caso.referencia for caso in CASOS}
    ids = [fila.get("id") for fila in datos["casos"]]
    if len(ids) != len(set(ids)) or any(
        fila.get("referencia") != referencias.get(fila.get("id"))
        for fila in datos["casos"]
    ):
        raise ValueError("Los casos guardados no coinciden con las referencias actuales.")
    return datos


def _guardar(datos: dict) -> None:
    RUTA_RESULTADOS.parent.mkdir(parents=True, exist_ok=True)
    filas = datos["casos"]
    datos["actualizado_utc"] = _ahora_utc()
    datos["resumen"] = {
        "respuestas": len(filas),
        "precision_promedio": mean(fila["precision"] for fila in filas) if filas else 0.0,
        "cobertura_promedio": mean(fila["cobertura"] for fila in filas) if filas else 0.0,
        "f1_promedio": mean(fila["f1"] for fila in filas) if filas else 0.0,
        "costo_total_usd_estimado": sum(fila["costo_usd_estimado"] for fila in filas),
    }
    temporal = RUTA_RESULTADOS.with_suffix(".tmp")
    temporal.write_text(json.dumps(datos, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.replace(temporal, RUTA_RESULTADOS)


def ejecutar(limite: int | None = None) -> int:
    configuracion = Configuracion.desde_entorno()
    datos = _cargar(configuracion.modelo)
    completados = {fila["id"] for fila in datos["casos"]}
    pendientes = [caso for caso in CASOS if caso.id not in completados]
    if limite is not None:
        pendientes = pendientes[:limite]
    if not pendientes:
        print(f"No hay casos pendientes. Total guardado: {len(completados)}/{len(CASOS)}.")
        return 0

    cliente = ClienteGemini(configuracion)
    for caso in pendientes:
        consulta = f"Contexto ficticio: {caso.contexto}\nPregunta: {caso.pregunta}"
        try:
            respuesta = cliente.consultar_modelo(consulta, system_instruction=INSTRUCCION)
        except (RuntimeError, ValueError) as error:
            print(f"{caso.id}: fallo ({error}). Se conservaron los casos anteriores.")
            return 1
        metricas = calcular_metricas(caso.referencia, respuesta)
        operacion = cliente.registro_costos.ultima_operacion
        fila = {
            "id": caso.id,
            "fecha_utc": _ahora_utc(),
            "pregunta": caso.pregunta,
            "contexto_ficticio": caso.contexto,
            "fuente_ficticia": caso.fuente,
            "referencia": caso.referencia,
            "respuesta": respuesta,
            **metricas,
            "costo_usd_estimado": operacion.usd_estimados if operacion else 0.0,
        }
        if caso.id in {"A01", "A02", "A03"}:
            fila["metricas_texto_crudo"] = calcular_metricas_crudas(
                caso.referencia, respuesta
            )
        datos["casos"].append(fila)
        _guardar(datos)
        print(f"{caso.id}: F1={metricas['f1']:.3f}; guardado {len(datos['casos'])}/{len(CASOS)}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--limite", type=int, help="Máximo de consultas nuevas en esta ejecución."
    )
    argumentos = parser.parse_args()
    if argumentos.limite is not None and argumentos.limite < 1:
        parser.error("--limite debe ser mayor que cero")
    return ejecutar(argumentos.limite)


if __name__ == "__main__":
    raise SystemExit(main())
