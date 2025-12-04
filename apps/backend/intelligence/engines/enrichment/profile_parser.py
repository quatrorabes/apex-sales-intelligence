#!/usr/bin/env python3
"""
Enrichment Profile Parser
Extracts structured data from markdown enrichment profiles
"""
import re
import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)

class ProfileParser:
    """Parse enrichment markdown into structured fields"""
    
    @staticmethod
    def parse(profile_text: str) -> Dict[str, str]:
        """Extract all sections from enrichment profile"""
        if not profile_text:
            return {}
        
        parsed = {
            'executive_summary': ProfileParser._extract_section(profile_text, 'EXECUTIVE SUMMARY'),
            'professional_overview': ProfileParser._extract_section(profile_text, 'Professional Profile', 'Overview'),
            'background_experience': ProfileParser._extract_section(profile_text, 'Background & Experience'),
            'education': ProfileParser._extract_section(profile_text, 'Education & Credentials'),
            'personality_style': ProfileParser._extract_section(profile_text, 'Professional Strengths & Working Style'),
            'social_presence': ProfileParser._extract_section(profile_text, 'Social Presence'),
            'company_overview': ProfileParser._extract_section(profile_text, 'Company Intelligence', 'Business Model'),
            'products_services': ProfileParser._extract_section(profile_text, 'Products & Services'),
            'market_position': ProfileParser._extract_section(profile_text, 'Market Position'),
            'leadership': ProfileParser._extract_section(profile_text, 'Leadership'),
            'recent_activity': ProfileParser._extract_section(profile_text, 'Recent Activity'),
            'trigger_events': ProfileParser._extract_section(profile_text, 'Trigger Events'),
            'pain_points': ProfileParser._extract_section(profile_text, 'Pain Points'),
            'engagement_strategy': ProfileParser._extract_section(profile_text, 'Engagement Strategy'),
            'recommended_opening': ProfileParser._extract_opening_line(profile_text),
            'opportunity_level': ProfileParser._extract_opportunity_level(profile_text),
            'top_reasons': ProfileParser._extract_top_reasons(profile_text),
            'strategic_summary': ProfileParser._extract_section(profile_text, 'Strategic Summary'),
            'competitive_intelligence': ProfileParser._extract_section(profile_text, 'Competitive Intelligence'),
        }
        
        # Remove None values
        parsed = {k: v for k, v in parsed.items() if v}
        
        logger.info(f"✅ Parsed {len(parsed)} sections from enrichment profile")
        
        return parsed
    
    @staticmethod
    def _extract_section(text: str, *section_names) -> Optional[str]:
        """Extract content under a section heading"""
        for section_name in section_names:
            # Try different heading formats
            patterns = [
                rf'##\s+{re.escape(section_name)}[^\n]*\n(.+?)(?=\n##|\n---|
\n# |$)',
                rf'###\s+{re.escape(section_name)}[^\n]*\n(.+?)(?=\n###|\n##|\n---|
\n# |$)',
                rf'\*\*{re.escape(section_name)}\*\*[^\n]*\n(.+?)(?=\n\*\*|\n##|\n---|
\n# |$)',
            ]
            
            for pattern in patterns:
                match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
                if match:
                    content = match.group(1).strip()
                    # Clean up
                    content = re.sub(r'\n{3,}', '\n\n', content)  # Max 2 newlines
                    content = re.sub(r'^[-•*]\s+', '', content, flags=re.MULTILINE)  # Remove bullets
                    return content if len(content) > 50 else None
        
        return None
    
    @staticmethod
    def _extract_opening_line(text: str) -> Optional[str]:
        """Extract recommended opening line"""
        patterns = [
            r'Recommended Opening Line[:\s]+["\']?([^"\n]+)["\']?',
            r'Opening Line[:\s]+["\']?([^"\n]+)["\']?',
            r'\*\*Opening[^:]*:[\s]+(.+?)(?=\n|\*\*|$)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                opening = match.group(1).strip()
                return opening if len(opening) > 20 else None
        
        return None
    
    @staticmethod
    def _extract_opportunity_level(text: str) -> Optional[str]:
        """Extract opportunity level (HIGH/MEDIUM/LOW)"""
        patterns = [
            r'Opportunity Level[:\s]+\*\*([A-Z]+)\*\*',
            r'\*\*Opportunity[^:]*:[\s]+([A-Z]+)',
            r'Estimated Opportunity Level[:\s]+\*\*([A-Z]+)\*\*',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                level = match.group(1).upper()
                if level in ['HIGH', 'MEDIUM', 'LOW']:
                    return level
        
        return None
    
    @staticmethod
    def _extract_top_reasons(text: str) -> Optional[str]:
        """Extract top reasons to engage"""
        patterns = [
            r'Top \d+ Reasons[^\n]*\n(.+?)(?=\n###|\n##|\n\*\*|$)',
            r'\*\*Top Reasons[^\n]*\n(.+?)(?=\n###|\n##|\n\*\*|$)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                reasons = match.group(1).strip()
                return reasons if len(reasons) > 30 else None
        
        return None
