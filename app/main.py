import os
from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.responses import JSONResponse
from typing import Optional
from .config import settings
from .rag import ingest_pdf, retrieve, format_context, initialize_rag
from .llm_provider import generate_answer

app = FastAPI(title="RAG PDF QA", version="1.0")

@app.on_event("startup")
async def startup_event():
    initialize_rag()

@app.get("/health")
def health():
    return {"status": "ok", "provider": settings.LLM_PROVIDER, "model": settings.LLM_MODEL}

@app.post("/ingest")
async def ingest(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Carica un PDF")
    dest = os.path.join(settings.UPLOAD_DIR, file.filename)
    content = await file.read()
    if len(content) > 200 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="PDF troppo grande (>200MB)")
    with open(dest, "wb") as f:
        f.write(content)
    n_chunks = ingest_pdf(dest)
    return {"ok": True, "filename": file.filename, "chunks": n_chunks}

@app.post("/query")
async def query(question: str = Form(...), k: Optional[int] = Form(None)):
    # Recupero
    try:
        triples = retrieve(question, k=k or settings.TOP_K)
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Indice non trovato o vuoto: {e}")
    context = format_context(triples)
    # Generazione
    answer = generate_answer(question, context)
    sources = [{"source": m["source"], "page": m["page"], "score": s} for _, m, s in triples]
    return JSONResponse({"answer": answer, "sources": sources})
