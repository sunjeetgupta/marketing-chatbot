"""Strategy Agent — powerful LLM + RAG → structured campaign strategy JSON."""
from __future__ import annotations

import json
import re
from typing import Any

from langchain_core.messages import HumanMessage, SystemMessage
from llm_factory import get_llm
from rag.vector_store import query_knowledge_base


SYSTEM_PROMPT = """You are a senior marketing strategist. Create a comprehensive campaign strategy.
Return ONLY a valid JSON object — no explanation, no markdown fences.
Use this exact structure:
{
  "campaign_name": "string",
  "campaign_type": "product_launch|brand_awareness|lead_gen|retention|seasonal",
  "objectives": ["string"],
  "target_market": "string",
  "unique_value_proposition": "string",
  "key_messages": ["string"],
  "channels": [{"name": "string", "budget_pct": 20, "rationale": "string"}],
  "timeline_weeks": 8,
  "phases": [{"phase": "string", "duration": "string", "activities": ["string"], "kpis": ["string"]}],
  "kpis": [{"metric": "string", "target": "string", "measurement": "string"}],
  "success_metrics": {"primary": "string", "secondary": ["string"]},
  "risk_factors": ["string"],
  "competitive_advantages": ["string"]
}"""


def _extract_json(text: str) -> str:
    text = re.sub(r"```(?:json)?", "", text).strip()
    start = text.find("{")
    if start == -1:
        raise ValueError("No JSON object found")
    depth, end = 0, -1
    for i, ch in enumerate(text[start:], start):
        if ch == "{": depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                end = i + 1
                break
    return text[start:end]


async def run_strategy_agent(user_input: str, campaign_id: str) -> dict[str, Any]:
    llm = get_llm(mode="powerful", temperature=0.3, max_tokens=4096, json_mode=True)

    rag_docs = query_knowledge_base(user_input, n_results=4)
    rag_context = "\n\n---\n\n".join(rag_docs)

    prompt = f"""Campaign Brief:
{user_input}

Marketing Knowledge (use this to inform the strategy):
{rag_context}

Return ONLY the JSON strategy object."""

    response = await llm.ainvoke([
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=prompt),
    ])

    raw = response.content.strip()
    try:
        return json.loads(_extract_json(raw))
    except Exception:
        fix = await llm.ainvoke([
            HumanMessage(content=f"Fix this to be valid JSON, return only the JSON object:\n{raw[:2000]}")
        ])
        return json.loads(_extract_json(fix.content.strip()))
