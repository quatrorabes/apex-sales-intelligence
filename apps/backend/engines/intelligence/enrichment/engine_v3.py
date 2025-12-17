# apps/backend/engines/intelligence/enrichment/engine_v3.py
"""
APEX Enrichment Engine v3.0 - Main Engine
10-stage enrichment pipeline producing 10,000+ word profiles
"""

import os
import json
import requests
import openai
from typing import Dict, Any, Optional
from datetime import datetime
import logging
from .research import PerplexityResearch
from .prompts import get_10k_synthesis_prompt
from .parser import parse_enrichment_sections
from .models import EnrichmentResponse

logger = logging.getLogger(__name__)

class ApexEnrichmentEngineV3:
    """
    Production enrichment engine v3.0
    
    Generates 10,000+ word buyer intelligence profiles including:
    - Personality profile (MBTI-style analysis)
    - Background & career trajectory
    - Company analysis
    - Role-specific pain points
    - Buying signals & budget indicators
    - Competitive landscape
    - Engagement strategy
    - Organizational dynamics
    - 90-day engagement roadmap
    
    Uses:
    - Perplexity AI: 10 parallel research queries (online search)
    - GPT-4: Synthesis into comprehensive profile
    """
    
    def __init__(self):
        self.perplexity_key = os.getenv("PERPLEXITY_API_KEY")
        self.openai_key = os.getenv("OPENAI_API_KEY")
        self.research_service = PerplexityResearch(self.perplexity_key)
        
        if not self.perplexity_key or not self.openai_key:
            raise ValueError("Missing API keys: PERPLEXITY_API_KEY or OPENAI_API_KEY")
        
        # Configure OpenAI
        openai.api_key = self.openai_key
        
        logger.info("✅ APEX Enrichment Engine v3.0 initialized")
    
    def enrich_contact(self, contact: Dict[str, Any]) -> EnrichmentResponse:
        """
        Main enrichment pipeline: 10 stages producing 10,000+ word profile
        
        Input: Contact object with name, title, company, email, linkedin_url
        Output: EnrichmentResponse with 10 detailed sections
        
        UUID HANDLING: All contact IDs remain as UUID strings throughout
        DATABASE: All contact fields preserved, no elimination
        """
        
        try:
            # Extract and validate contact fields (UUID stays as string)
            contact_id = contact.get("id")
            name = contact.get("name", "").strip()
            title = contact.get("title", "").strip()
            company = contact.get("company", "").strip()
            email = contact.get("email", "").strip()
            linkedin_url = contact.get("linkedin_url", "").strip()
            
            # Preserve all other fields (no elimination)
            preserved_fields = {
                k: v for k, v in contact.items()
                if k not in ["id", "name", "title", "company", "email", "linkedin_url", "enrichment_data"]
            }
            
            if not all([name, title, company]):
                return EnrichmentResponse(
                    success=False,
                    error="Missing required fields: name, title, company",
                    contact_id=contact_id
                )
            
            logger.info(f"🚀 APEX v3.0: Enriching {name} ({title} @ {company})")
            start_time = datetime.utcnow()
            
            # ================================================================
            # STAGES 1-5: RESEARCH GATHERING (Perplexity - Parallel)
            # ================================================================
            logger.info("📡 Stage 1-5: Gathering research from Perplexity...")
            research = self.research_service.gather_comprehensive_research(
                name=name,
                title=title,
                company=company,
                email=email,
                linkedin_url=linkedin_url
            )
            
            research_time = (datetime.utcnow() - start_time).total_seconds()
            logger.info(f"✅ Research complete: {research_time:.1f}s")
            
            # ================================================================
            # STAGES 6-10: GPT-4 SYNTHESIS → 10,000 WORD PROFILE
            # ================================================================
            logger.info("🧠 Stage 6-10: Synthesizing profile with GPT-4...")
            profile_text = self._synthesize_10k_profile(
                name=name,
                title=title,
                company=company,
                research=research
            )
            
            synthesis_time = (datetime.utcnow() - start_time).total_seconds() - research_time
            logger.info(f"✅ Synthesis complete: {synthesis_time:.1f}s")
            
            # ================================================================
            # PARSE INTO STRUCTURED SECTIONS
            # ================================================================
            logger.info("📋 Parsing sections...")
            sections = parse_enrichment_sections(profile_text)
            
            # ================================================================
            # BUILD RESPONSE (All data preserved)
            # ================================================================
            response = EnrichmentResponse(
                success=True,
                contact_id=contact_id,  # UUID string preserved
                contact_info={
                    "id": contact_id,
                    "name": name,
                    "title": title,
                    "company": company,
                    "email": email,
                    "linkedin_url": linkedin_url
                },
                sections=sections,
                raw_profile=profile_text,
                metadata={
                    "enrichment_engine": "v3.0",
                    "total_sections": len(sections),
                    "character_count": len(profile_text),
                    "word_count": len(profile_text.split()),
                    "research_sources": list(research.keys()),
                    "generated_at": datetime.utcnow().isoformat(),
                    "processing_time_seconds": round((datetime.utcnow() - start_time).total_seconds(), 2)
                },
                preserved_fields=preserved_fields  # All extra fields preserved
            )
            
            total_time = (datetime.utcnow() - start_time).total_seconds()
            logger.info(f"✅ COMPLETE: {len(profile_text)} chars, {response.metadata['word_count']} words, {total_time:.1f}s total")
            
            return response
        
        except Exception as e:
            logger.error(f"❌ Enrichment failed: {str(e)}", exc_info=True)
            return EnrichmentResponse(
                success=False,
                error=str(e),
                contact_id=contact.get("id")
            )
    
    def _synthesize_10k_profile(
        self, name: str, title: str, company: str, research: Dict[str, str]
    ) -> str:
        """
        Use GPT-4 to synthesize research into 10,000+ word profile
        """
        
        # Build research context (each source truncated to avoid token overload)
        research_context = self._build_research_context(research)
        
        # Get comprehensive synthesis prompt
        prompt = get_10k_synthesis_prompt(
            name=name,
            title=title,
            company=company,
            research=research_context
        )
        
        # Call GPT-4 with high token limit for 10,000 word output
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are the world's best B2B sales intelligence analyst. "
                        "Create comprehensive, deeply researched buyer profiles that help sales reps close deals. "
                        "Be specific, detailed, and action-oriented. "
                        "Include personality traits, pain points, buying signals, and engagement strategies. "
                        "Write in conversational tone. Target: 10,000+ words across all sections."
                    )
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.7,
            max_tokens=8000,  # Will produce ~10,000 words
            timeout=60
        )
        
        return response.choices[0].message.content
    
    def _build_research_context(self, research: Dict[str, str]) -> str:
        """Format research data into readable context (truncated to fit tokens)"""
        sections = []
        
        for source_name, content in research.items():
            if content.strip():
                label = source_name.replace("_", " ").upper()
                # Truncate each source to ~800 chars to avoid token overload
                truncated = content[:800] + ("..." if len(content) > 800 else "")
                sections.append(f"{label}:\n{truncated}")
        
        return "\n\n".join(sections)
