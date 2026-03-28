"""LLM factory — returns Groq (cloud) or Ollama (local) based on LLM_PROVIDER env var."""
from __future__ import annotations
from config import LLM_PROVIDER, GROQ_API_KEY, GROQ_MODEL_FAST, GROQ_MODEL_POWERFUL, OLLAMA_BASE_URL, OLLAMA_MODEL


def get_llm(mode: str = "powerful", temperature: float = 0.4, max_tokens: int = 4096, json_mode: bool = False):
    """
    mode: "powerful" (70b for strategy/content) | "fast" (8b for audience/images)
    Returns a LangChain chat model ready for ainvoke().
    """
    if LLM_PROVIDER == "groq":
        return _groq_llm(mode, temperature, max_tokens, json_mode)
    return _ollama_llm(temperature, max_tokens, json_mode)


def _groq_llm(mode: str, temperature: float, max_tokens: int, json_mode: bool):
    from langchain_groq import ChatGroq
    model = GROQ_MODEL_POWERFUL if mode == "powerful" else GROQ_MODEL_FAST
    kwargs: dict = dict(
        model=model,
        api_key=GROQ_API_KEY,
        temperature=temperature,
        max_tokens=max_tokens,
    )
    if json_mode:
        kwargs["model_kwargs"] = {"response_format": {"type": "json_object"}}
    return ChatGroq(**kwargs)


def _ollama_llm(temperature: float, max_tokens: int, json_mode: bool):
    from langchain_ollama import ChatOllama
    kwargs: dict = dict(
        model=OLLAMA_MODEL,
        base_url=OLLAMA_BASE_URL,
        temperature=temperature,
        num_predict=max_tokens,
    )
    if json_mode:
        kwargs["format"] = "json"
    return ChatOllama(**kwargs)
