"""Content Agent — Qwen generates content JSON → Python renders into polished HTML templates.

Architecture:
  1. Qwen generates structured content (headlines, copy, colors) as JSON
  2. Python renders that content into pre-built, pixel-perfect HTML templates
  3. Images served by picsum.photos (fastly CDN, always 200, seed-based consistency)
"""
from __future__ import annotations

import json
import re
from typing import Any

from langchain_core.messages import HumanMessage, SystemMessage

from llm_factory import get_llm
from rag.vector_store import query_knowledge_base


# ─── LLM ──────────────────────────────────────────────────────────────────────

def _llm():
    return get_llm(mode="powerful", temperature=0.4, max_tokens=3000, json_mode=True)


def _extract_json(text: str) -> dict:
    text = re.sub(r"```(?:json)?", "", text).strip().rstrip("`").strip()
    start = text.find("{")
    end = text.rfind("}") + 1
    if start >= 0 and end > start:
        text = text[start:end]
    return json.loads(text)


# ─── Image helpers ────────────────────────────────────────────────────────────
# picsum.photos: Fastly CDN, always returns HTTP 200, seed gives consistent images

def _picsum(seed: str, w: int, h: int) -> str:
    """Return a consistent, always-loading picsum photo URL for a given seed."""
    clean_seed = re.sub(r"[^a-zA-Z0-9_-]", "", seed.replace(" ", "_"))[:40]
    return f"https://picsum.photos/seed/{clean_seed}/{w}/{h}"

def _pravatar(seed: str, size: int = 80) -> str:
    """Return a consistent avatar image URL."""
    return f"https://i.pravatar.cc/{size}?u={seed}"


# ─── Content JSON generation via Qwen ─────────────────────────────────────────

async def _generate_content_json(strategy: dict[str, Any], audience: dict[str, Any]) -> dict:
    """Ask Qwen for copy/content only — no HTML."""
    llm = _llm()
    primary = audience.get("primary_segment", {})
    persona = audience.get("persona_narrative", {})

    campaign_type = strategy.get("campaign_type", "brand_awareness")
    color_map = {
        "product_launch": {"primary": "#6366f1", "dark": "#4338ca", "accent": "#a78bfa", "text_on": "#ffffff"},
        "brand_awareness": {"primary": "#0f766e", "dark": "#0d5c56", "accent": "#2dd4bf", "text_on": "#ffffff"},
        "lead_gen":        {"primary": "#0369a1", "dark": "#075985", "accent": "#38bdf8", "text_on": "#ffffff"},
        "retention":       {"primary": "#b45309", "dark": "#92400e", "accent": "#fbbf24", "text_on": "#ffffff"},
        "seasonal":        {"primary": "#be185d", "dark": "#9d174d", "accent": "#f472b6", "text_on": "#ffffff"},
    }
    colors = color_map.get(campaign_type, color_map["product_launch"])

    prompt = f"""Generate marketing copy for this campaign. Return ONLY valid JSON.

Campaign: {strategy.get('campaign_name')}
Value proposition: {strategy.get('unique_value_proposition')}
Key messages: {', '.join(strategy.get('key_messages', [])[:4])}
Advantages: {', '.join(strategy.get('competitive_advantages', [])[:3])}
Audience: {primary.get('name')} | Pain points: {', '.join(primary.get('pain_points', [])[:3])}
Emotional driver: {persona.get('emotional_driver', '')}

Return this exact JSON structure:
{{
  "hero_eyebrow": "short 3-4 word badge text e.g. New Collection 2025",
  "hero_headline": "powerful 6-10 word headline addressing the main pain point",
  "hero_subheadline": "compelling 15-20 word subheadline explaining the value",
  "cta_primary": "3-4 word CTA button text",
  "cta_secondary": "3-4 word secondary CTA",
  "benefits": [
    {{"icon": "single emoji", "title": "3-4 word title", "desc": "15-20 word benefit description"}},
    {{"icon": "single emoji", "title": "3-4 word title", "desc": "15-20 word benefit description"}},
    {{"icon": "single emoji", "title": "3-4 word title", "desc": "15-20 word benefit description"}}
  ],
  "features": [
    {{"icon": "emoji", "title": "feature name", "headline": "5-7 word feature headline", "desc": "20-25 word description", "bullets": ["point 1", "point 2", "point 3"]}},
    {{"icon": "emoji", "title": "feature name", "headline": "5-7 word feature headline", "desc": "20-25 word description", "bullets": ["point 1", "point 2", "point 3"]}}
  ],
  "testimonials": [
    {{"quote": "20-25 word authentic testimonial quote", "name": "First Last", "role": "Job Title", "company": "Company Inc", "initials": "FL", "color": "#6366f1"}},
    {{"quote": "20-25 word authentic testimonial quote", "name": "First Last", "role": "Job Title", "company": "Company Inc", "initials": "FL", "color": "#0369a1"}},
    {{"quote": "20-25 word authentic testimonial quote", "name": "First Last", "role": "Job Title", "company": "Company Inc", "initials": "FL", "color": "#0f766e"}}
  ],
  "faqs": [
    {{"q": "common question?", "a": "clear 15-20 word answer"}},
    {{"q": "common question?", "a": "clear 15-20 word answer"}},
    {{"q": "common question?", "a": "clear 15-20 word answer"}},
    {{"q": "common question?", "a": "clear 15-20 word answer"}}
  ],
  "stats": [
    {{"number": "10K+", "label": "stat label"}},
    {{"number": "95%", "label": "stat label"}},
    {{"number": "4.9★", "label": "stat label"}}
  ],
  "email_subject": "compelling email subject line under 50 chars",
  "email_preheader": "email preheader text under 90 chars",
  "email_body_intro": "2-3 sentence email opening paragraph",
  "footer_tagline": "5-7 word brand tagline"
}}"""

    response = await llm.ainvoke([HumanMessage(content=prompt)])
    try:
        content = _extract_json(response.content.strip())
    except Exception:
        content = {}

    # Merge colors into content
    content["colors"] = colors
    content["campaign_name"] = strategy.get("campaign_name", "Campaign")
    content["campaign_type"] = campaign_type

    # Defaults for missing fields
    content.setdefault("hero_eyebrow", "Introducing")
    content.setdefault("hero_headline", strategy.get("unique_value_proposition", "Built for your success"))
    content.setdefault("hero_subheadline", "Join thousands of teams who transformed their workflow.")
    content.setdefault("cta_primary", "Get Started Free")
    content.setdefault("cta_secondary", "Learn More")
    content.setdefault("email_subject", f"Introducing {content['campaign_name']}")
    content.setdefault("email_preheader", strategy.get("unique_value_proposition", "")[:90])
    content.setdefault("footer_tagline", "Built for modern teams")
    content.setdefault("stats", [
        {"number": "10K+", "label": "Happy customers"},
        {"number": "98%", "label": "Satisfaction rate"},
        {"number": "4.9★", "label": "Average rating"},
    ])
    if not content.get("benefits"):
        msgs = strategy.get("key_messages", ["Great quality", "Fast delivery", "Best price"])
        content["benefits"] = [
            {"icon": "✨", "title": m[:30], "desc": f"{m}. Experience the difference today."}
            for m in msgs[:3]
        ]
    if not content.get("testimonials"):
        content["testimonials"] = [
            {"quote": "This completely transformed how our team works. Absolutely recommend it.", "name": "Sarah Johnson", "role": "Product Manager", "company": "TechCorp", "initials": "SJ", "color": "#6366f1"},
            {"quote": "Incredible results from day one. Our productivity doubled within a week.", "name": "Michael Chen", "role": "CEO", "company": "StartupXYZ", "initials": "MC", "color": "#0369a1"},
            {"quote": "The best investment we made this year. Worth every penny and more.", "name": "Emily Davis", "role": "Operations Lead", "company": "ScaleUp", "initials": "ED", "color": "#0f766e"},
        ]
    if not content.get("faqs"):
        content["faqs"] = [
            {"q": "How do I get started?", "a": "Sign up in minutes — no credit card required. Our onboarding takes under 10 minutes."},
            {"q": "Is there a free trial?", "a": "Yes! Enjoy a full-featured 14-day free trial with no commitment required."},
            {"q": "Can I cancel anytime?", "a": "Absolutely. Cancel with one click, no questions asked, no cancellation fees."},
            {"q": "Do you offer customer support?", "a": "24/7 live chat and email support. Average response time under 2 minutes."},
        ]

    return content


