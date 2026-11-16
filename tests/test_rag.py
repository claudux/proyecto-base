"""Riesgos propios del RAG: IDs, persistencia y casos borde de evaluación."""

import subprocess
import sys

from rag.consulta import revisar_citas
from rag.evaluacion import metricas
from rag.indice import RAIZ, cargar_documentos, preparar_chunks


def test_corpus_tiene_fuentes_y_ids_estables():
    documentos = cargar_documentos()
    chunks = preparar_chunks(documentos)
    assert len(documentos) >= 8
    assert len(chunks) == len(documentos)  # Con 500 caracteres, una idea por documento.
    assert len({c.id for c in chunks}) == len(chunks)
    assert all(c.page_content and c.metadata["fuente"] for c in chunks)


def test_chroma_persiste_y_recarga_ids_sin_api(carpeta_temporal):
    carpeta = carpeta_temporal / "indice"
    # Procesos separados comprueban la persistencia real y liberan el archivo
    # SQLite antes de que Windows retire la carpeta temporal.
    crear = """
import sys
from langchain_chroma import Chroma
from langchain_core.embeddings import DeterministicFakeEmbedding
from rag.indice import cargar_documentos, preparar_chunks
chunks = preparar_chunks(cargar_documentos())
db = Chroma.from_documents(
    chunks, embedding=DeterministicFakeEmbedding(size=16),
    ids=[c.id for c in chunks], collection_name="prueba_rag",
    persist_directory=sys.argv[1],
)
assert len(db.get(include=[])["ids"]) == len(chunks)
"""
    recargar = """
import sys
from langchain_chroma import Chroma
from langchain_core.embeddings import DeterministicFakeEmbedding
from rag.indice import cargar_documentos, preparar_chunks
db = Chroma(
    collection_name="prueba_rag", persist_directory=sys.argv[1],
    embedding_function=DeterministicFakeEmbedding(size=16),
)
assert set(db.get(include=[])["ids"]) == {
    c.id for c in preparar_chunks(cargar_documentos())
}
"""
    for codigo in (crear, recargar):
        subprocess.run([sys.executable, "-c", codigo, str(carpeta)], cwd=RAIZ, check=True)


def test_metricas_y_citas_invalidas():
    assert metricas(["a", "b"], {"a"}) == (0.5, 1.0)
    assert metricas([], {"a"}) == (0.0, 0.0)
    assert metricas(["a"], set()) == (0.0, None)
    assert revisar_citas("Dato [1] y otro [99]", {1: {"fuente": "x"}})["invalidas"] == [99]
    assert revisar_citas("Evidencia [1, 2]", {1: {}, 2: {}}) == {
        "citadas": [1, 2], "invalidas": [], "sin_citas": False,
    }
