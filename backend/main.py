"""FastAPI backend with SSE streaming for the marketing campaign chatbot."""
from __future__ import annotations

import asyncio
from typing import Optional
import json
import uuid
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from langchain_core.messages import HumanMessage

from graph.marketing_graph import get_marketing_graph, campaign_queues, MarketingState
from rag.vector_store import get_collection


# ─── Lifespan ──────────────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Initializing RAG vector store...")
    try:
        get_collection()
        print("RAG vector store ready.")
    except Exception as e:
        print(f"RAG init warning: {e}")
    print("Pre-compiling LangGraph...")
    get_marketing_graph()
    print("Server ready.")
    yield
    print("Shutting down.")


# ─── App Setup ─────────────────────────────────────────────────────────────────

app = FastAPI(
    title="Marketing Campaign AI API",
    description="AI-powered marketing campaign generation with LangGraph, Claude, and RAG",
    version="1.0.0",
    lifespan=lifespan,
)

import os as _os
_FRONTEND_URL = _os.getenv("FRONTEND_URL", "")
_ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://localhost:3000",
    "http://127.0.0.1:5173",
]
if _FRONTEND_URL:
    _ALLOWED_ORIGINS.append(_FRONTEND_URL)

app.add_middleware(
    CORSMiddleware,
    allow_origins=_ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory campaign results store
campaign_results: dict[str, dict] = {}


# ─── Models ────────────────────────────────────────────────────────────────────

class CampaignRequest(BaseModel):
    user_input: str
    campaign_id: Optional[str] = None


class ChatMessage(BaseModel):
    campaign_id: str
    message: str


# ─── Endpoints ─────────────────────────────────────────────────────────────────

@app.get("/health")
async def health():
    return {"status": "ok", "message": "Marketing AI is running"}


@app.post("/api/campaign/start")
async def start_campaign(request: CampaignRequest):
    """Start a new marketing campaign generation and return a campaign_id."""
    campaign_id = request.campaign_id or str(uuid.uuid4())

    # Create SSE queue for this campaign
    queue: asyncio.Queue = asyncio.Queue(maxsize=100)
    campaign_queues[campaign_id] = queue
    campaign_results[campaign_id] = {"status": "running"}

    # Run the LangGraph pipeline in the background
    asyncio.create_task(_run_campaign(campaign_id, request.user_input))

    return {"campaign_id": campaign_id, "status": "started"}


async def _run_campaign(campaign_id: str, user_input: str) -> None:
    """Background task: run the LangGraph campaign pipeline."""
    graph = get_marketing_graph()
    initial_state: MarketingState = {
        "messages": [HumanMessage(content=user_input)],
        "user_input": user_input,
        "campaign_id": campaign_id,
        "strategy": None,
        "audience": None,
        "email_html": None,
        "website_html": None,
        "images": None,
        "image_urls": None,
        "current_step": "strategy",
        "error": None,
    }
    try:
        final_state = await graph.ainvoke(initial_state)
        campaign_results[campaign_id] = {
            "status": "complete",
            "strategy": final_state.get("strategy"),
            "audience": final_state.get("audience"),
            "email_html": final_state.get("email_html"),
            "website_html": final_state.get("website_html"),
            "images": final_state.get("images"),
            "image_urls": final_state.get("image_urls"),
        }
    except Exception as e:
        campaign_results[campaign_id] = {"status": "error", "error": str(e)}
        queue = campaign_queues.get(campaign_id)
        if queue:
            await queue.put({"type": "fatal_error", "step": "pipeline", "message": str(e), "data": None})
    finally:
        # Signal SSE stream to end
        queue = campaign_queues.get(campaign_id)
        if queue:
            await queue.put(None)  # Sentinel


@app.get("/api/campaign/{campaign_id}/stream")
async def stream_campaign(campaign_id: str):
    """SSE endpoint — streams campaign generation events to the frontend."""
    queue = campaign_queues.get(campaign_id)
    if not queue:
        raise HTTPException(status_code=404, detail="Campaign not found or already completed.")

    async def event_generator() -> AsyncGenerator[str, None]:
        yield f"data: {json.dumps({'type': 'connected', 'step': 'init', 'message': 'Connected to campaign stream', 'data': None})}\n\n"
        try:
            while True:
                try:
                    event = await asyncio.wait_for(queue.get(), timeout=120.0)
                    if event is None:
                        yield f"data: {json.dumps({'type': 'stream_end', 'step': 'done', 'message': 'Campaign complete', 'data': None})}\n\n"
                        break
                    yield f"data: {json.dumps(event)}\n\n"
                except asyncio.TimeoutError:
                    yield f"data: {json.dumps({'type': 'ping', 'step': 'alive', 'message': 'keepalive', 'data': None})}\n\n"
        finally:
            campaign_queues.pop(campaign_id, None)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@app.get("/api/campaign/{campaign_id}/result")
async def get_campaign_result(campaign_id: str):
    """Get the final campaign result (for polling fallback)."""
    result = campaign_results.get(campaign_id)
    if not result:
        raise HTTPException(status_code=404, detail="Campaign not found.")
    return result


@app.post("/api/campaign/{campaign_id}/chat")
async def campaign_chat(campaign_id: str, msg: ChatMessage):
    """Follow-up chat on an existing campaign."""
    from langchain_core.messages import HumanMessage, SystemMessage
    from llm_factory import get_llm

    result = campaign_results.get(campaign_id, {})
    strategy = result.get("strategy", {})

    llm = get_llm(mode="fast", temperature=0.5, max_tokens=1024)
    system = f"""You are a marketing expert assistant helping a user refine and understand their campaign.
Campaign context: {json.dumps(strategy, indent=2)[:1000]}
Answer concisely and helpfully."""

    response = await llm.ainvoke([SystemMessage(content=system), HumanMessage(content=msg.message)])
    return {"response": response.content}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
