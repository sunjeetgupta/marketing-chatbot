"""Marketing knowledge base documents for RAG seeding."""

MARKETING_DOCUMENTS = [
    # ─── Campaign Strategy Frameworks ───────────────────────────────────────
    {
        "id": "strategy_aida",
        "content": """AIDA Marketing Framework:
The AIDA model is a foundational marketing framework describing the stages a consumer goes through:
- Awareness: Make target audience aware of the product/service. Use broad-reach channels like social media ads, PR, and content marketing.
- Interest: Generate interest by highlighting key benefits and differentiators. Use engaging content, demos, and educational material.
- Desire: Convert interest into desire by addressing emotional needs and demonstrating value. Use testimonials, case studies, and comparison content.
- Action: Drive conversion with clear CTAs, limited-time offers, frictionless checkout, and retargeting.
Best for: Product launches, brand campaigns, and top-of-funnel strategies.""",
        "category": "strategy_framework",
    },
    {
        "id": "strategy_race",
        "content": """RACE Digital Marketing Framework:
RACE stands for Reach, Act, Convert, Engage — a practical digital marketing planning framework:
- Reach: Build awareness through SEO, paid search, social media, display ads, and influencer partnerships. KPIs: Impressions, reach, share of voice.
- Act: Encourage interaction with content, website visits, social engagement, and lead generation. KPIs: Page views, time on site, leads generated.
- Convert: Drive sales through email nurture, retargeting, landing page optimization, CRO. KPIs: Conversion rate, revenue, cart abandonment rate.
- Engage: Build long-term loyalty via email newsletters, loyalty programs, community building. KPIs: Repeat purchase rate, NPS, CLV.
Best for: E-commerce, SaaS, and brands with multi-channel presence.""",
        "category": "strategy_framework",
    },
    {
        "id": "strategy_smart",
        "content": """SMART Marketing Goals Framework:
Effective marketing campaigns require SMART objectives:
- Specific: Define exactly what you want to achieve (e.g., "increase email newsletter subscribers")
- Measurable: Attach numbers (e.g., "by 25%")
- Achievable: Realistic given budget and resources
- Relevant: Aligned with business objectives
- Time-bound: Set a deadline (e.g., "within Q2 2025")
Example SMART goal: "Increase qualified leads from paid search by 30% within 90 days with a CPA below $50."
Campaign budget allocation recommendation: 40% acquisition, 30% conversion, 20% retention, 10% testing.""",
        "category": "strategy_framework",
    },
    {
        "id": "strategy_funnel",
        "content": """Marketing Funnel Strategy:
Modern marketing funnels have 6 key stages requiring different tactics:
1. Awareness (TOFU): Content marketing, SEO, social media, PR, podcasts, YouTube. Budget: 25%.
2. Consideration (MOFU): Email marketing, webinars, comparison guides, case studies, retargeting. Budget: 30%.
3. Decision (BOFU): Free trials, demos, discount offers, testimonials, live chat. Budget: 25%.
4. Purchase: Smooth checkout, upsell/cross-sell, payment flexibility. Budget: 10%.
5. Retention: Onboarding sequences, customer success, loyalty programs. Budget: 7%.
6. Advocacy: Referral programs, community building, UGC campaigns. Budget: 3%.
Channel attribution model: Use multi-touch attribution to credit all touchpoints.""",
        "category": "strategy_framework",
    },
    {
        "id": "strategy_channels",
        "content": """Marketing Channel Selection Guide:
Choose channels based on audience, budget, and goals:
- Email Marketing: Highest ROI ($42 per $1 spent). Best for nurture, retention, and promotions.
- Social Media (Instagram/TikTok): Visual products, B2C, youth demographics. CPM: $5-$10.
- Social Media (LinkedIn): B2B, professional services. CPM: $30-$60 but highest-quality B2B leads.
- Google Search Ads: High-intent buyers. CPC varies $1-$50 by industry.
- Content/SEO: Long-term organic growth, 12+ month payoff, builds brand authority.
- Influencer Marketing: Authentic reach, micro-influencers (10K-100K followers) yield 60% higher engagement.
- Display/Programmatic: Brand awareness at scale. CPM: $1-$5.
- Podcast/CTV Ads: Engaged audiences, growing fast, good for brand storytelling.""",
        "category": "channel_strategy",
    },

    # ─── Audience Segmentation ───────────────────────────────────────────────
    {
        "id": "audience_segmentation",
        "content": """Audience Segmentation Strategies:
Effective campaigns require precise audience segmentation:

Demographic Segmentation:
- Age groups: Gen Z (18-27), Millennials (28-43), Gen X (44-59), Boomers (60+)
- Income levels: Budget-conscious (<$50K), Mid-market ($50K-$150K), Affluent ($150K+)
- Education, occupation, family status

Psychographic Segmentation:
- Lifestyle: Health-conscious, eco-friendly, tech-savvy, career-driven
- Values: Sustainability, innovation, community, tradition
- Personality: Early adopters vs. pragmatists vs. skeptics

Behavioral Segmentation:
- Purchase history, browsing behavior, brand loyalty
- Usage rate: Heavy, medium, light users
- Decision triggers: Price, quality, convenience, social proof

B2B Segmentation:
- Company size (SMB vs. Enterprise), industry vertical, tech stack
- Decision-maker role (C-suite, Director, Manager)
- Buying stage and intent signals""",
        "category": "audience",
    },
    {
        "id": "audience_personas",
        "content": """Customer Persona Development:
Build detailed buyer personas for campaign targeting:

Components of a strong persona:
- Name and photo (humanizes the segment)
- Demographics (age, location, income, education)
- Job title and responsibilities (for B2B)
- Goals and motivations (what drives them)
- Pain points and frustrations (what problems they face)
- Preferred content formats (video, articles, podcasts)
- Preferred channels (social platforms, email, search)
- Purchase triggers and objections
- Day-in-the-life narrative

Common persona archetypes:
- The Busy Professional: Values efficiency, researches thoroughly, ROI-focused
- The Early Adopter: Tech-curious, seeks innovation, influences peers
- The Value Seeker: Price-conscious, needs social proof, responds to deals
- The Loyal Advocate: Brand-attached, responds to exclusivity and recognition
- The Research-First Buyer: Content-driven, needs education before purchase""",
        "category": "audience",
    },
    {
        "id": "audience_b2b",
        "content": """B2B Marketing Audience Strategies:
Business-to-business campaigns require account-based thinking:

Account-Based Marketing (ABM):
- Identify target accounts (ICP: Ideal Customer Profile)
- Map stakeholders within each account (champion, economic buyer, influencer, end user)
- Personalize messaging for each role
- Coordinate across sales and marketing

B2B Buying Committee Roles:
- Economic Buyer (CFO/CEO): Cares about ROI, risk, strategic fit
- Technical Buyer (CTO/IT): Cares about integration, security, scalability
- End User (Manager/IC): Cares about usability, efficiency, workflow
- Procurement: Cares about pricing, contract terms, vendor reliability

Content by stage:
- Awareness: Industry reports, benchmarks, thought leadership
- Consideration: Case studies, ROI calculators, product comparisons
- Decision: Demos, trials, references, proposal templates

Sales cycle: Average B2B deal takes 6-12 months with 6+ stakeholders.""",
        "category": "audience",
    },

    # ─── Email Marketing ─────────────────────────────────────────────────────
    {
        "id": "email_best_practices",
        "content": """Email Marketing Best Practices:
Email remains the highest-ROI digital channel. Key best practices:

Subject Line Optimization:
- Keep under 50 characters for mobile preview
- Use personalization tokens ([First Name], [Company])
- Create urgency without being spammy
- A/B test: question vs. statement, emoji vs. no emoji
- Best performing formats: numbered lists, "how to", personalized

Email Design Principles:
- Single column layout for mobile-first rendering
- Font size: minimum 16px body, 22px+ headlines
- CTA button: minimum 44x44px tap target, high-contrast color
- Preheader text: 85-100 characters that complement subject
- Image-to-text ratio: 60% text, 40% images for deliverability
- Always include a plain-text version

Timing and Frequency:
- Best send times: Tuesday-Thursday, 9-11am and 1-3pm recipient timezone
- Welcome series: Send immediately, then +1 day, +3 days, +7 days
- Newsletter: Weekly or bi-weekly for engaged audiences
- Promotional: 2-4x per month maximum to avoid fatigue

Performance benchmarks:
- Open rate: 20-25% is average; 30%+ is excellent
- Click rate: 2.5% average; 5%+ is excellent
- Unsubscribe rate: Keep below 0.5%""",
        "category": "email_marketing",
    },
    {
        "id": "email_automation",
        "content": """Email Marketing Automation Sequences:
Automated email campaigns deliver 320% more revenue than batch-and-blast.

Key automation sequences:
1. Welcome Series (5 emails over 14 days):
   - Email 1 (Day 0): Welcome + brand story + what to expect
   - Email 2 (Day 2): Best resources / getting started guide
   - Email 3 (Day 5): Social proof + testimonials
   - Email 4 (Day 9): Feature spotlight or key benefit
   - Email 5 (Day 14): Soft promotion or next step CTA

2. Abandoned Cart (3 emails):
   - Email 1 (1 hour after): Reminder with cart contents
   - Email 2 (24 hours): Add social proof or answer objections
   - Email 3 (72 hours): Offer incentive (discount or free shipping)

3. Post-Purchase (3 emails):
   - Email 1 (Immediate): Order confirmation + next steps
   - Email 2 (Day 7): Onboarding tips or usage guide
   - Email 3 (Day 30): Upsell/cross-sell or request review

4. Re-engagement (3-email sunset campaign):
   - Email 1: "We miss you" with valuable content
   - Email 2: Special win-back offer
   - Email 3: Last chance + unsubscribe if not interested""",
        "category": "email_marketing",
    },

    # ─── Website/Landing Page ─────────────────────────────────────────────────
    {
        "id": "landing_page_design",
        "content": """Landing Page Design and CRO Best Practices:
High-converting landing pages follow proven patterns:

Above-the-Fold Elements:
- Compelling headline addressing the primary pain point or desire
- Subheadline clarifying the value proposition
- Hero image or video showing the product/outcome
- Primary CTA button (high-contrast, action-oriented text)
- Trust indicators (logos, ratings, subscriber counts)

Social Proof Sections:
- Customer testimonials with photos, names, and companies
- Case studies with specific results (numbers, percentages)
- Star ratings from review platforms
- Client logos (for B2B)
- Media mentions ("As seen in Forbes, TechCrunch")

Feature/Benefit Section:
- Lead with benefits (what they get), not features (how it works)
- Use icons for scanability
- 3-6 key points maximum

FAQ Section:
- Address top 5-8 objections
- Keep answers concise (2-3 sentences)

Page Performance:
- Load time under 3 seconds (1-2 seconds ideal)
- Mobile-first responsive design
- Minimal navigation to reduce distraction
- A/B test headlines, CTAs, and social proof""",
        "category": "website",
    },
    {
        "id": "website_content_strategy",
        "content": """Website Content Strategy for Campaigns:
Campaign landing pages vs. homepage vs. product pages:

Campaign Landing Page (highest conversion focus):
- Single objective, single CTA
- No navigation links (reduce exit points)
- Headline matches ad/email creative (message match)
- Form above the fold for lead gen campaigns
- Video increases conversions 80% on average

Homepage (brand + discovery):
- Clear hero statement: what you do + who it's for
- Multiple paths for different visitor types
- Latest content/news section
- Trust signals prominent

Product Pages (purchase intent):
- Product photography from multiple angles
- Detailed specifications table
- Review/rating display
- Related products (upsell)
- Urgency elements: stock levels, limited offers

Campaign Microsites:
- Themed around specific campaign
- Interactive elements (calculators, quizzes)
- Campaign-specific URLs for tracking
- Often used for seasonal or product launch campaigns""",
        "category": "website",
    },

    # ─── KPIs and Metrics ────────────────────────────────────────────────────
    {
        "id": "marketing_kpis",
        "content": """Marketing KPIs and Performance Metrics:
Measure campaign success with the right metrics by funnel stage:

Awareness Metrics:
- Impressions: Total times ad was shown
- Reach: Unique people who saw content
- Brand search volume: Branded keyword search trends
- Social followers growth rate
- Share of Voice (SOV): Your mentions vs. competitors

Engagement Metrics:
- CTR (Click-Through Rate): Clicks / Impressions. Benchmark: 0.5% display, 3-5% search
- Engagement Rate: Interactions / Reach. Benchmark: 1-3% organic social
- Time on Site: Longer is better for content; shorter for landing pages
- Bounce Rate: Benchmark varies; 40-60% normal for blogs

Conversion Metrics:
- Conversion Rate (CVR): Completions / Visits. Benchmark: 2-5% e-commerce, 5-15% B2B lead gen
- Cost Per Lead (CPL): Total spend / Leads generated
- Cost Per Acquisition (CPA): Total spend / Customers acquired
- ROAS: Revenue from ads / Ad spend. Target: 3-5x minimum

Retention and Revenue Metrics:
- Customer Lifetime Value (CLV): Average order × purchase frequency × customer lifespan
- Churn Rate: Customers lost / Total customers per period
- Net Promoter Score (NPS): Measure loyalty and advocacy (50+ is excellent)
- Email List Growth Rate: (New subscribers - Unsubscribes) / Total × 100""",
        "category": "metrics",
    },
    {
        "id": "campaign_budget",
        "content": """Campaign Budget Planning and Allocation:
How to allocate marketing budgets for maximum ROI:

Budget Benchmarks by Company Stage:
- Startup: 10-20% of revenue on marketing
- Growth stage: 7-12% of revenue
- Mature brand: 3-7% of revenue

Channel Budget Allocation (growth-stage e-commerce example):
- Paid search (Google/Bing): 30%
- Paid social (Meta/TikTok): 25%
- Email marketing (tools + creative): 10%
- SEO/content marketing: 15%
- Influencer/partnerships: 10%
- Creative production: 5%
- Testing/experimentation: 5%

Campaign Type Budget Splits:
- Product launch campaign: 50% paid media, 30% PR/influencer, 20% content/SEO
- Brand awareness campaign: 60% display/video, 20% social, 20% content
- Lead generation campaign: 40% paid search, 30% content/SEO, 20% email, 10% events
- Retention campaign: 60% email, 20% loyalty program, 20% social retargeting

Testing budget rule: Always reserve 10-15% for A/B testing and experimentation.""",
        "category": "budget_planning",
    },
    {
        "id": "content_marketing",
        "content": """Content Marketing Strategy:
Content marketing drives 3x more leads than outbound at 62% lower cost.

Content Pillars:
1. Educational: How-to guides, tutorials, explainer videos, FAQs
2. Inspirational: Success stories, behind-the-scenes, transformation content
3. Entertaining: Memes, challenges, interactive content, humor
4. Promotional: Product features, offers, announcements (keep under 20% of total)

Content Formats by Channel:
- Blog posts: 1500-2500 words for SEO; 800-1200 for engagement
- Video: Under 60 seconds for social; 5-10 minutes for YouTube/LinkedIn
- Infographics: Data visualization, step-by-step guides
- Podcasts: 20-45 minutes, weekly cadence
- Newsletters: Curated roundups + original insights, 300-800 words
- Social posts: Platform-native formats, vertical video priority

Content Calendar Framework:
- 70% evergreen content (always relevant)
- 20% trending/timely content
- 10% experimental/test content

SEO Content Strategy:
- Target long-tail keywords (3+ words) for easier ranking
- Create content clusters: pillar page + 8-12 cluster pages
- Update top-performing content every 6-12 months""",
        "category": "content_strategy",
    },
    {
        "id": "social_media_strategy",
        "content": """Social Media Marketing Strategy:
Platform-specific best practices for campaigns:

Instagram:
- Optimal post times: Monday-Friday 8-9am, Tuesday-Wednesday 2pm
- Stories: Use polls, questions, sliders for engagement
- Reels: 15-30 second, trending audio, first 3 seconds critical
- Hashtags: 5-10 highly relevant (not 30 generic ones)
- UGC (User Generated Content): Reposts build trust and reduce content burden

TikTok:
- Algorithm favors completion rate, not follower count
- Hook in first 1-3 seconds
- Native-feeling content outperforms polished ads
- Trending sounds boost discoverability
- Best for: Gen Z, entertainment, lifestyle, food, beauty

LinkedIn:
- Best B2B platform; 4x higher conversion than other social channels
- Document posts (carousels) get highest organic reach
- Personal brand posts outperform company page posts
- Best times: Tuesday-Thursday 8-10am
- Long-form articles establish thought leadership

Facebook/Meta:
- Best for retargeting and lookalike audiences
- Video (especially live) gets highest organic reach
- Group engagement higher than page engagement
- Best for: 35-65 age demographic

Twitter/X:
- Real-time conversation and trending topics
- Threading (tweetstorms) for long-form thoughts
- Best for: Tech, media, finance, politics audiences""",
        "category": "social_media",
    },
]

DOCUMENT_CATEGORIES = list({doc["category"] for doc in MARKETING_DOCUMENTS})
