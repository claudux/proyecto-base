"""Construcción y carga del índice documental persistente de la Unidad 2.5."""

import hashlib
import json
import os
from pathlib import Path

from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter


RAIZ = Path(__file__).resolve().parent.parent
CORPUS = RAIZ / "rag" / "corpus"
ALMACEN = RAIZ / "rag" / "almacen"
COLECCION = "academico_ficticio_v1"
MODELO_EMBEDDING = "gemini-embedding-001"
TAMANO_CHUNK = 500
SOLAPAMIENTO = 50


def cargar_documentos() -> list[Document]:
    """Lee solo Markdown versionado y conserva la ruta de origen para citar."""
    documentos = []
    for ruta in sorted(CORPUS.glob("*.md")):
        texto = ruta.read_text(encoding="utf-8").strip()
        if not texto:
            raise ValueError(f"Documento vacío: {ruta}")
        documentos.append(Document(page_content=texto, metadata={"fuente": ruta.name}))
    if len(documentos) < 8:
        raise ValueError("El corpus necesita al menos ocho documentos no vacíos.")
    return documentos


def preparar_chunks(documentos: list[Document], tamano: int = TAMANO_CHUNK) -> list[Document]:
    """Asigna IDs reproducibles; cada documento mantiene su propia numeración."""
    splitter = RecursiveCharacterTextSplitter(chunk_size=tamano, chunk_overlap=min(SOLAPAMIENTO, tamano - 1))
    chunks = []
    for documento in documentos:
        partes = splitter.split_documents([documento])
        for numero, parte in enumerate(partes):
            if not parte.page_content.strip():
                raise ValueError(f"Chunk vacío en {documento.metadata['fuente']}")
            parte.id = f"{documento.metadata['fuente']}:{numero}"
            chunks.append(parte)
    if len({chunk.id for chunk in chunks}) != len(chunks):
        raise ValueError("Hay IDs de chunks duplicados.")
    return chunks


def huella(documentos: list[Document]) -> str:
    """Detecta cambios del corpus o de la configuración que exigen reindexar."""
    datos = {
        "modelo": MODELO_EMBEDDING,
        "tamano_chunk": TAMANO_CHUNK,
        "solapamiento": SOLAPAMIENTO,
        "documentos": [(d.metadata["fuente"], d.page_content) for d in documentos],
    }
    serializado = json.dumps(datos, ensure_ascii=False, sort_keys=True)
    return hashlib.sha256(serializado.encode("utf-8")).hexdigest()


def crear_embeddings() -> GoogleGenerativeAIEmbeddings:
    load_dotenv(RAIZ / ".env")
    clave = os.getenv("GEMINI_API_KEY", "")
    if not clave or clave == "tu_llave_aqui":
        raise ValueError("Configura GEMINI_API_KEY en .env antes de usar embeddings reales.")
    return GoogleGenerativeAIEmbeddings(model=MODELO_EMBEDDING, google_api_key=clave)


def comparar_chunking() -> list[dict]:
    """Comparación local, sin clave ni llamadas a la API."""
    documentos = cargar_documentos()
    resultados = []
    for tamano in (150, TAMANO_CHUNK):
        chunks = preparar_chunks(documentos, tamano)
        resultados.append({
            "tamano": tamano,
            "cantidad": len(chunks),
            "longitudes": [len(c.page_content) for c in chunks],
            "muestra": [(c.id, c.page_content[:100]) for c in chunks[:3]],
        })
    return resultados


def indexar() -> dict:
    """Crea el índice una sola vez, sin duplicar entradas existentes."""
    documentos = cargar_documentos()
    chunks = preparar_chunks(documentos)
    if ALMACEN.exists():
        raise FileExistsError(
            f"{ALMACEN} ya existe. Revisa o retira ese índice antes de reconstruirlo."
        )
    db = Chroma.from_documents(
        documents=chunks,
        embedding=crear_embeddings(),
        ids=[c.id for c in chunks],
        collection_name=COLECCION,
        persist_directory=str(ALMACEN),
    )
    cantidad = len(db.get(include=[])["ids"])
    if cantidad != len(chunks):
        raise RuntimeError(f"Persistencia incompleta: {cantidad} de {len(chunks)} chunks.")
    manifiesto = {
        "huella": huella(documentos),
        "modelo_embedding": MODELO_EMBEDDING,
        "tamano_chunk": TAMANO_CHUNK,
        "solapamiento": SOLAPAMIENTO,
        "documentos": len(documentos),
        "chunks": cantidad,
    }
    (ALMACEN / "manifiesto.json").write_text(
        json.dumps(manifiesto, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return manifiesto


def cargar_indice() -> Chroma:
    """Reabre el índice y rechaza uno vacío o desactualizado."""
    ruta_manifiesto = ALMACEN / "manifiesto.json"
    if not ruta_manifiesto.is_file():
        raise FileNotFoundError("No hay índice completo. Ejecuta primero 'indexar'.")
    manifiesto = json.loads(ruta_manifiesto.read_text(encoding="utf-8"))
    if manifiesto["huella"] != huella(cargar_documentos()):
        raise ValueError("El corpus o la configuración cambiaron: reconstruye el índice.")
    db = Chroma(
        collection_name=COLECCION,
        persist_directory=str(ALMACEN),
        embedding_function=crear_embeddings(),
    )
    if len(db.get(include=[])["ids"]) != manifiesto["chunks"]:
        raise RuntimeError("La cantidad de chunks no coincide con el manifiesto.")
    return db
