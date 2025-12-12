"""
APEX Enrichment Parser v2.2 - Production
Handles BOTH apex_custom and enhanced formats
Added support for apex_custom three-stage format
"""
import re
from typing import Dict


class EnrichmentParser:
    """Parse raw enrichment profiles into structured sections"""
    
    def parse(self, raw_profile: str) -> Dict[str, any]:
        """
        Main parsing function - auto-detects format
        
        Supports:
        - apex_custom (=== ENRICHED PROFILE ===)
        - enhanced (## Professional Profile)
        - legacy (=== PERSON RESEARCH ===)
        
        Returns:
        {
            "sections": {"person_overview": "text...", ...},
            "metadata": {"total_sections": 12, ...}
        }
        """
        if not raw_profile or not isinstance(raw_profile, str):
            return self._empty_result()
        
        # Detect format
        if "=== ENRICHED PROFILE" in raw_profile or "APEX CUSTOM ENRICHMENT" in raw_profile:
            format_type = "apex_custom"
            sections = self._parse_apex_custom(raw_profile)
        elif "## " in raw_profile and ("Professional Profile" in raw_profile or "Company Intelligence" in raw_profile):
            format_type = "enhanced_markdown"
            sections = self._parse_enhanced_markdown(raw_profile)
        elif "=== PERSON RESEARCH" in raw_profile:
            format_type = "legacy_triple_equals"
            sections = self._parse_triple_equals(raw_profile)
        else:
            format_type = "unknown"
            sections = {"raw_text": raw_profile}
        
        # Filter empty sections
        sections = {k: v for k, v in sections.items() if v and len(v.strip()) > 0}
        
        return {
            "sections": sections,
            "metadata": {
                "total_sections": len(sections),
                "character_count": len(raw_profile),
                "format_detected": format_type
            }
        }
    
    def _parse_apex_custom(self, text: str) -> Dict[str, str]:
        """Parse apex_custom three-stage format with === markers"""
        sections = {}
        
        # Pattern: === ENRICHED PROFILE: Name - SECTION_NAME ===
        pattern = r'===\s*ENRICHED PROFILE:.*?-\s*([^=]+?)\s*===\n(.*?)(?=\n===|$)'
        matches = re.findall(pattern, text, re.DOTALL)
        
        for header, content in matches:
            header_clean = header.strip()
            content_clean = content.strip()
            
            if not content_clean:
                continue
            
            # Map apex_custom sections to standard keys
            if "CONTACT INFORMATION" in header_clean:
                sections["contact_info"] = content_clean
            
            elif "PERSON PROFILE" in header_clean:
                # Parse sub-sections
                subsections = self._parse_apex_subsections(content_clean)
                
                # Map to standard keys
                if "Overview" in subsections:
                    sections["overview"] = subsections["Overview"]
                if "Background" in subsections or "Background & Experience" in subsections:
                    sections["background_and_experience"] = subsections.get("Background & Experience", subsections.get("Background", ""))
                if "Education" in subsections:
                    sections["education"] = subsections["Education"]
                if "Recent Activity" in subsections or "Recent Activity Mentions" in subsections:
                    sections["recent_activity_and_news"] = subsections.get("Recent Activity Mentions", subsections.get("Recent Activity", ""))
                if "LinkedIn Activity" in subsections:
                    sections["linkedin_activity"] = subsections["LinkedIn Activity"]
                if "Top Skills" in subsections:
                    sections["skills_expertise"] = subsections["Top Skills"]
                
                # Full person profile
                sections["person_profile"] = content_clean
            
            elif "COMPANY PROFILE" in header_clean:
                # Parse sub-sections
                subsections = self._parse_apex_subsections(content_clean)
                
                if "Overview" in subsections:
                    sections["company_overview"] = subsections["Overview"]
                if "Products" in subsections or "Products Services" in subsections:
                    sections["products_services"] = subsections.get("Products Services", subsections.get("Products", ""))
                if "Leadership" in subsections:
                    sections["leadership_and_culture"] = subsections["Leadership"]
                if "Market" in subsections or "Market Competitors" in subsections:
                    sections["market_position"] = subsections.get("Market Competitors", subsections.get("Market", ""))
                if "Recent News" in subsections:
                    sections["company_recent_news"] = subsections["Recent News"]
                if "Strategic Context" in subsections:
                    sections["strategic_context"] = subsections["Strategic Context"]
                
                # Full company profile
                sections["company_research"] = content_clean
            
            elif "PERSONALITY ASSESSMENT" in header_clean:
                # Parse personality sub-sections
                subsections = self._parse_apex_subsections(content_clean)
                
                # This is the key section for frontend Personality tab
                personality_parts = []
                
                if "Myers-Briggs" in subsections or "MBTI Type" in subsections:
                    personality_parts.append(f"### Myers-Briggs Type Indicator (MBTI)\n{subsections.get('Myers-Briggs MBTI Type', subsections.get('Myers-Briggs', ''))}")
                
                if "DISC Profile" in subsections:
                    personality_parts.append(f"### DISC Profile\n{subsections['DISC Profile']}")
                
                if "StrengthsFinder" in subsections:
                    personality_parts.append(f"### StrengthsFinder Top 5 Themes\n{subsections['StrengthsFinder']}")
                
                if "Professional Communication Style" in subsections or "Communication Style" in subsections:
                    personality_parts.append(f"### Communication Preferences\n{subsections.get('Professional Communication Style', subsections.get('Communication Style', ''))}")
                
                # Combined personality section for frontend
                sections["personality_and_communication"] = "\n\n".join(personality_parts)
                
                # Also store full raw
                sections["personality_assessment"] = content_clean
            
            elif "SOCIAL MEDIA PROFILES" in header_clean:
                sections["social_profiles"] = content_clean
            
            elif "SALES INTELLIGENCE" in header_clean:
                # Parse sales sub-sections
                subsections = self._parse_apex_subsections(content_clean)
                
                if "Top 5 Talking Points" in subsections or "Talking Points" in subsections:
                    sections["talking_points"] = subsections.get("Top 5 Talking Points", subsections.get("Talking Points", ""))
                
                if "Sales Opportunities" in subsections:
                    opp_content = subsections["Sales Opportunities"]
                    
                    # Extract pain points
                    pain_match = re.search(r'Pain Points:(.*?)(?=Buying Triggers:|Current Signals:|$)', opp_content, re.DOTALL)
                    if pain_match:
                        sections["pain_points_and_challenges"] = pain_match.group(1).strip()
                    
                    # Extract buying triggers
                    trigger_match = re.search(r'Buying Triggers:(.*?)(?=Current Signals:|$)', opp_content, re.DOTALL)
                    if trigger_match:
                        sections["buying_triggers"] = trigger_match.group(1).strip()
                
                if "Value Proposition" in subsections:
                    sections["value_proposition"] = subsections["Value Proposition"]
                
                if "Relationship Building" in subsections:
                    sections["relationship_strategy"] = subsections["Relationship Building"]
                
                if "Objection Handling" in subsections:
                    sections["objection_handling"] = subsections["Objection Handling"]
                
                if "Outreach Strategy" in subsections:
                    sections["engagement_strategy"] = subsections["Outreach Strategy"]
                
                # Budget & authority extraction
                budget_match = re.search(r'(?:Budget|Authority|Decision)', content_clean, re.IGNORECASE)
                if budget_match:
                    sections["budget_and_authority"] = self._extract_paragraph(content_clean, budget_match.start())
                
                # Full sales intel
                sections["sales_intelligence"] = content_clean
            
            elif "NEWS" in header_clean or "FUN FACTS" in header_clean:
                sections["news_and_fun_facts"] = content_clean
            
            elif "ENRICHMENT NOTES" in header_clean:
                sections["enrichment_metadata"] = content_clean
        
        return sections
    
    def _parse_apex_subsections(self, content: str) -> Dict[str, str]:
        """Parse ### subsections within apex_custom sections"""
        subsections = {}
        
        # Pattern: ### Subsection Name
        pattern = r'###\s+([^\n]+)\n(.*?)(?=\n###|$)'
        matches = re.findall(pattern, content, re.DOTALL)
        
        for header, text in matches:
            key = header.strip()
            value = text.strip()
            if value:
                subsections[key] = value
        
        return subsections
    
    def _extract_paragraph(self, text: str, start_pos: int, num_lines: int = 5) -> str:
        """Extract a paragraph starting from position"""
        lines = text[start_pos:].split('\n')[:num_lines]
        return '\n'.join(line.strip() for line in lines if line.strip())
    
    def _parse_enhanced_markdown(self, text: str) -> Dict[str, str]:
        """Parse enhanced_enrichment markdown format (## headers)"""
        sections = {}
        
        # Pattern: ## Header
        main_pattern = r'##\s+(.+?)\n(.*?)(?=\n##|\Z)'
        main_matches = re.findall(main_pattern, text, re.DOTALL)
        
        for header, content in main_matches:
            header_clean = header.strip()
            
            if "Professional Profile" in header_clean:
                subsections = self._parse_subsections(content)
                sections.update({f"person_{k}": v for k, v in subsections.items()})
                if content.strip():
                    sections["person_profile"] = content.strip()
            
            elif "Company Intelligence" in header_clean:
                subsections = self._parse_subsections(content)
                sections.update({f"company_{k}": v for k, v in subsections.items()})
                if content.strip():
                    sections["company_intelligence"] = content.strip()
            
            elif "Sales Opportunities" in header_clean or "Sales Intelligence" in header_clean:
                subsections = self._parse_subsections(content)
                sections.update({f"sales_{k}": v for k, v in subsections.items()})
                if content.strip():
                    sections["sales_opportunities"] = content.strip()
            
            elif "Personality" in header_clean or "Working Style" in header_clean:
                sections["personality_and_communication"] = content.strip()
            
            else:
                key = self._clean_key(header_clean)
                if content.strip():
                    sections[key] = content.strip()
        
        return sections
    
    def _parse_subsections(self, content: str) -> Dict[str, str]:
        """Parse ### subsections"""
        subsections = {}
        pattern = r'###\s+(.+?)\n(.*?)(?=\n###|\n##|\Z)'
        matches = re.findall(pattern, content, re.DOTALL)
        
        for header, text in matches:
            key = self._clean_key(header)
            if text.strip():
                subsections[key] = text.strip()
        
        return subsections
    
    def _parse_triple_equals(self, text: str) -> Dict[str, str]:
        """Parse OLD format: === SECTION ==="""
        sections = {}
        pattern = r'===\s*([A-Z\s&]+?)(?::\s*[^\n]+)?\s*===\n(.*?)(?=\n===|\Z)'
        matches = re.findall(pattern, text, re.DOTALL | re.IGNORECASE)
        
        for header, content in matches:
            header_clean = header.strip().upper()
            
            if "PERSON RESEARCH" in header_clean:
                sections["person_research"] = content.strip()
            elif "COMPANY RESEARCH" in header_clean:
                sections["company_research"] = content.strip()
            elif "SALES INTELLIGENCE" in header_clean:
                sections["sales_intelligence"] = content.strip()
            elif "PERSONALITY" in header_clean:
                sections["personality_analysis"] = content.strip()
        
        return sections
    
    def _clean_key(self, text: str) -> str:
        """Convert header to clean key"""
        return text.lower().replace(" ", "_").replace("&", "and").replace("-", "_").replace("–", "_").replace("__", "_").strip("_")
    
    def _empty_result(self) -> Dict:
        return {
            "sections": {},
            "metadata": {"total_sections": 0, "character_count": 0, "format_detected": "none"}
        }


def parse_enrichment(raw_profile: str) -> Dict:
    """Convenience function"""
    parser = EnrichmentParser()
    return parser.parse(raw_profile)
