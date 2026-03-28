"""LangChain tools available to marketing agents."""

from langchain_core.tools import tool
from rag.vector_store import query_knowledge_base


@tool
def query_marketing_knowledge(query: str, category: str = "") -> str:
    """Query the marketing knowledge base using semantic search.

    Args:
        query: The marketing question or topic to search for.
        category: Optional filter — one of: strategy_framework, channel_strategy,
                  audience, email_marketing, website, metrics, budget_planning,
                  content_strategy, social_media.

    Returns:
        Relevant marketing knowledge excerpts.
    """
    docs = query_knowledge_base(query, n_results=3, category_filter=category or None)
    if not docs:
        return "No relevant knowledge found for this query."
    return "\n\n---\n\n".join(docs)


@tool
def get_industry_benchmarks(industry: str) -> str:
    """Get marketing benchmarks and KPI targets for a specific industry.

    Args:
        industry: The industry name (e.g., SaaS, E-commerce, Healthcare, Finance, Retail).

    Returns:
        Industry-specific marketing benchmarks.
    """
    benchmarks = {
        "saas": {
            "email_open_rate": "22-28%",
            "email_ctr": "2.5-4%",
            "landing_page_cvr": "5-15%",
            "cac": "$200-$1,500",
            "trial_to_paid": "15-25%",
            "monthly_churn": "2-5%",
            "cac_payback": "12-18 months",
            "ltv_cac_ratio": "3:1 minimum",
        },
        "e-commerce": {
            "email_open_rate": "18-22%",
            "email_ctr": "2-3%",
            "cart_abandonment": "70-75%",
            "landing_page_cvr": "2-4%",
            "average_order_value": "$50-$150",
            "roas_target": "4:1 minimum",
            "returning_customer_rate": "25-35%",
        },
        "healthcare": {
            "email_open_rate": "25-30%",
            "email_ctr": "3-5%",
            "landing_page_cvr": "3-6%",
            "cpc_search": "$5-$15",
            "compliance_note": "HIPAA compliant messaging required",
        },
        "finance": {
            "email_open_rate": "24-28%",
            "email_ctr": "2.5-4%",
            "landing_page_cvr": "4-8%",
            "cpc_search": "$10-$50 (highly competitive)",
            "compliance_note": "Regulatory disclaimers required",
        },
        "retail": {
            "email_open_rate": "18-24%",
            "email_ctr": "2-3.5%",
            "landing_page_cvr": "1.5-3%",
            "roas_target": "5:1 for paid",
            "seasonal_multiplier": "Q4 budget should be 2-3x baseline",
        },
    }
    key = industry.lower().replace("-", "").replace(" ", "")
    data = benchmarks.get(key, benchmarks.get("e-commerce"))
    lines = [f"**{industry.title()} Industry Benchmarks:**"]
    for metric, value in data.items():
        label = metric.replace("_", " ").title()
        lines.append(f"- {label}: {value}")
    return "\n".join(lines)


@tool
def analyze_campaign_brief(brief: str) -> str:
    """Analyze a campaign brief and extract key information.

    Args:
        brief: The raw campaign brief or user description.

    Returns:
        Structured analysis of the brief with extracted key information.
    """
    return f"""Campaign Brief Analysis:
Brief provided: {brief}

Extraction framework applied:
1. Product/Service: Identify what is being marketed
2. Business Model: B2B, B2C, or hybrid
3. Target Market: Primary customer segment
4. Campaign Objective: Awareness, lead gen, conversion, or retention
5. Competitive Context: Positioning relative to alternatives
6. Unique Value Proposition: Key differentiator
7. Campaign Constraints: Budget, timeline, regulatory considerations

Please use this analysis to inform strategy development."""


@tool
def generate_campaign_timeline(duration_weeks: int, campaign_type: str) -> str:
    """Generate a phased campaign timeline.

    Args:
        duration_weeks: Total campaign duration in weeks.
        campaign_type: Type of campaign (e.g., product_launch, brand_awareness, lead_gen).

    Returns:
        A phased campaign timeline with activities per phase.
    """
    phases = []
    if campaign_type == "product_launch":
        phases = [
            (f"Week 1-{max(1, duration_weeks//4)}", "Pre-launch: Teaser content, landing page, email list building, influencer seeding"),
            (f"Week {duration_weeks//4+1}-{duration_weeks//2}", "Launch Week: Full media push, press release, social campaign, email blast"),
            (f"Week {duration_weeks//2+1}-{int(duration_weeks*0.75)}", "Amplification: Retargeting, case studies, user testimonials, paid scale-up"),
            (f"Week {int(duration_weeks*0.75)+1}-{duration_weeks}", "Optimization: A/B test learnings, double down on winners, nurture sequences"),
        ]
    elif campaign_type == "lead_gen":
        phases = [
            (f"Week 1-{max(1, duration_weeks//4)}", "Setup: Landing pages, lead magnets, tracking, CRM integration"),
            (f"Week {duration_weeks//4+1}-{duration_weeks//2}", "Acquisition: Paid campaigns live, content distribution, SEO push"),
            (f"Week {duration_weeks//2+1}-{int(duration_weeks*0.75)}", "Nurture: Email automation, webinars, sales handoff"),
            (f"Week {int(duration_weeks*0.75)+1}-{duration_weeks}", "Optimization: Iterate on best-performing channels, scale winners"),
        ]
    else:
        phases = [
            (f"Week 1-{max(1, duration_weeks//3)}", "Foundation: Creative production, channel setup, audience building"),
            (f"Week {duration_weeks//3+1}-{int(duration_weeks*0.66)}", "Execution: Campaign live, monitoring, initial optimization"),
            (f"Week {int(duration_weeks*0.66)+1}-{duration_weeks}", "Optimization: Performance analysis, creative refresh, budget reallocation"),
        ]
    return "\n".join([f"**{phase}**: {activities}" for phase, activities in phases])