# ─── Website HTML Template ─────────────────────────────────────────────────────

def _render_website(c: dict, strategy: dict, audience: dict) -> str:
    col = c["colors"]
    primary = col["primary"]
    dark = col["dark"]
    accent = col["accent"]
    name = c["campaign_name"]

    # loremflickr keywords from campaign type
    kw_map = {
        "product_launch": "technology,startup,innovation",
        "brand_awareness": "lifestyle,brand,people",
        "lead_gen": "business,office,professional",
        "retention": "community,happy,team",
        "seasonal": "fashion,celebration,style",
    }
    img_kw = kw_map.get(c.get("campaign_type", ""), "business,professional,marketing")

    benefits_html = ""
    for i, b in enumerate(c.get("benefits", [])[:3]):
        if not isinstance(b, dict):
            continue
        benefits_html += f"""
        <div class="card benefit-card">
          <div class="benefit-icon">{b.get('icon','✨')}</div>
          <h3>{b.get('title','')}</h3>
          <p>{b.get('desc','')}</p>
        </div>"""

    features_html = ""
    for i, f in enumerate(c.get("features", [])[:2]):
        reverse = "reverse" if i % 2 == 1 else ""
        bullets = "".join(f"<li>{bl}</li>" for bl in f.get("bullets", [])[:3])
        feat_img_url = _picsum(f"{name}_feature_{i}", 600, 480)
        features_html += f"""
      <div class="feature-row {reverse}">
        <div class="feature-text">
          <span class="feature-icon">{f.get('icon','⚡')}</span>
          <p class="feature-label">{f.get('title','Feature')}</p>
          <h3>{f.get('headline','Powerful and simple')}</h3>
          <p class="feature-desc">{f.get('desc','')}</p>
          <ul class="feature-bullets">{bullets}</ul>
        </div>
        <div class="feature-visual">
          <img src="{feat_img_url}" alt="{f.get('title','Feature visual')}" loading="lazy" />
        </div>
      </div>"""

    testimonials_html = ""
    for t in c.get("testimonials", [])[:3]:
        if not isinstance(t, dict):
            continue
        testimonials_html += f"""
        <div class="card testimonial-card">
          <div class="stars">★★★★★</div>
          <p class="quote">"{t.get('quote','Great product, highly recommended!')}"</p>
          <div class="testimonial-author">
            <div class="avatar" style="background:{t.get('color', primary)}">{t.get('initials','AB')}</div>
            <div>
              <strong>{t.get('name','Happy Customer')}</strong>
              <span>{t.get('role','')}, {t.get('company','')}</span>
            </div>
          </div>
        </div>"""

    stats_html = ""
    for s in c.get("stats", [])[:3]:
        if not isinstance(s, dict):
            continue
        stats_html += f"""
        <div class="stat-item">
          <div class="stat-number">{s.get('number','—')}</div>
          <div class="stat-label">{s.get('label','')}</div>
        </div>"""

    faqs_html = ""
    for faq in c.get("faqs", [])[:4]:
        if not isinstance(faq, dict):
            continue
        q = faq.get("q") or faq.get("question") or faq.get("Q") or "Common question"
        a = faq.get("a") or faq.get("answer") or faq.get("A") or "Please contact us for more information."
        faqs_html += f"""
        <details class="faq-item">
          <summary>{q}</summary>
          <p>{a}</p>
        </details>"""

    hero_img  = _picsum(f"{name}_hero",  680, 560)
    hero_img2 = _picsum(f"{name}_hero2", 340, 240)
    hero_img3 = _picsum(f"{name}_hero3", 340, 240)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{name}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap" rel="stylesheet">
