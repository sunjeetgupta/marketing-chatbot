"""Image Agent — fast LLM picks keywords → picsum.photos (Fastly CDN) returns real photos."""
from __future__ import annotations

import json
import re
import urllib.parse
from typing import Any

from langchain_core.messages import HumanMessage, SystemMessage
from llm_factory import get_llm

PICSUM_BASE = "https://picsum.photos/seed"

FORMATS = [
    {"format": "email",   "name": "Email Hero Banner",  "width": 1200, "height": 400},
    {"format": "website", "name": "Website Hero Image",  "width": 1280, "height": 720},
    {"format": "social",  "name": "Social Media Square", "width": 1080, "height": 1080},
    {"format": "story",   "name": "Story / Reel",        "width": 720,  "height": 1280},
]


def _picsum(seed: str, w: int, h: int) -> str:
    clean = re.sub(r"[^a-zA-Z0-9_-]", "", seed.replace(" ", "_"))[:50]
    return f"{PICSUM_BASE}/{clean}/{w}/{h}"


def _extract_json_array(text: str) -> str:
    text = re.sub(r"```(?:json)?", "", text).strip().rstrip("`").strip()
    start = text.find("[")
    if start == -1:
        obj = text.find("{")
        if obj != -1:
            return f"[{text[obj:]}]"
        raise ValueError("No JSON array found")
    depth, end = 0, -1
    for i, ch in enumerate(text[start:], start):
        if ch == "[": depth += 1
        elif ch == "]":
            depth -= 1
            if depth == 0:
                end = i + 1
                break
    return text[start:end]


async def run_image_agent(strategy: dict[str, Any], audience: dict[str, Any]) -> dict[str, Any]:
    llm = get_llm(mode="fast", temperature=0.6, max_tokens=1024, json_mode=True)
    primary = audience.get("primary_segment", {})
    persona = audience.get("persona_narrative", {})
    name = strategy.get("campaign_name", "campaign")

    system = """You are a creative director selecting photo keywords for marketing campaigns.
Return ONLY a JSON array with exactly 4 objects:
[
  {"format": "email",   "name": "Email Hero Banner",  "keywords": ["word1", "word2", "word3"], "description": "one line"},
  {"format": "website", "name": "Website Hero Image",  "keywords": ["word1", "word2", "word3"], "description": "one line"},
  {"format": "social",  "name": "Social Media Square", "keywords": ["word1", "word2", "word3"], "description": "one line"},
  {"format": "story",   "name": "Story / Reel",        "keywords": ["word1", "word2", "word3"], "description": "one line"}
]
Keywords must be single English words suitable for image search."""

    prompt = f"""Campaign: {name}
Value proposition: {strategy.get('unique_value_proposition')}
Key messages: {', '.join(strategy.get('key_messages', [])[:3])}
Audience lifestyle: {primary.get('psychographics', {}).get('lifestyle', 'professional')}
Emotional driver: {persona.get('emotional_driver', 'success')}
Campaign type: {strategy.get('campaign_type', 'brand_awareness')}

Return ONLY the JSON array of 4 image specs."""

    response = await llm.ainvoke([SystemMessage(content=system), HumanMessage(content=prompt)])
    raw = response.content.strip()

    try:
        specs = json.loads(_extract_json_array(raw))
        specs = [s for s in specs if isinstance(s, dict)]
        if not specs:
            raise ValueError("empty")
    except Exception:
        specs = _fallback_specs(strategy)

    fmt_map = {f["format"]: f for f in FORMATS}
    images = []
    for idx, spec in enumerate(specs[:4]):
        fmt = fmt_map.get(spec.get("format", FORMATS[idx % 4]["format"]), FORMATS[idx % 4])
        kws = spec.get("keywords", ["marketing", "business", "people"])
        seed = "_".join(re.sub(r"[^a-zA-Z0-9]", "", k) for k in kws[:3]) + f"_{name[:10]}_{idx}"
        url = _picsum(seed, fmt["width"], fmt["height"])
        images.append({
            "name":    spec.get("name", fmt["name"]),
            "format":  fmt["format"],
            "prompt":  spec.get("description", ", ".join(kws)),
            "keywords": kws,
            "url":     url,
            "width":   fmt["width"],
            "height":  fmt["height"],
        })

    return {"images": images, "image_urls": [img["url"] for img in images]}


def _fallback_specs(strategy: dict) -> list[dict]:
    ctype = strategy.get("campaign_type", "brand")
    kw_map = {
        "product_launch": ["launch", "innovation", "product"],
        "brand_awareness": ["brand", "lifestyle", "people"],
        "lead_gen":        ["business", "growth", "professional"],
        "retention":       ["community", "loyalty", "happy"],
        "seasonal":        ["celebration", "seasonal", "festive"],
    }
    kws = kw_map.get(ctype, ["marketing", "business", "success"])
    return [
        {"format": "email",   "name": "Email Hero Banner",  "keywords": kws,                    "description": "Wide email banner"},
        {"format": "website", "name": "Website Hero Image",  "keywords": ["team"] + kws[:2],     "description": "Website hero"},
        {"format": "social",  "name": "Social Media Square", "keywords": ["people"] + kws[:2],   "description": "Social square"},
        {"format": "story",   "name": "Story / Reel",        "keywords": ["mobile"] + kws[:2],   "description": "Story format"},
    ]
