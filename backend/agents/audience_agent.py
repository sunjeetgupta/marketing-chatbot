"""Audience Agent — fast LLM + RAG → structured audience segments JSON."""
from __future__ import annotations

import json
import re
from typing import Any

from langchain_core.messages import HumanMessage, SystemMessage
from llm_factory import get_llm
from rag.vector_store import query_knowledge_base


SYSTEM_PROMPT = """You are an expert audience researcher. Define precise audience segments.
Return ONLY a valid JSON object — no explanation, no markdown fences.
Use this exact structure:
{
  "primary_segment": {
    "name": "string", "description": "string", "age_range": "string",
    "gender_split": "string", "income_level": "string", "education": "string",
    "location": "string",
    "psychographics": {"values": ["string"], "lifestyle": "string", "personality_traits": ["string"]},
    "pain_points": ["string"], "motivations": ["string"], "buying_triggers": ["string"],
    "preferred_channels": ["string"], "content_preferences": ["string"],
    "estimated_market_size": "string"
  },
  "secondary_segment": {
    "name": "string", "description": "string", "age_range": "string",
    "gender_split": "string", "income_level": "string", "location": "string",
    "psychographics": {"values": ["string"], "lifestyle": "string"},
    "pain_points": ["string"], "motivations": ["string"], "preferred_channels": ["string"]
  },
  "negative_audience": {"description": "string", "exclusions": ["string"]},
  "targeting_parameters": {
    "demographic_targeting": ["string"], "interest_targeting": ["string"],
    "behavioral_targeting": ["string"], "lookalike_seed_audience": "string",
    "custom_audience_strategy": "string"
  },
  "persona_narrative": {
    "primary_day_in_life": "string", "key_insight": "string", "emotional_driver": "string"
  },
  "audience_sizing": {
    "total_addressable_market": "string", "serviceable_market": "string", "realistic_reach": "string"
  }
}"""


def _extract_json(text: str) -> str:
    text = re.sub(r"```(?:json)?", "", text).strip()
    start = text.find("{")
    if start == -1:
        raise ValueError("No JSON found")
    depth, end = 0, -1
    for i, ch in enumerate(text[start:], start):
        if ch == "{": depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                end = i + 1
                break
    return text[start:end]


async def run_audience_agent(strategy: dict[str, Any]) -> dict[str, Any]:
    llm = get_llm(mode="fast", temperature=0.4, max_tokens=4096, json_mode=True)

    query = f"{strategy.get('campaign_name', '')} {strategy.get('target_market', '')}"
    rag_docs = query_knowledge_base(query, n_results=3, category_filter="audience")
    rag_context = "\n\n---\n\n".join(rag_docs)

    prompt = f"""Campaign context:
- Name: {strategy.get('campaign_name')}
- Type: {strategy.get('campaign_type')}
- Target Market: {strategy.get('target_market')}
- UVP: {strategy.get('unique_value_proposition')}
- Key Messages: {', '.join(strategy.get('key_messages', [])[:3])}
- Channels: {', '.join(c['name'] for c in strategy.get('channels', [])[:3])}

Audience knowledge:
{rag_context}

Return ONLY the JSON audience object."""

    response = await llm.ainvoke([
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=prompt),
    ])

    raw = response.content.strip()
    try:
        result = json.loads(_extract_json(raw))
    except Exception:
        fix = await llm.ainvoke([
            HumanMessage(content=f"Fix this to be valid JSON:\n{raw[:2000]}")
        ])
        result = json.loads(_extract_json(fix.content.strip()))

    from config import LLM_PROVIDER, GROQ_MODEL_FAST, OLLAMA_MODEL
    result["_llm_used"] = LLM_PROVIDER
    result["_llm_model"] = GROQ_MODEL_FAST if LLM_PROVIDER == "groq" else OLLAMA_MODEL
    return result
