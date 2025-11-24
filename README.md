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

### 1. Start API

 ```
bash
uvicorn app.main:app --reload
 ```

### 2. Ingest PDFs

Use the `/ingest` endpoint to upload PDF documents.

 ```
 curl -X POST "http://127.0.0.1:8000/ingest" -H "accept: application/json" -H "Content-Type: multipart/form-data" -F "file=@/path/to/your/document.pdf"
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

 ```
docker compose up --build
 ```

## 📌 Notes

Designed for local, offline RAG — no API keys required.
