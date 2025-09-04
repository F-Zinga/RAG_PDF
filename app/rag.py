import os
from typing import List, Tuple
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from .config import settings

def _embedding():
    return HuggingFaceEmbeddings(model_name=settings.EMBEDDING_MODEL, model_kwargs={"device": "cpu"})

def _split_docs(pages) -> List:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.CHUNK_SIZE,
        chunk_overlap=settings.CHUNK_OVERLAP,
        add_start_index=True,
        separators=["\n\n", "\n", " ", ""],
    )
    return splitter.split_documents(pages)

def ingest_pdf(file_path: str) -> int:
    loader = PyPDFLoader(file_path)
    pages = loader.load()  # ogni pagina ha metadata {"source":..., "page":...}
    for d in pages:
        # Rendi il path più corto come "source"
        d.metadata["source"] = os.path.basename(d.metadata.get("source", os.path.basename(file_path)))
        # assicura che "page" parta da 1
        if "page" in d.metadata:
            d.metadata["page"] = int(d.metadata["page"]) + 1
    chunks = _split_docs(pages)

    if os.path.isdir(settings.INDEX_DIR) and os.listdir(settings.INDEX_DIR):
        vs = FAISS.load_local(settings.INDEX_DIR, _embedding(), allow_dangerous_deserialization=True)
        vs.add_documents(chunks)
    else:
        vs = FAISS.from_documents(chunks, _embedding())
    vs.save_local(settings.INDEX_DIR)
    return len(chunks)

def retrieve(query: str, k: int = None) -> List[Tuple[str, dict, float]]:
    k = k or settings.TOP_K
    vs = FAISS.load_local(settings.INDEX_DIR, _embedding(), allow_dangerous_deserialization=True)
    results = vs.similarity_search_with_score(query, k=k)
    # results: List[(Document, score)]
    triples = []
    for doc, score in results:
        meta = doc.metadata or {}
        src = meta.get("source", "unknown")
        page = meta.get("page", "?")
        triples.append((doc.page_content, {"source": src, "page": page}, float(score)))
    return triples

def format_context(triples: List[Tuple[str, dict, float]]) -> str:
    blocks = []
    for content, meta, score in triples:
        blocks.append(f"[{meta['source']}:{meta['page']}] (score={score:.3f})\n{content}")
    return "\n\n---\n\n".join(blocks)
