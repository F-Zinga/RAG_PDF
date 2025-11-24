import os
from typing import List, Tuple, Optional
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from .config import settings

# Global state
_embeddings = None
_vector_store = None

def get_embeddings():
    global _embeddings
    if _embeddings is None:
        _embeddings = HuggingFaceEmbeddings(model_name=settings.EMBEDDING_MODEL, model_kwargs={"device": "cpu"})
    return _embeddings

def get_vector_store():
    global _vector_store
    if _vector_store is None:
        embeddings = get_embeddings()
        if os.path.isdir(settings.INDEX_DIR) and os.listdir(settings.INDEX_DIR):
             try:
                _vector_store = FAISS.load_local(settings.INDEX_DIR, embeddings, allow_dangerous_deserialization=True)
             except Exception as e:
                 print(f"Failed to load index: {e}, creating new one.")
                 # Initialize empty if load fails? Or better to let it be None and created on ingest?
                 # But ingest assumes we can add to existing.
                 # Let's handle initialization when needed.
                 pass
    return _vector_store

def initialize_rag():
    """Initializes the RAG components (embeddings and vector store) into memory."""
    print("Initializing RAG engine...")
    get_embeddings()
    get_vector_store()
    print("RAG engine initialized.")

def _split_docs(pages) -> List:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.CHUNK_SIZE,
        chunk_overlap=settings.CHUNK_OVERLAP,
        add_start_index=True,
        separators=["\n\n", "\n", " ", ""],
    )
    return splitter.split_documents(pages)

def ingest_pdf(file_path: str) -> int:
    global _vector_store
    loader = PyPDFLoader(file_path)
    pages = loader.load()  # page has {"source":..., "page":...}
    for d in pages:
        # path short come "source"
        d.metadata["source"] = os.path.basename(d.metadata.get("source", os.path.basename(file_path)))
        # page start from 1
        if "page" in d.metadata:
            d.metadata["page"] = int(d.metadata["page"]) + 1
    chunks = _split_docs(pages)

    # Ensure vector store is loaded
    vs = get_vector_store()

    if vs is None:
        # Create new if doesn't exist
        vs = FAISS.from_documents(chunks, get_embeddings())
        _vector_store = vs
    else:
        vs.add_documents(chunks)

    vs.save_local(settings.INDEX_DIR)
    return len(chunks)

def retrieve(query: str, k: int = None) -> List[Tuple[str, dict, float]]:
    k = k or settings.TOP_K
    vs = get_vector_store()
    if vs is None:
        # Index empty
        return []

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
