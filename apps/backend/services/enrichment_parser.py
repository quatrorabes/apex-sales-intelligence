"""
APEX Enrichment Parser v2.1 - Production
Handles BOTH old (===) and NEW (## ###) formats
Filters empty sections automatically
"""
import re
from typing import Dict

class EnrichmentParser:
    """Parse raw enrichment profiles into structured sections"""
    
    def parse(self, raw_profile: str) -> Dict[str, any]:
        """
        Main parsing function - auto-detects format
        
        Returns:
            {
                "sections": {"person_overview": "text...", ...},
                "metadata": {"total_sections": 12, ...}
            }
        """
        if not raw_profile or not isinstance(raw_profile, str):
            return self._empty_result()
        
        # Detect format
        if "## " in raw_profile and ("Professional Profile" in raw_profile or "Company Intelligence" in raw_profile):
            format_type = "markdown_structured"
            sections = self._parse_markdown_structured(raw_profile)
        elif "=== PERSON RESEARCH" in raw_profile:
            format_type = "triple_equals"
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
    
    def _parse_markdown_structured(self, text: str) -> Dict[str, str]:
        """Parse NEW format with ## and ### headers"""
        sections = {}
        
        # Split by ## headers (top-level)
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
