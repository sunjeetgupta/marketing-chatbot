# Low Level Design — Marketing Campaign AI Chatbot

## 1. System Overview

The Marketing Campaign AI Chatbot is a multi-agent AI pipeline that takes a plain-English campaign brief and produces a complete marketing package: strategy, audience segments, email HTML, website landing page, and campaign imagery.

**Deployment:**
- Frontend → Vercel (https://frontend-ten-alpha-60.vercel.app)
- Backend → Railway (https://backend-production-c409.up.railway.app)

---

## 2. Architecture Components

| Layer | Technology | Purpose |
|---|---|---|
| Frontend | React + Vite + TailwindCSS | Chat UI, real-time progress, asset preview |
| Backend | FastAPI + LangGraph | API server, agent orchestration |
| LLM (Strategy / Content) | Groq — `llama-3.3-70b-versatile` | High-quality structured generation |
| LLM (Audience / Chat) | Groq — `llama-3.1-8b-instant` | Fast segment/follow-up generation |
| RAG | ChromaDB (ephemeral) + ONNX `all-MiniLM-L6-v2` | Marketing knowledge retrieval |
| Image URLs | picsum.photos + pravatar.cc | Deterministic placeholder imagery |
| Streaming | Server-Sent Events (SSE) | Real-time frontend updates |

---

## 3. E2E Request Flow — Sequence Diagram

```
User (Browser)          Frontend (React)           Backend (FastAPI)         LangGraph Pipeline
     |                        |                           |                          |
     |--- types brief ------->|                           |                          |
     |                        |-- POST /api/campaign/start|                          |
     |                        |   { user_input }          |                          |
     |                        |                           |-- create asyncio.Queue --|
     |                        |                           |-- spawn _run_campaign() -|
     |                        |<-- { campaign_id } -------|                          |
     |                        |                           |                          |
     |                        |-- GET /api/campaign/{id}/stream (SSE) ------------->|
     |                        |   (connection held open)  |                          |
     |                        |                           |                          |
     |                        |<-- event: connected ------|                          |
     |                        |                           |                          |
```

### 3.1 Strategy Agent

```
LangGraph                 StrategyAgent              ChromaDB (RAG)           Groq API
    |                          |                           |                      |
    |-- strategy_node() ------>|                           |                      |
    |                          |-- query_knowledge_base() >|                      |
    |                          |   (n=4, no filter)        |                      |
    |                          |<-- 4 marketing docs ------|                      |
    |                          |                           |                      |
    |                          |-- ainvoke([system, human]) -------------------- >|
    |                          |   Model: llama-3.3-70b-versatile                 |
    |                          |   json_mode: true                                |
    |                          |   max_tokens: 4096                               |
    |                          |<-- JSON: { campaign_name, campaign_type,         |
    |                          |           objectives, channels, phases, kpis }   |
    |                          |                           |                      |
    |<-- { strategy, current_step: "audience" } ----------|                      |
    |-- emit SSE: step_complete/strategy ----------------->|  (→ Frontend)        |
```

### 3.2 Audience Agent

```
LangGraph                 AudienceAgent              ChromaDB (RAG)           Groq API
    |                          |                           |                      |
    |-- audience_node() ------>|                           |                      |
    |                          |-- query_knowledge_base() >|                      |
    |                          |   (n=3, category="audience")                     |
    |                          |<-- 3 audience docs -------|                      |
    |                          |                           |                      |
    |                          |-- ainvoke([system, human]) -------------------- >|
    |                          |   Model: llama-3.1-8b-instant                    |
    |                          |   json_mode: true                                |
    |                          |   max_tokens: 4096                               |
    |                          |<-- JSON: { primary_segment, secondary_segment,   |
    |                          |           targeting_parameters, persona_narrative }|
    |                          |                           |                      |
    |<-- { audience, current_step: "content" } -----------|                      |
    |-- emit SSE: step_complete/audience ----------------->|  (→ Frontend)        |
```

### 3.3 Content Agent

```
LangGraph                 ContentAgent               ChromaDB (RAG)           Groq API
    |                          |                           |                      |
    |-- content_node() ------->|                           |                      |
    |                          |-- query_knowledge_base() >|                      |
    |                          |   (n=3, category="email_marketing")              |
    |                          |<-- 3 content docs --------|                      |
    |                          |                           |                      |
    |                          |-- _generate_content_json() -------------------- >|
    |                          |   Model: llama-3.3-70b-versatile                 |
    |                          |   json_mode: true                                |
    |                          |   Inputs: strategy + audience + RAG context      |
    |                          |<-- JSON: { subject_line, headline, body_copy,    |
    |                          |           cta, color_scheme, testimonials }       |
    |                          |                           |                      |
    |                          |-- render_email_html(content_json)                |
    |                          |   (Python template, picsum.photos for images)    |
    |                          |-- render_website_html(content_json)              |
    |                          |   (Python template, picsum.photos for images)    |
    |                          |                           |                      |
    |<-- { email_html, website_html, current_step: "images" } ------------------|
    |-- emit SSE: step_complete/content ----------------->|  (→ Frontend)         |
```

### 3.4 Image Agent

```
LangGraph                 ImageAgent                                          Groq API
    |                          |                                                   |
    |-- image_node() --------->|                                                   |
    |                          |-- ainvoke([system, human]) --------------------> |
    |                          |   Model: llama-3.1-8b-instant                    |
    |                          |   Generates: image keyword prompts for           |
    |                          |   hero, email, social, billboard                 |
    |                          |<-- JSON: { images: [{ type, prompt, keywords }] }|
    |                          |                                                   |
    |                          |-- Build picsum.photos URLs from keywords          |
    |                          |   (seed = sanitised keyword string)               |
    |                          |                                                   |
    |<-- { images, image_urls, current_step: "complete" } -------------------.   |
    |-- emit SSE: step_complete/images ----------------->|  (→ Frontend)      |   |
```

### 3.5 Finalize & Follow-up Chat

```
LangGraph                  Backend (FastAPI)          Frontend (React)
    |                           |                           |
    |-- finalize_node() ------->|                           |
    |   emit SSE: campaign_complete                         |
    |   (full payload: strategy, audience, html, images)    |
    |                           |-- SSE: campaign_complete ->|
    |                           |                           |-- render all panels
    |                           |-- SSE: stream_end ------->|
    |                           |   (queue sentinel = None) |-- close EventSource
    |                           |                           |
    |                           |                    user asks follow-up
    |                           |<-- POST /api/campaign/{id}/chat
    |                           |    { message }            |
    |                           |                           |
    |                           |-- ainvoke([system, human])|
    |                           |   Model: llama-3.1-8b-instant
    |                           |   System: campaign strategy context (1000 chars)
    |                           |<-- { response }           |
    |                           |-- 200 { response } ------>|
```

---

## 4. Data Models

### 4.1 MarketingState (LangGraph shared state)

```python
class MarketingState(TypedDict):
    messages:      list[BaseMessage]   # LangGraph message history
    user_input:    str                 # Original campaign brief
    campaign_id:   str                 # UUID for SSE routing
    strategy:      dict | None         # Output of StrategyAgent
    audience:      dict | None         # Output of AudienceAgent
    email_html:    str | None          # Rendered email template
    website_html:  str | None          # Rendered landing page
    images:        list[dict] | None   # Image metadata
    image_urls:    list[str] | None    # picsum.photos URLs
    current_step:  str                 # strategy|audience|content|images|complete|error
    error:         str | None          # Error message if any agent fails
```

### 4.2 SSE Event Schema

```json
{
  "type":    "connected|step_start|step_progress|step_complete|step_error|campaign_complete|stream_end|ping",
  "step":    "strategy|audience|content|images|done|init",
  "message": "human-readable description",
  "data":    null | { ...agent output }
}
```

### 4.3 Strategy JSON (output of StrategyAgent)

```json
{
  "campaign_name": "string",
  "campaign_type": "product_launch|brand_awareness|lead_gen|retention|seasonal",
  "objectives": ["string"],
  "target_market": "string",
  "unique_value_proposition": "string",
  "key_messages": ["string"],
  "channels": [{ "name": "string", "budget_pct": 20, "rationale": "string" }],
  "timeline_weeks": 8,
  "phases": [{ "phase": "string", "duration": "string", "activities": ["string"], "kpis": ["string"] }],
  "kpis": [{ "metric": "string", "target": "string", "measurement": "string" }],
  "success_metrics": { "primary": "string", "secondary": ["string"] },
  "risk_factors": ["string"],
  "competitive_advantages": ["string"]
}
```

### 4.4 Audience JSON (output of AudienceAgent)

```json
{
  "primary_segment": {
    "name": "string", "age_range": "string", "income_level": "string",
    "psychographics": { "values": [], "lifestyle": "string", "personality_traits": [] },
    "pain_points": [], "motivations": [], "buying_triggers": [],
    "preferred_channels": [], "estimated_market_size": "string"
  },
  "secondary_segment": { "name": "string", "age_range": "string", ... },
  "negative_audience": { "description": "string", "exclusions": [] },
  "targeting_parameters": { "demographic_targeting": [], "interest_targeting": [], ... },
  "persona_narrative": { "primary_day_in_life": "string", "key_insight": "string" },
  "audience_sizing": { "total_addressable_market": "string", "realistic_reach": "string" }
}
```

---

## 5. RAG Pipeline

```
query_knowledge_base(query, n_results, category_filter)
        |
        v
ChromaDB EphemeralClient
  Collection: "marketing_knowledge"
  Embedding:  DefaultEmbeddingFunction (ONNX all-MiniLM-L6-v2, 384-dim, cosine similarity)
  Documents:  16 seeded on startup (categories: strategy_framework, audience, email_marketing, content_strategy)
        |
        v
Top-N documents returned as plain text → injected into LLM prompt
```

---

## 6. Error Handling

| Scenario | Behaviour |
|---|---|
| Agent throws exception | Caught in node try/except → `error` set in state → SSE `step_error` emitted → downstream nodes skip via `if state.get("error"): return {"current_step": "error"}` |
| Groq returns invalid JSON | `_extract_json()` parses raw text → fallback `ainvoke` to fix JSON |
| SSE queue full (100 events) | Events silently dropped (`put_nowait` with except) |
| SSE timeout (120s per event) | Keepalive `ping` event sent to browser |
| Frontend SSE disconnect | `onerror` handler closes EventSource, shows error message |

---

## 7. Model Summary

| Agent | Model | Provider | Mode | Purpose |
|---|---|---|---|---|
| Strategy Agent | `llama-3.3-70b-versatile` | Groq | powerful | Campaign strategy JSON |
| Audience Agent | `llama-3.1-8b-instant` | Groq | fast | Audience segments JSON |
| Content Agent | `llama-3.3-70b-versatile` | Groq | powerful | Copy/content JSON → HTML |
| Image Agent | `llama-3.1-8b-instant` | Groq | fast | Image keyword generation |
| Follow-up Chat | `llama-3.1-8b-instant` | Groq | fast | Conversational Q&A |
| Embeddings | `all-MiniLM-L6-v2` (ONNX) | ChromaDB built-in | — | RAG vector search |
