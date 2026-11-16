"""Comandos: comparar, indexar, consultar y evaluar el RAG ficticio."""

import argparse
import json

from .consulta import consultar
from .evaluacion import evaluar
from .indice import comparar_chunking, indexar


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="accion", required=True)
    sub.add_parser("comparar", help="Compara chunking localmente, sin API")
    sub.add_parser("indexar", help="Crea embeddings reales e índice persistente")
    consulta = sub.add_parser("consultar", help="Recupera y genera una respuesta con Gemini")
    consulta.add_argument("pregunta")
    consulta.add_argument("--k", type=int, default=2)
    evaluacion = sub.add_parser("evaluar", help="Evalúa recuperación con Gemini Embeddings")
    evaluacion.add_argument("--k", type=int, default=2)
    args = parser.parse_args()

    if args.accion == "comparar":
        resultado = comparar_chunking()
    elif args.accion == "indexar":
        resultado = indexar()
    elif args.accion == "consultar":
        resultado = consultar(args.pregunta, args.k)
    else:
        informe, ruta = evaluar(args.k)
        resultado = {
            "preguntas": informe["preguntas"],
            "precision_promedio": informe["precision_promedio"],
            "recall_promedio": informe["recall_promedio"],
            "informe": ruta,
        }
    print(json.dumps(resultado, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
