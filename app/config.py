import os

class Settings:
    # Allow env var overrides, default to Docker paths if not set, or local defaults if running locally
    # Ideally, for local dev without docker, one might want ./index.
    # But to match Dockerfile logic, let's use the env vars if provided.
    INDEX_DIR = os.getenv("INDEX_DIR", "/app/storage/index")
    UPLOAD_DIR = os.getenv("UPLOAD_DIR", "/app/storage/uploads")

    # If running locally without /app existing, fallback to relative paths could be useful
    # but let's stick to the plan of aligning with Docker.
    # Users running locally should set env vars or we can check if /app exists.
    # A safer default for local dev might be "./storage/index"
    if not os.path.exists("/app") and INDEX_DIR == "/app/storage/index":
         INDEX_DIR = "./storage/index"
    if not os.path.exists("/app") and UPLOAD_DIR == "/app/storage/uploads":
         UPLOAD_DIR = "./storage/uploads"

    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
    CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "1000"))
    CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "150"))
    TOP_K = int(os.getenv("TOP_K", "4"))

    LLM_PROVIDER = os.getenv("LLM_PROVIDER", "ollama")  # "openai" | "ollama"
    LLM_MODEL = os.getenv("LLM_MODEL", "llama3.2:1b")   # es. "gpt-4o-mini"
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434") #OLLAMA_BASE_URL=http://ollama:11434


settings = Settings()
os.makedirs(settings.INDEX_DIR, exist_ok=True)
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
