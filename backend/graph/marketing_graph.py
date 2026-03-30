"""LangGraph orchestration of marketing campaign agents."""
from __future__ import annotations

import asyncio
from typing import TypedDict, Annotated, Optional, Any
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage, AIMessage

from agents.strategy_agent import run_strategy_agent
from agents.audience_agent import run_audience_agent
from agents.content_agent import run_content_agent
from agents.image_agent import run_image_agent


# ─── Shared State ──────────────────────────────────────────────────────────────

class MarketingState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    user_input: str
    campaign_id: str
    strategy: Optional[dict[str, Any]]
    audience: Optional[dict[str, Any]]
    email_html: Optional[str]
    website_html: Optional[str]
    images: Optional[list[dict]]
    image_urls: Optional[list[str]]
    current_step: str
    error: Optional[str]


# ─── Node Functions ─────────────────────────────────────────────────────────────

async def strategy_node(state: MarketingState) -> dict:
    """Agent 1: Generate campaign strategy using Claude + RAG."""
    campaign_id = state["campaign_id"]
    _emit(campaign_id, "step_start", "strategy", "Analyzing campaign brief and creating strategy...")

    try:
        strategy = await run_strategy_agent(state["user_input"], campaign_id)
        _emit(campaign_id, "step_complete", "strategy", "Campaign strategy created.", data=strategy)
        return {
            "strategy": strategy,
            "current_step": "audience",
            "messages": [AIMessage(content=f"Campaign strategy '{strategy.get('campaign_name', 'Campaign')}' created successfully.")],
        }
    except Exception as e:
        _emit(campaign_id, "step_error", "strategy", f"Strategy generation failed: {str(e)}")
        return {"error": str(e), "current_step": "error"}


async def audience_node(state: MarketingState) -> dict:
    """Agent 2: Define target audience using Ollama (open-source LLM) + RAG."""
    campaign_id = state["campaign_id"]
    _emit(campaign_id, "step_start", "audience", "Defining target audience segments...")

    if state.get("error"):
        return {"current_step": "error"}

    try:
        audience = await run_audience_agent(state["strategy"])
        llm_used = audience.get("_llm_used", "unknown")
        _emit(campaign_id, "step_complete", "audience", f"Audience defined (using {llm_used}).", data=audience)
        return {
            "audience": audience,
            "current_step": "content",
            "messages": [AIMessage(content=f"Target audience '{audience.get('primary_segment', {}).get('name', 'Segment')}' defined.")],
        }
    except Exception as e:
        _emit(campaign_id, "step_error", "audience", f"Audience definition failed: {str(e)}")
        return {"error": str(e), "current_step": "error"}


async def content_node(state: MarketingState) -> dict:
    """Agent 3: Generate Email and Website HTML using Claude."""
    campaign_id = state["campaign_id"]
    _emit(campaign_id, "step_start", "content", "Generating email and website content...")

    if state.get("error"):
        return {"current_step": "error"}

    try:
        _emit(campaign_id, "step_progress", "content", "Generating email HTML...")
        content = await run_content_agent(state["strategy"], state["audience"])

        _emit(campaign_id, "step_complete", "content", "Email and website HTML generated.", data={
            "email_preview": content["email_html"][:200] + "...",
            "website_preview": content["website_html"][:200] + "...",
        })
        return {
            "email_html": content["email_html"],
            "website_html": content["website_html"],
            "current_step": "images",
            "messages": [AIMessage(content="Email and website HTML templates generated.")],
        }
    except Exception as e:
        _emit(campaign_id, "step_error", "content", f"Content generation failed: {str(e)}")
        return {"error": str(e), "current_step": "error"}


async def image_node(state: MarketingState) -> dict:
    """Agent 4: Generate campaign imagery using Claude prompts + Pollinations.ai (Flux)."""
    campaign_id = state["campaign_id"]
    _emit(campaign_id, "step_start", "images", "Creating campaign imagery with AI...")

    if state.get("error"):
        return {"current_step": "error"}

    try:
        result = await run_image_agent(state["strategy"], state["audience"])
        _emit(campaign_id, "step_complete", "images", f"Generated {len(result['images'])} campaign images.", data=result)
        return {
            "images": result["images"],
            "image_urls": result["image_urls"],
            "current_step": "complete",
            "messages": [AIMessage(content=f"Generated {len(result['images'])} campaign images for email, website, and social media.")],
        }
    except Exception as e:
        _emit(campaign_id, "step_error", "images", f"Image generation failed: {str(e)}")
        return {"error": str(e), "current_step": "error"}


async def finalize_node(state: MarketingState) -> dict:
    """Final node: emit campaign_complete event."""
    campaign_id = state["campaign_id"]
    _emit(campaign_id, "campaign_complete", "done", "Campaign creation complete!", data={
        "strategy": state.get("strategy"),
        "audience": state.get("audience"),
        "email_html": state.get("email_html"),
        "website_html": state.get("website_html"),
        "images": state.get("images"),
        "image_urls": state.get("image_urls"),
    })
    return {"current_step": "complete"}


def should_continue(state: MarketingState) -> str:
    if state.get("error"):
        return "error_end"
    return "continue"


# ─── Event Queue System ──────────────────────────────────────────────────────────

# Global dict of campaign_id -> asyncio.Queue for SSE events
campaign_queues: dict[str, asyncio.Queue] = {}


def _emit(campaign_id: str, event_type: str, step: str, message: str, data: Any = None) -> None:
    """Put an event into the campaign's SSE queue."""
    queue = campaign_queues.get(campaign_id)
    if queue:
        event = {
            "type": event_type,
            "step": step,
            "message": message,
            "data": data,
        }
        try:
            queue.put_nowait(event)
        except asyncio.QueueFull:
            pass


# ─── Graph Compilation ──────────────────────────────────────────────────────────

def build_marketing_graph() -> Any:
    builder = StateGraph(MarketingState)

    builder.add_node("run_strategy", strategy_node)
    builder.add_node("run_audience", audience_node)
    builder.add_node("run_content", content_node)
    builder.add_node("run_images", image_node)
    builder.add_node("run_finalize", finalize_node)

    builder.add_edge(START, "run_strategy")
    builder.add_edge("run_strategy", "run_audience")
    builder.add_edge("run_audience", "run_content")
    builder.add_edge("run_content", "run_images")
    builder.add_edge("run_images", "run_finalize")
    builder.add_edge("run_finalize", END)

    return builder.compile()


# Singleton compiled graph
_marketing_graph = None


def get_marketing_graph():
    global _marketing_graph
    if _marketing_graph is None:
        _marketing_graph = build_marketing_graph()
    return _marketing_graph
