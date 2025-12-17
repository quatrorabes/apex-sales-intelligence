# apps/backend/engines/intelligence/enrichment/parser.py
"""Parse enrichment markdown into structured sections"""

from typing import Dict
import logging

logger = logging.getLogger(__name__)

def parse_enrichment_sections(markdown_text: str) -> Dict[str, str]:
    """
    Parse 10,000+ word markdown into 10 sections
    
    Input: "## 1. EXECUTIVE SUMMARY\n...\n## 2. PERSONALITY PROFILE\n..."
    Output: {"executive_summary": "...", "personality_profile": "...", ...}
    """
    
    sections = {}
    current_section = None
    current_content = []
    
    lines = markdown_text.split('\n')
    
    for line in lines:
        # Match markdown h2 headings: ## Section Name
        if line.startswith('## '):
            # Save previous section
            if current_section and current_content:
                key = _normalize_section_key(current_section)
                content = '\n'.join(current_content).strip()
                if content:
                    sections[key] = content
            
            # Start new section
            current_section = line[3:].strip()  # Remove "## "
            current_content = []
        else:
            # Accumulate content
            if current_section is not None:
                current_content.append(line)
    
    # Save last section
    if current_section and current_content:
        key = _normalize_section_key(current_section)
        content = '\n'.join(current_content).strip()
        if content:
            sections[key] = content
    
    logger.info(f"✅ Parsed {len(sections)} sections")
    return sections

def _normalize_section_key(heading: str) -> str:
    """
    Convert heading to section key
    "1. EXECUTIVE SUMMARY & PRIORITY INSIGHTS" → "executive_summary_priority_insights"
    """
    return (
        heading.lower()
        .replace('&', 'and')
        .replace(':', '')
        .replace(' and ', '_')
        .replace(' - ', '_')
        .replace(' / ', '_')
        .replace('.', '')
        .replace(',', '')
        .replace('  ', ' ')
        .replace(' ', '_')
        .replace('__', '_')
        .strip('_')
    )

# Expected section keys (for validation)
EXPECTED_SECTIONS = [
    "executive_summary_priority_insights",
    "personality_profile_communication_style",
    "background_experience_career_trajectory",
    "company_analysis_business_context",
    "role_specific_pain_points_challenges",
    "buying_signals_decision_triggers",
    "competitive_landscape_alternative_options",
    "engagement_strategy_reach_persuade",
    "organizational_dynamics_politics",
    "engagement_roadmap_90_day_plan"
]