<style>
  *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
  :root {{
    --primary: {primary};
    --dark: {dark};
    --accent: {accent};
    --text: #0f172a;
    --text-muted: #64748b;
    --bg: #ffffff;
    --bg-subtle: #f8fafc;
    --border: #e2e8f0;
    --radius: 16px;
    --radius-sm: 8px;
    --shadow: 0 4px 24px rgba(0,0,0,0.08);
    --shadow-lg: 0 20px 60px rgba(0,0,0,0.12);
    --transition: all 0.25s ease;
  }}
  html {{ scroll-behavior: smooth; font-size: 16px; }}
  body {{ font-family: 'Inter', system-ui, sans-serif; color: var(--text); background: var(--bg); overflow-x: hidden; }}

  /* ── NAV ── */
  nav {{
    position: fixed; top: 0; left: 0; right: 0; z-index: 100;
    background: rgba(255,255,255,0.92); backdrop-filter: blur(12px);
    border-bottom: 1px solid var(--border);
    padding: 0 5%;
    display: flex; align-items: center; justify-content: space-between;
    height: 68px;
  }}
  .nav-logo {{ font-weight: 800; font-size: 1.25rem; color: var(--primary); letter-spacing: -0.02em; }}
  .nav-links {{ display: flex; align-items: center; gap: 2rem; list-style: none; }}
  .nav-links a {{ text-decoration: none; color: var(--text-muted); font-size: 0.9rem; font-weight: 500; transition: var(--transition); }}
  .nav-links a:hover {{ color: var(--text); }}
  .btn-nav {{ background: var(--primary); color: #fff !important; padding: 0.55rem 1.4rem; border-radius: 50px; font-size: 0.875rem !important; font-weight: 600 !important; }}
  .btn-nav:hover {{ background: var(--dark) !important; transform: translateY(-1px); box-shadow: 0 4px 12px rgba(0,0,0,0.15); }}

  /* ── HERO ── */
  .hero {{
    min-height: 100vh; padding: 68px 5% 0;
    background: linear-gradient(135deg, var(--dark) 0%, var(--primary) 60%, {accent}88 100%);
    display: grid; grid-template-columns: 1fr 1fr; gap: 4rem;
    align-items: center;
    position: relative; overflow: hidden;
  }}
  .hero::before {{
    content: ''; position: absolute; top: -30%; right: -10%;
    width: 600px; height: 600px; border-radius: 50%;
    background: rgba(255,255,255,0.04); pointer-events: none;
  }}
  .hero-left {{ color: #fff; padding: 4rem 0; z-index: 1; }}
  .hero-eyebrow {{
    display: inline-flex; align-items: center; gap: 0.5rem;
    background: rgba(255,255,255,0.15); border: 1px solid rgba(255,255,255,0.25);
    color: #fff; padding: 0.4rem 1rem; border-radius: 50px;
    font-size: 0.8rem; font-weight: 600; letter-spacing: 0.05em; text-transform: uppercase;
    margin-bottom: 1.5rem;
  }}
  .hero-headline {{
    font-size: clamp(2.2rem, 4.5vw, 3.8rem); font-weight: 900;
    line-height: 1.1; letter-spacing: -0.03em; margin-bottom: 1.25rem;
  }}
  .hero-headline span {{ color: {accent}; }}
  .hero-sub {{
    font-size: clamp(1rem, 1.5vw, 1.2rem); font-weight: 400;
    color: rgba(255,255,255,0.82); line-height: 1.6; margin-bottom: 2.5rem; max-width: 480px;
  }}
  .hero-ctas {{ display: flex; gap: 1rem; flex-wrap: wrap; margin-bottom: 3rem; }}
  .btn-primary {{
    background: #fff; color: var(--primary); padding: 0.9rem 2rem;
    border-radius: 50px; font-weight: 700; font-size: 1rem;
    text-decoration: none; display: inline-flex; align-items: center; gap: 0.5rem;
    transition: var(--transition); box-shadow: 0 8px 24px rgba(0,0,0,0.15);
  }}
  .btn-primary:hover {{ transform: translateY(-2px); box-shadow: 0 12px 32px rgba(0,0,0,0.2); }}
  .btn-secondary {{
    background: transparent; color: #fff; padding: 0.9rem 2rem;
    border-radius: 50px; font-weight: 600; font-size: 1rem;
    text-decoration: none; border: 2px solid rgba(255,255,255,0.4);
    transition: var(--transition); display: inline-flex; align-items: center;
  }}
  .btn-secondary:hover {{ background: rgba(255,255,255,0.1); border-color: rgba(255,255,255,0.7); }}
  .hero-stats {{ display: flex; gap: 2.5rem; }}
  .hero-stat {{ }}
  .hero-stat-num {{ font-size: 1.6rem; font-weight: 800; color: #fff; }}
  .hero-stat-label {{ font-size: 0.8rem; color: rgba(255,255,255,0.65); font-weight: 500; }}
  .hero-right {{ position: relative; padding: 4rem 0; z-index: 1; }}
  .hero-img-main {{
    width: 100%; border-radius: var(--radius); overflow: hidden;
    box-shadow: var(--shadow-lg); aspect-ratio: 4/3;
  }}
  .hero-img-main img {{ width: 100%; height: 100%; object-fit: cover; }}
  .hero-img-row {{ display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-top: 1rem; }}
  .hero-img-sm {{ border-radius: var(--radius-sm); overflow: hidden; aspect-ratio: 4/3; }}
  .hero-img-sm img {{ width: 100%; height: 100%; object-fit: cover; }}
  .floating-badge {{
    position: absolute; top: 10%; right: -5%;
    background: #fff; border-radius: var(--radius-sm); padding: 0.75rem 1rem;
    box-shadow: var(--shadow-lg); font-size: 0.8rem; font-weight: 600;
    display: flex; align-items: center; gap: 0.5rem; z-index: 2;
  }}
  .floating-badge .dot {{ width: 8px; height: 8px; border-radius: 50%; background: #10b981; }}

  /* ── STATS BAR ── */
  .stats-bar {{
    background: var(--text); color: #fff;
    padding: 2.5rem 5%; display: flex; justify-content: center; gap: 6rem;
    flex-wrap: wrap;
  }}
  .stat-item {{ text-align: center; }}
  .stat-number {{ font-size: 2.2rem; font-weight: 800; color: {accent}; }}
  .stat-label {{ font-size: 0.85rem; color: rgba(255,255,255,0.65); margin-top: 0.2rem; font-weight: 500; }}

  /* ── TRUST BAR ── */
  .trust-bar {{
    background: var(--bg-subtle); border-bottom: 1px solid var(--border);
    padding: 2rem 5%; text-align: center;
  }}
  .trust-bar p {{ font-size: 0.85rem; color: var(--text-muted); font-weight: 500; margin-bottom: 1.25rem; letter-spacing: 0.05em; text-transform: uppercase; }}
  .trust-logos {{ display: flex; align-items: center; justify-content: center; gap: 2rem; flex-wrap: wrap; }}
  .trust-logo {{
    padding: 0.5rem 1.25rem; border: 1.5px solid var(--border);
    border-radius: var(--radius-sm); font-weight: 700; color: var(--text-muted);
    font-size: 0.9rem; letter-spacing: -0.01em;
  }}

  /* ── SECTION COMMONS ── */
  section {{ padding: 6rem 5%; }}
  .section-label {{ text-transform: uppercase; letter-spacing: 0.1em; font-size: 0.78rem; font-weight: 700; color: var(--primary); margin-bottom: 0.75rem; }}
  .section-title {{ font-size: clamp(1.8rem, 3vw, 2.8rem); font-weight: 800; line-height: 1.2; letter-spacing: -0.02em; margin-bottom: 1rem; }}
  .section-sub {{ font-size: 1.05rem; color: var(--text-muted); line-height: 1.7; max-width: 560px; }}
  .section-header {{ text-align: center; margin-bottom: 4rem; }}
  .section-header .section-sub {{ margin: 0 auto; }}

  /* ── CARDS ── */
  .card {{ background: #fff; border-radius: var(--radius); border: 1px solid var(--border); padding: 2rem; transition: var(--transition); }}
  .card:hover {{ box-shadow: var(--shadow-lg); transform: translateY(-4px); border-color: var(--primary)22; }}

  /* ── BENEFITS ── */
  .benefits-grid {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 1.5rem; }}
  .benefit-card {{ display: flex; flex-direction: column; gap: 1rem; }}
  .benefit-icon {{ font-size: 2.2rem; width: 56px; height: 56px; background: var(--primary)14; border-radius: var(--radius-sm); display: flex; align-items: center; justify-content: center; }}
  .benefit-card h3 {{ font-size: 1.1rem; font-weight: 700; }}
  .benefit-card p {{ color: var(--text-muted); line-height: 1.6; font-size: 0.95rem; }}

  /* ── FEATURES ── */
  .features-section {{ background: var(--bg-subtle); }}
  .feature-row {{ display: grid; grid-template-columns: 1fr 1fr; gap: 5rem; align-items: center; margin-bottom: 6rem; }}
  .feature-row:last-child {{ margin-bottom: 0; }}
  .feature-row.reverse {{ direction: rtl; }}
  .feature-row.reverse > * {{ direction: ltr; }}
  .feature-icon {{ font-size: 1.5rem; }}
  .feature-label {{ font-size: 0.8rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.08em; color: var(--primary); margin: 0.5rem 0 0.75rem; }}
  .feature-text h3 {{ font-size: 1.8rem; font-weight: 800; line-height: 1.2; letter-spacing: -0.02em; margin-bottom: 1rem; }}
  .feature-desc {{ color: var(--text-muted); line-height: 1.7; margin-bottom: 1.25rem; }}
  .feature-bullets {{ list-style: none; display: flex; flex-direction: column; gap: 0.5rem; }}
  .feature-bullets li {{ display: flex; align-items: center; gap: 0.6rem; color: var(--text-muted); font-size: 0.95rem; }}
  .feature-bullets li::before {{ content: '✓'; color: var(--primary); font-weight: 700; flex-shrink: 0; }}
  .feature-visual {{ border-radius: var(--radius); overflow: hidden; box-shadow: var(--shadow-lg); aspect-ratio: 5/4; }}
  .feature-visual img {{ width: 100%; height: 100%; object-fit: cover; display: block; }}

  /* ── TESTIMONIALS ── */
  .testimonials-section {{ background: var(--bg); }}
  .testimonials-grid {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 1.5rem; }}
  .testimonial-card {{ display: flex; flex-direction: column; gap: 1rem; }}
  .stars {{ color: #f59e0b; font-size: 1rem; letter-spacing: 2px; }}
  .quote {{ color: var(--text); font-size: 0.95rem; line-height: 1.7; font-style: italic; flex: 1; }}
  .testimonial-author {{ display: flex; align-items: center; gap: 0.75rem; padding-top: 1rem; border-top: 1px solid var(--border); }}
  .avatar {{ width: 44px; height: 44px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 0.85rem; color: #fff; flex-shrink: 0; }}
  .testimonial-author strong {{ display: block; font-size: 0.9rem; font-weight: 700; }}
  .testimonial-author span {{ color: var(--text-muted); font-size: 0.8rem; }}

  /* ── FAQ ── */
  .faq-section {{ background: var(--bg-subtle); }}
  .faq-list {{ max-width: 720px; margin: 0 auto; display: flex; flex-direction: column; gap: 1rem; }}
  .faq-item {{ background: #fff; border: 1px solid var(--border); border-radius: var(--radius-sm); overflow: hidden; }}
  .faq-item summary {{ padding: 1.25rem 1.5rem; font-weight: 600; font-size: 0.95rem; cursor: pointer; display: flex; justify-content: space-between; align-items: center; list-style: none; }}
  .faq-item summary::-webkit-details-marker {{ display: none; }}
  .faq-item summary::after {{ content: '+'; font-size: 1.25rem; color: var(--primary); transition: var(--transition); }}
  .faq-item[open] summary::after {{ content: '−'; }}
  .faq-item[open] summary {{ color: var(--primary); }}
  .faq-item p {{ padding: 0 1.5rem 1.25rem; color: var(--text-muted); font-size: 0.9rem; line-height: 1.6; }}

  /* ── FINAL CTA ── */
  .cta-section {{
    background: linear-gradient(135deg, var(--dark), var(--primary));
    text-align: center; color: #fff;
  }}
  .cta-section h2 {{ font-size: clamp(2rem, 3.5vw, 3rem); font-weight: 800; letter-spacing: -0.02em; margin-bottom: 1rem; }}
  .cta-section p {{ font-size: 1.1rem; color: rgba(255,255,255,0.75); margin-bottom: 2.5rem; }}
  .cta-buttons {{ display: flex; gap: 1rem; justify-content: center; flex-wrap: wrap; }}
  .btn-white {{ background: #fff; color: var(--primary); padding: 1rem 2.5rem; border-radius: 50px; font-weight: 700; font-size: 1.05rem; text-decoration: none; transition: var(--transition); box-shadow: 0 8px 24px rgba(0,0,0,0.2); }}
  .btn-white:hover {{ transform: translateY(-2px); box-shadow: 0 12px 32px rgba(0,0,0,0.25); }}
  .btn-outline-white {{ background: transparent; color: #fff; padding: 1rem 2.5rem; border-radius: 50px; font-weight: 600; font-size: 1.05rem; text-decoration: none; border: 2px solid rgba(255,255,255,0.4); transition: var(--transition); }}
  .btn-outline-white:hover {{ background: rgba(255,255,255,0.1); }}

  /* ── FOOTER ── */
  footer {{ background: #0f172a; color: rgba(255,255,255,0.75); padding: 4rem 5% 2rem; }}
  .footer-top {{ display: grid; grid-template-columns: 2fr 1fr 1fr 1fr; gap: 3rem; margin-bottom: 3rem; }}
  .footer-brand-name {{ font-weight: 800; font-size: 1.2rem; color: #fff; margin-bottom: 0.75rem; }}
  .footer-tagline {{ font-size: 0.9rem; line-height: 1.6; margin-bottom: 1.25rem; }}
  .footer-col h4 {{ color: #fff; font-weight: 700; font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 1rem; }}
  .footer-col ul {{ list-style: none; display: flex; flex-direction: column; gap: 0.6rem; }}
  .footer-col a {{ text-decoration: none; color: rgba(255,255,255,0.6); font-size: 0.88rem; transition: var(--transition); }}
  .footer-col a:hover {{ color: #fff; }}
  .footer-bottom {{ border-top: 1px solid rgba(255,255,255,0.1); padding-top: 2rem; display: flex; justify-content: space-between; align-items: center; flex-wrap: gap; }}
  .footer-bottom p {{ font-size: 0.82rem; }}

  /* ── RESPONSIVE ── */
  @media (max-width: 1024px) {{
    .hero {{ grid-template-columns: 1fr; min-height: auto; padding: 100px 5% 4rem; }}
    .hero-right {{ display: none; }}
    .benefits-grid, .testimonials-grid {{ grid-template-columns: repeat(2, 1fr); }}
    .feature-row {{ grid-template-columns: 1fr; gap: 2rem; }}
    .feature-row.reverse {{ direction: ltr; }}
    .footer-top {{ grid-template-columns: 1fr 1fr; }}
  }}
  @media (max-width: 768px) {{
    section {{ padding: 4rem 5%; }}
    .benefits-grid, .testimonials-grid {{ grid-template-columns: 1fr; }}
    .stats-bar {{ gap: 3rem; }}
    .trust-logos {{ gap: 1rem; }}
    .footer-top {{ grid-template-columns: 1fr; }}
    .nav-links {{ display: none; }}
    .hero-stats {{ gap: 1.5rem; flex-wrap: wrap; }}
  }}
</style>
</head>
<body>

<!-- NAV -->
<nav>
  <div class="nav-logo">{name}</div>
  <ul class="nav-links">
    <li><a href="#benefits">Features</a></li>
    <li><a href="#testimonials">Reviews</a></li>
    <li><a href="#faq">FAQ</a></li>
    <li><a href="#cta" class="btn-nav">{c.get('cta_primary', 'Get Started')}</a></li>
  </ul>
</nav>

<!-- HERO -->
<section class="hero">
  <div class="hero-left">
    <div class="hero-eyebrow">✦ {c.get('hero_eyebrow', 'Introducing')}</div>
    <h1 class="hero-headline">{c.get('hero_headline', name)}</h1>
    <p class="hero-sub">{c.get('hero_subheadline', '')}</p>
    <div class="hero-ctas">
      <a href="#cta" class="btn-primary">{c.get('cta_primary', 'Get Started')} →</a>
      <a href="#benefits" class="btn-secondary">{c.get('cta_secondary', 'Learn More')}</a>
    </div>
    <div class="hero-stats">
      {"".join(f'<div class="hero-stat"><div class="hero-stat-num">{s["number"]}</div><div class="hero-stat-label">{s["label"]}</div></div>' for s in c.get("stats", [])[:3])}
    </div>
  </div>
  <div class="hero-right">
    <div class="floating-badge"><div class="dot"></div> Live now</div>
    <div class="hero-img-main">
      <img src="{hero_img}" alt="{name} hero visual" loading="lazy" />
    </div>
    <div class="hero-img-row">
      <div class="hero-img-sm"><img src="{hero_img2}" alt="Feature preview" loading="lazy" /></div>
      <div class="hero-img-sm"><img src="{hero_img3}" alt="Team preview" loading="lazy" /></div>
    </div>
  </div>
</section>

<!-- STATS BAR -->
<div class="stats-bar">
  {stats_html}
</div>

<!-- TRUST BAR -->
<div class="trust-bar">
  <p>Trusted by fast-growing teams worldwide</p>
  <div class="trust-logos">
    <span class="trust-logo">Acme Co</span>
    <span class="trust-logo">Veritas</span>
    <span class="trust-logo">Quantum</span>
    <span class="trust-logo">Nexora</span>
    <span class="trust-logo">Stratify</span>
  </div>
</div>

<!-- BENEFITS -->
<section id="benefits">
  <div class="section-header">
    <p class="section-label">Why choose us</p>
    <h2 class="section-title">Everything you need to succeed</h2>
    <p class="section-sub">Designed for teams who demand the best — powerful, intuitive, and built to scale with you.</p>
  </div>
  <div class="benefits-grid">
    {benefits_html}
  </div>
</section>

<!-- FEATURES -->
<section class="features-section">
  <div class="section-header">
    <p class="section-label">How it works</p>
    <h2 class="section-title">Powerful features, simple experience</h2>
  </div>
  {features_html}
</section>

<!-- TESTIMONIALS -->
<section id="testimonials" class="testimonials-section">
  <div class="section-header">
    <p class="section-label">Customer stories</p>
    <h2 class="section-title">Loved by thousands of teams</h2>
    <p class="section-sub">Don't just take our word for it — hear from the people who use it every day.</p>
  </div>
  <div class="testimonials-grid">
    {testimonials_html}
  </div>
</section>

<!-- FAQ -->
<section id="faq" class="faq-section">
  <div class="section-header">
    <p class="section-label">Questions</p>
    <h2 class="section-title">Frequently asked questions</h2>
  </div>
  <div class="faq-list">
    {faqs_html}
  </div>
</section>

<!-- FINAL CTA -->
<section id="cta" class="cta-section">
  <p class="section-label" style="color:{accent}">Get started today</p>
  <h2>Ready to transform your {c.get('campaign_type','business').replace('_',' ')}?</h2>
  <p>{c.get('hero_subheadline', 'Join thousands of teams already seeing results.')}</p>
  <div class="cta-buttons">
    <a href="#" class="btn-white">{c.get('cta_primary', 'Start Free Trial')} →</a>
    <a href="#" class="btn-outline-white">{c.get('cta_secondary', 'Learn More')}</a>
  </div>
</section>

<!-- FOOTER -->
<footer>
  <div class="footer-top">
    <div>
      <div class="footer-brand-name">{name}</div>
      <p class="footer-tagline">{c.get('footer_tagline', 'Built for modern teams')}</p>
    </div>
    <div class="footer-col">
      <h4>Product</h4>
      <ul>
        <li><a href="#">Features</a></li>
        <li><a href="#">Pricing</a></li>
        <li><a href="#">Changelog</a></li>
        <li><a href="#">Roadmap</a></li>
      </ul>
    </div>
    <div class="footer-col">
      <h4>Company</h4>
      <ul>
        <li><a href="#">About</a></li>
        <li><a href="#">Blog</a></li>
        <li><a href="#">Careers</a></li>
        <li><a href="#">Press</a></li>
      </ul>
    </div>
    <div class="footer-col">
      <h4>Legal</h4>
      <ul>
        <li><a href="#">Privacy</a></li>
        <li><a href="#">Terms</a></li>
        <li><a href="#">Cookies</a></li>
        <li><a href="#">Security</a></li>
      </ul>
    </div>
  </div>
  <div class="footer-bottom">
    <p>© 2025 {name}. All rights reserved.</p>
    <p style="color:rgba(255,255,255,0.4);font-size:0.8rem">Generated by CampaignAI</p>
  </div>
</footer>

</body>
</html>"""


# ─── Email HTML Template ────────────────────────────────────────────────────────

def _render_email(c: dict, strategy: dict, audience: dict) -> str:
    col = c["colors"]
    primary = col["primary"]
    dark = col["dark"]
    name = c["campaign_name"]

    kw_map = {
        "product_launch": "technology,startup,innovation",
        "brand_awareness": "lifestyle,brand,people",
        "lead_gen": "business,office,professional",
        "retention": "community,happy,team",
        "seasonal": "fashion,celebration,style",
    }
    img_kw = kw_map.get(c.get("campaign_type", ""), "business,professional,marketing")
    hero_img = _picsum(f"{name}_email_hero", 600, 280)

    benefits = c.get("benefits", [])[:3]
    benefit_tds = ""
    for b in benefits:
        benefit_tds += f"""
          <td width="33%" style="padding:0 8px;vertical-align:top;text-align:center;">
            <div style="background:{primary}14;border-radius:12px;width:48px;height:48px;margin:0 auto 12px;display:table;line-height:48px;text-align:center;font-size:22px;">{b['icon']}</div>
            <p style="margin:0 0 6px;font-size:14px;font-weight:700;color:#0f172a;">{b['title']}</p>
            <p style="margin:0;font-size:13px;color:#64748b;line-height:1.5;">{b['desc']}</p>
          </td>"""

    testimonial = c.get("testimonials", [{}])[0]

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <meta http-equiv="X-UA-Compatible" content="IE=edge">
  <title>{name}</title>
  <!-- Subject: {c.get('email_subject', name)} -->
  <style>
    @media screen and (max-width:600px) {{
      .email-body {{ padding: 0 !important; }}
      .main-table {{ width: 100% !important; }}
      .hero-title {{ font-size: 26px !important; }}
      .benefit-td {{ display: block !important; width: 100% !important; padding: 0 0 20px !important; }}
    }}
  </style>
</head>
<body style="margin:0;padding:0;background:#f1f5f9;font-family:Inter,-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;-webkit-font-smoothing:antialiased;">

<!-- Preheader -->
<div style="display:none;max-height:0;overflow:hidden;color:#f1f5f9;">{c.get('email_preheader', '')}&nbsp;‌&nbsp;‌&nbsp;‌</div>

<table width="100%" cellpadding="0" cellspacing="0" border="0" style="background:#f1f5f9;" class="email-body">
  <tr><td align="center" style="padding:32px 16px;">

    <table width="600" cellpadding="0" cellspacing="0" border="0" class="main-table" style="width:600px;max-width:100%;">

      <!-- HEADER -->
      <tr>
        <td style="background:{primary};border-radius:16px 16px 0 0;padding:20px 32px;text-align:center;">
          <span style="font-size:22px;font-weight:900;color:#ffffff;letter-spacing:-0.03em;">{name}</span>
        </td>
      </tr>

      <!-- HERO IMAGE -->
      <tr>
        <td style="background:{dark};padding:0;overflow:hidden;">
          <img src="{hero_img}" width="600" alt="{name} campaign visual"
               style="width:100%;max-width:600px;height:auto;display:block;border:0;" />
        </td>
      </tr>

      <!-- HERO COPY -->
      <tr>
        <td style="background:linear-gradient(135deg,{dark},{primary});padding:40px 40px 48px;text-align:center;">
          <p style="margin:0 0 12px;display:inline-block;background:rgba(255,255,255,0.18);border:1px solid rgba(255,255,255,0.3);color:#fff;padding:5px 16px;border-radius:50px;font-size:11px;font-weight:700;letter-spacing:0.08em;text-transform:uppercase;">✦ {c.get('hero_eyebrow','New')}</p>
          <h1 class="hero-title" style="margin:16px 0;font-size:32px;font-weight:900;color:#ffffff;line-height:1.15;letter-spacing:-0.03em;">{c.get('hero_headline', name)}</h1>
          <p style="margin:0 auto 28px;font-size:16px;color:rgba(255,255,255,0.82);line-height:1.6;max-width:440px;">{c.get('hero_subheadline', '')}</p>
          <a href="#" style="display:inline-block;background:#ffffff;color:{primary};padding:14px 36px;border-radius:50px;font-size:15px;font-weight:700;text-decoration:none;letter-spacing:-0.01em;box-shadow:0 8px 24px rgba(0,0,0,0.2);">{c.get('cta_primary','Get Started')} &rarr;</a>
        </td>
      </tr>

      <!-- BENEFITS -->
      <tr>
        <td style="background:#ffffff;padding:40px 32px;">
          <p style="margin:0 0 8px;text-align:center;font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:0.1em;color:{primary};">Why it matters</p>
          <h2 style="margin:0 0 32px;text-align:center;font-size:22px;font-weight:800;color:#0f172a;letter-spacing:-0.02em;">Everything you need, nothing you don't</h2>
          <table width="100%" cellpadding="0" cellspacing="0" border="0">
            <tr>{benefit_tds}</tr>
          </table>
        </td>
      </tr>

      <!-- DIVIDER -->
      <tr><td style="background:#ffffff;padding:0 32px;"><div style="height:1px;background:#e2e8f0;"></div></td></tr>

      <!-- TESTIMONIAL -->
      <tr>
        <td style="background:#f8fafc;padding:36px 40px;text-align:center;">
          <p style="margin:0 0 16px;font-size:28px;color:#f59e0b;">★★★★★</p>
          <p style="margin:0 0 20px;font-size:15px;color:#334155;line-height:1.7;font-style:italic;max-width:440px;margin-left:auto;margin-right:auto;">"{testimonial.get('quote', 'This completely changed how we work. Highly recommended!')}"</p>
          <div style="display:inline-flex;align-items:center;gap:12px;">
            <div style="width:44px;height:44px;border-radius:50%;background:{testimonial.get('color', primary)};color:#fff;font-weight:700;font-size:14px;line-height:44px;text-align:center;display:inline-block;">{testimonial.get('initials','AB')}</div>
            <div style="text-align:left;display:inline-block;">
              <strong style="display:block;font-size:14px;color:#0f172a;">{testimonial.get('name','Happy Customer')}</strong>
              <span style="font-size:12px;color:#64748b;">{testimonial.get('role','')}, {testimonial.get('company','')}</span>
            </div>
          </div>
        </td>
      </tr>

      <!-- STATS ROW -->
      <tr>
        <td style="background:{primary};padding:32px 40px;">
          <table width="100%" cellpadding="0" cellspacing="0" border="0">
            <tr>
              {"".join(f'<td width="33%" style="text-align:center;"><div style="font-size:24px;font-weight:900;color:#fff;">{s["number"]}</div><div style="font-size:11px;color:rgba(255,255,255,0.7);margin-top:4px;font-weight:500;">{s["label"]}</div></td>' for s in c.get("stats",[])[:3])}
            </tr>
          </table>
        </td>
      </tr>

      <!-- FINAL CTA -->
      <tr>
        <td style="background:#0f172a;padding:40px;text-align:center;border-radius:0 0 16px 16px;">
          <h3 style="margin:0 0 10px;font-size:20px;font-weight:800;color:#ffffff;">Ready to get started?</h3>
          <p style="margin:0 0 24px;font-size:14px;color:rgba(255,255,255,0.65);line-height:1.6;">No credit card required · Free for 14 days · Cancel anytime</p>
          <a href="#" style="display:inline-block;background:{primary};color:#ffffff;padding:14px 36px;border-radius:50px;font-size:15px;font-weight:700;text-decoration:none;margin-bottom:24px;">{c.get('cta_primary','Get Started Free')}</a>
          <p style="margin:0;font-size:12px;color:rgba(255,255,255,0.35);line-height:1.6;">
            © 2025 {name} · <a href="#" style="color:rgba(255,255,255,0.45);text-decoration:none;">Unsubscribe</a> · <a href="#" style="color:rgba(255,255,255,0.45);text-decoration:none;">Privacy Policy</a>
          </p>
        </td>
      </tr>

    </table>
  </td></tr>
</table>
</body>
</html>"""


# ─── Public API ───────────────────────────────────────────────────────────────

async def generate_email_html(strategy: dict[str, Any], audience: dict[str, Any]) -> str:
    content = await _generate_content_json(strategy, audience)
    return _render_email(content, strategy, audience)


async def generate_website_html(strategy: dict[str, Any], audience: dict[str, Any]) -> str:
    content = await _generate_content_json(strategy, audience)
    return _render_website(content, strategy, audience)


async def run_content_agent(strategy: dict[str, Any], audience: dict[str, Any]) -> dict[str, str]:
    # Generate content JSON once, render both templates
    content = await _generate_content_json(strategy, audience)
    return {
        "email_html":   _render_email(content, strategy, audience),
        "website_html": _render_website(content, strategy, audience),
    }
