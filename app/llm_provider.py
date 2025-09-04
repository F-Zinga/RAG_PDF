import json
import requests
from typing import Dict
from .config import settings
from .prompt import SYSTEM_INSTRUCTION, USER_TEMPLATE

def build_prompt(question: str, context: str) -> str:
    # Prompt unico (funziona per Ollama generate/chat e per OpenAI chat)
    return f"{SYSTEM_INSTRUCTION}\n\n" + USER_TEMPLATE.format(question=question, context=context)

def openai_chat(prompt: str) -> str:
    if not settings.OPENAI_API_KEY:
        raise RuntimeError("OPENAI_API_KEY non impostata")
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
        "Content-Type": "application/json",
    }
    body = {
        "model": settings.LLM_MODEL,
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.1,
    }
    r = requests.post(url, headers=headers, data=json.dumps(body), timeout=120)
    r.raise_for_status()
    return r.json()["choices"][0]["message"]["content"]

def ollama_chat(prompt: str) -> str:
    url = f"{settings.OLLAMA_BASE_URL}/api/chat"
    body = {"model": settings.LLM_MODEL, "messages": [{"role": "user", "content": prompt}], "stream": False}
    r = requests.post(url, json=body, timeout=300)
    r.raise_for_status()
    data = r.json()
    # Ollama /api/chat risponde con {'message': {'content': '...'}}
    if "message" in data and "content" in data["message"]:
        return data["message"]["content"]
    # fallback per /api/generate
    if "response" in data:
        return data["response"]
    return str(data)

def generate_answer(question: str, context: str) -> str:
    prompt = build_prompt(question, context)
    if settings.LLM_PROVIDER.lower() == "openai":
        return openai_chat(prompt)
    return ollama_chat(prompt)
