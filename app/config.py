import os

class Settings:
    INDEX_DIR = "./index"
    UPLOAD_DIR = "./uploads"
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
