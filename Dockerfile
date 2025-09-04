FROM ubuntu:latest
LABEL authors="zinga"

ENTRYPOINT ["top", "-b"]

FROM python:3.11-slim

# Evita prompt interattivi
ENV DEBIAN_FRONTEND=noninteractive \
    PIP_NO_CACHE_DIR=1

# Dipendenze di base
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential git curl && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Requisiti
COPY requirements.txt .
# Torch CPU (necessario per sentence-transformers)
RUN pip install --upgrade pip && \
    pip install torch --index-url https://download.pytorch.org/whl/cpu && \
    pip install -r requirements.txt

# Codice
COPY app ./app

# Storage per indici e upload
RUN mkdir -p /app/storage/index /app/storage/uploads

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]