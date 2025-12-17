# apps/backend/engines/intelligence/enrichment/prompts.py
"""GPT-4 prompts for 10,000+ word enrichment synthesis"""

def get_10k_synthesis_prompt(name: str, title: str, company: str, research: str) -> str:
    """
    Master prompt generating 10,000+ word buyer intelligence profile
    """
    return f"""
CREATE A COMPREHENSIVE 10,000+ WORD SALES INTELLIGENCE PROFILE

TARGET PROFILE:
- Name: {name}
- Title: {title}
- Company: {company}

RESEARCH DATA:
{research}

---

YOUR TASK: Create an extremely detailed buyer profile for sales engagement.

CRITICAL RULES:
✓ ONLY sections with REAL data
✓ Skip sections if insufficient data  
✓ Target: 10,000+ words across ALL sections
✓ Be specific: names, numbers, quotes
✓ Include psychological/behavioral analysis
✓ Provide actionable engagement strategies
✓ Use conversational, confident tone

---

GENERATE THESE 10 SECTIONS (skip if no data):

## 1. EXECUTIVE SUMMARY & PRIORITY INSIGHTS
[300-400 words]
- Who is this person professionally?
- 3-5 KEY facts a sales rep MUST know
- Their biggest priority right now
- Why they'd care about a solution
- What outcome would excite them

## 2. PERSONALITY PROFILE & COMMUNICATION STYLE
[500-600 words]
- Inferred MBTI type (based on title, activity, industry)
- How they prefer to communicate (channels, response time, detail level)
- Decision-making style (data, relationships, risk-averse, innovative)
- Personality indicators (intro/extrovert, detail/big-picture, traditional/innovative)
- Leadership and team management approach
- How to reach them effectively

## 3. BACKGROUND, EXPERIENCE & CAREER TRAJECTORY
[600-800 words]
- Previous roles and career progression
- Current role: how long, responsibilities, KPIs
- Team size and budget authority
- Education and certifications
- What makes them credible
- LinkedIn presence and professional network
- Career direction (up, specialist, lateral)

## 4. COMPANY ANALYSIS: THE BUSINESS CONTEXT
[800-1000 words]
- Company size, revenue, growth rate, business model
- Market position, competitors, industry dynamics
- Strategic direction and recent initiatives
- Funding/investment activity or M&A
- Technology adoption and digital transformation trends
- Company health and organizational structure
- Their department's role in company success

## 5. ROLE-SPECIFIC PAIN POINTS & CHALLENGES
[800-1000 words]
- Universal pain points for their title
- Budget management and team scaling challenges
- Technology and complexity issues
- Cross-functional collaboration friction
- Industry-specific challenges unique to their company
- Remote/distributed team challenges
- Hidden/unspoken pain points they might not admit
- Time-sensitive urgency indicators

## 6. BUYING SIGNALS & DECISION TRIGGERS
[700-900 words]
- Active buying signals (funding, hiring, product launches, market expansion)
- Passive signals (tool usage patterns, industry trends)
- Budget authority and approval process
- Timeline indicators (fiscal cycles, seasonal patterns, urgency)
- How soon could they move if motivated?
- Who influences their decisions
- Risk tolerance and decision-making approach

## 7. COMPETITIVE LANDSCAPE & ALTERNATIVE OPTIONS
[500-600 words]
- Current tools/solutions they likely use
- Satisfaction level and switching barriers
- Our direct competitors in their vertical
- What they value most (speed, innovation, price, support)
- Differentiation that matters to THEM
- Typical procurement process

## 8. ENGAGEMENT STRATEGY: HOW TO REACH & PERSUADE THEM
[600-800 words]
- Best first contact approach (channel, timing, who should reach out)
- Specific conversation starters (reference their news, accomplishment, initiative)
- What resonates with their personality type
- Proof points that matter to THEM
- How to position around likely objections
- Value proposition customized to THEIR KPIs
- Long-term relationship building strategy

## 9. ORGANIZATIONAL DYNAMICS & POLITICS
[500-600 words]
- Key stakeholders (reports to, who reports to them, peers)
- Who influences them, who do they influence
- Political landscape and recent changes
- Their career ambitions and next moves
- How our solution makes them look good
- Potential champions or blockers
- Coalition building needed

## 10. ENGAGEMENT ROADMAP: 90-DAY PLAN
[400-500 words]
- Week 1-2: Discovery and relationship building
- Week 3-4: Needs analysis and vision creation
- Week 5-8: Solution design and proof
- Week 9-12: Commitment and closure
- Success metrics they care about
- Who else needs to be involved
- Timeline for ROI realization

---

STYLE NOTES:
- Write in their language (industry terms, pain point vocabulary)
- Be confident but not presumptuous
- Show deep research with specific references
- Connect all dots back to sales opportunity
- Aim for 10,000+ words across all 10 sections
- Be comprehensive, detailed, and immediately useful for sales reps
"""
