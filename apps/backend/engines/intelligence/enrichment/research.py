# apps/backend/engines/intelligence/enrichment/research.py
"""Perplexity API research module - 10 parallel searches"""

import requests
import logging
from typing import Dict

logger = logging.getLogger(__name__)

class PerplexityResearch:
    """Execute parallel Perplexity searches for comprehensive research"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.perplexity.ai/chat/completions"
    
    def gather_comprehensive_research(
        self, name: str, title: str, company: str, email: str, linkedin_url: str
    ) -> Dict[str, str]:
        """Execute 10 parallel Perplexity searches"""
        
        queries = {
            "person_linkedin": (
                f"LinkedIn profile of {name} working at {company} as {title}. "
                f"Background, experience, education, skills, personality, communication style."
            ),
            "company_overview": (
                f"{company} company profile: size, revenue, industry, founded, "
                f"products, business model, market position, competitors."
            ),
            "company_growth": (
                f"{company} growth, funding rounds, acquisitions, new markets, "
                f"revenue growth, hiring, market share, competitive advantages."
            ),
            "company_news": (
                f"{company} latest news 2024 2025: product launches, partnerships, "
                f"executive changes, geographic expansion."
            ),
            "role_responsibilities": (
                f"{title} role typical responsibilities, KPIs, challenges, budget authority, "
                f"decision-making power, team size, success metrics."
            ),
            "industry_trends": (
                f"{company}'s industry trends, challenges, digital transformation, "
                f"competitive pressures, technology adoption, budget priorities."
            ),
            "buying_signals": (
                f"{company} technology stack, SaaS tools, cloud migration, CRM/ERP, "
                f"recent tech hires, AI adoption, digital initiatives."
            ),
            "person_authority": (
                f"{name} at {company} decision-making power, budget control, "
                f"vendor selection authority, team influence, cross-functional relationships."
            ),
            "competitive_landscape": (
                f"{company} competitors, market dynamics, market share, customer satisfaction, "
                f"pricing sensitivity, contract renewal timing."
            ),
            "business_challenges": (
                f"Common pain points for {title} roles at companies like {company}: "
                f"operational challenges, team management, revenue problems, technology gaps."
            )
        }
        
        research = {}
        
        # Execute all searches (could be parallelized with asyncio if needed)
        for source_name, query in queries.items():
            try:
                logger.info(f"  📡 Perplexity: {source_name}")
                research[source_name] = self._search_perplexity(query)
            except Exception as e:
                logger.warning(f"  ⚠️  {source_name} failed: {str(e)}")
                research[source_name] = ""
        
        return research
    
    def _search_perplexity(self, query: str) -> str:
        """Call Perplexity API"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "llama-3.1-sonar-large-128k-online",
            "messages": [{"role": "user", "content": query}],
            "temperature": 0.7,
            "max_tokens": 2048
        }
        
        response = requests.post(
            self.base_url,
            headers=headers,
            json=payload,
            timeout=30
        )
        
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
