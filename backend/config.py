from __future__ import annotations
import os
from dotenv import load_dotenv

load_dotenv()

# ── LLM provider: "groq" (cloud, fast, free) or "ollama" (local) ──
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "groq").lower()

# Groq (cloud, free tier)
GROQ_API_KEY        = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL_FAST     = os.getenv("GROQ_MODEL_FAST",  "llama-3.1-8b-instant")      # audience (speed)
GROQ_MODEL_POWERFUL = os.getenv("GROQ_MODEL_POWERFUL", "llama-3.1-70b-versatile") # strategy/content

# Ollama (local fallback)
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL    = os.getenv("OLLAMA_MODEL", "qwen2.5:7b")

# RAG
CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", "./chroma_db")
# Set to "memory" on cloud platforms with ephemeral filesystems
CHROMA_MODE = os.getenv("CHROMA_MODE", "persist")  # "persist" | "memory"
