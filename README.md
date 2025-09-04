# 🗂️ RAG PDF Assistant

A lightweight Retrieval-Augmented Generation (RAG) system that lets you query PDF documents using a local LLM.  
Built with **FastAPI**, **LangChain**, **Ollama**.  
Dockerized for easy deployment.



---

## 🚀 Features
- 📄 Ingest one or multiple PDF files  
- 🔍 Semantic search with FAISS
- 🌐 REST API endpoints with FastAPI  
- 🐳 Docker-ready

---

## 🛠️ Requirements
- Python 3.10+  
- `pip install -r requirements.txt`
- (Optional) Docker

---

## ▶️ Usage

### 1. Ingest PDFs

 ```
 python app/ingest.py data/mydoc.pdf
 ```

### 2. Start API

 ```
bash
uvicorn app.api:app --reload
 ```
### 3. Test Endpoints

- Interface → http://127.0.0.1:8000/docs
- Healthcheck → http://127.0.0.1:8000/health
- Query → POST http://127.0.0.1:8000/query with JSON:
- 
 ```
{
  "question": "What does the document say about X?"
}
 ```

## 🐳 Run with Docker

Build and run:

docker build -t rag-pdf .
docker run -p 8000:8000 rag-pdf

## 📌 Notes

Designed for local, offline RAG — no API keys required.