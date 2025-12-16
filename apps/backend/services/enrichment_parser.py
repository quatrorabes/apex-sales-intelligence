#!/usr/bin/env python3
"""
APEX Enrichment Parser v3.0 - Production
Parses raw enrichment profiles into structured sections
Handles ALL formats from enrichment engines
"""

import re
from typing import Dict, Any


class EnrichmentParser:
    """Parse raw enrichment profiles into structured sections"""

    def parse(self, raw_profile: str) -> Dict[str, Any]:
        """
        Main parsing function - auto-detects format

        Returns:
        {
            "sections": {
                "overview": "text...",
                "company_overview": "text...",
                "pain_points_and_challenges": "text...",
                ...
            },
            "metadata": {
                "total_sections": 12,
                "character_count": 8500,
                "format_detected": "markdown_v3"
            }
        }
        """
        if not raw_profile or not isinstance(raw_profile, str):
            return self._empty_result()

        # Detect format and parse
        if self._is_double_hash_format(raw_profile):
            # NEW FORMAT: ## section_name (from enrichment_engine.py)
            format_type = "markdown_v3"
            sections = self._parse_double_hash(raw_profile)
        elif "---" in raw_profile and "###" in raw_profile:
            # OLD FORMAT: ### SECTION NAME with ---
            format_type = "markdown_structured"
            sections = self._parse_markdown_structured(raw_profile)
        elif "===" in raw_profile:
            # LEGACY FORMAT: === SECTION ===
            format_type = "triple_equals"
            sections = self._parse_triple_equals(raw_profile)
        else:
            # FALLBACK: Try double hash, else raw
            sections = self._parse_double_hash(raw_profile)
            format_type = "markdown_v3" if len(sections) > 1 else "unknown"
            if format_type == "unknown":
                sections = {"raw_text": raw_profile}

        return {
            "sections": sections,
            "metadata": {
                "total_sections": len(sections),
                "character_count": len(raw_profile),
                "format_detected": format_type
            }
        }

    def _is_double_hash_format(self, text: str) -> bool:
        """Check if text uses ## section format"""
        # Look for ## followed by lowercase words (new format)
        pattern = r'^## [a-z_]+\s*$'
        return bool(re.search(pattern, text, re.MULTILINE))

    def _parse_double_hash(self, text: str) -> Dict[str, str]:
        """
        Parse NEW format from enrichment_engine.py
        
        Input: "## overview\nContent...\n\n## company_overview\nMore..."
        Output: {"overview": "Content...", "company_overview": "More..."}
        """
        sections = {}
        
        # Pattern matches ## section_name (lowercase, may have spaces or underscores)
        lines = text.split('\n')
        current_section = None
        current_content = []

        for line in lines:
            # Match ## header (case insensitive, various formats)
            match = re.match(r'^## ([A-Za-z][A-Za-z0-9_ &-]+)\s*$', line.strip())
            if match:
                # Save previous section
                if current_section:
                    sections[current_section] = '\n'.join(current_content).strip()
                
                # Start new section (normalize key)
                header = match.group(1)
                current_section = self._normalize_key(header)
                current_content = []
            else:
                if current_section:
                    current_content.append(line)

        # Save last section
        if current_section:
            sections[current_section] = '\n'.join(current_content).strip()

        # Also extract structured fields from content
        sections = self._extract_fields_from_sections(sections, text)

        return sections

    def _normalize_key(self, header: str) -> str:
        """Normalize header to snake_case key"""
        key = header.lower()
        key = key.replace(' ', '_')
        key = key.replace('&', 'and')
        key = key.replace('-', '_')
        key = re.sub(r'_+', '_', key)  # Remove double underscores
        key = key.strip('_')
        return key

    def _extract_fields_from_sections(self, sections: Dict[str, str], full_text: str) -> Dict[str, str]:
        """Extract additional structured fields from parsed sections"""
        
        # Extract pain points if in a section
        for key in ['pain_points_and_challenges', 'sales_intelligence', 'pain_points']:
            if key in sections:
                pain_bullets = re.findall(r'^[-•]\s*(.+)$', sections[key], re.MULTILINE)
                if pain_bullets:
                    sections['pain_points_list'] = pain_bullets

        # Extract talking points
        for key in ['sales_intelligence', 'talking_points']:
            if key in sections:
                talking_match = re.findall(r'^\d+\.\s*(.+)$', sections[key], re.MULTILINE)
                if talking_match:
                    sections['talking_points_list'] = talking_match[:5]

        # Extract MBTI if present
        mbti_match = re.search(r'Myers-Briggs.*?:\s*\**([EISNTFJP]{4})\**', full_text, re.IGNORECASE)
        if mbti_match:
            sections['mbti'] = mbti_match.group(1)

        # Extract DISC if present
        disc_match = re.search(r'DISC.*?:\s*\**([DISC][a-z]*)\**', full_text, re.IGNORECASE)
        if disc_match:
            sections['disc'] = disc_match.group(1)

        # Extract confidence score
        conf_match = re.search(r'Confidence.*?:\s*(\d+)%?', full_text, re.IGNORECASE)
        if conf_match:
            sections['confidence_score'] = conf_match.group(1)

        # Extract best channel
        channel_match = re.search(r'Best Channel:\s*([^\n]+)', full_text, re.IGNORECASE)
        if channel_match:
            sections['best_channel'] = channel_match.group(1).strip()

        return sections

    def _parse_markdown_structured(self, text: str) -> Dict[str, str]:
        """Parse OLD format with ### headers and ---"""
        sections = {}

        # Split by main section headers (###)
        main_pattern = r'###\s+(.+?)\n(.*?)(?=###|$)'
        main_matches = re.findall(main_pattern, text, re.DOTALL)

        for header, content in main_matches:
            header_clean = header.strip()
            key = self._normalize_key(header_clean)
            
            # Map old keys to new standardized keys
            key_mapping = {
                'person_profile': 'person_profile',
                'professional_profile': 'person_profile',
                'company_profile': 'company_overview',
                'company_intelligence': 'company_overview',
                'personality_assessment': 'personality_and_communication',
                'sales_intelligence': 'sales_intelligence',
                'sales_opportunities': 'sales_intelligence',
                'social_media_profiles': 'social_profiles',
                'news_and_fun_facts': 'fun_facts',
                'enrichment_notes': 'enrichment_notes',
            }
            
            mapped_key = key_mapping.get(key, key)
            sections[mapped_key] = content.strip()

            # Parse subsections (####)
            subsections = self._parse_subsections(content)
            for sub_key, sub_content in subsections.items():
                sections[f"{mapped_key}_{self._normalize_key(sub_key)}"] = sub_content

        return sections

    def _parse_subsections(self, content: str) -> Dict[str, str]:
        """Parse subsections within a section (#### headers)"""
        subsections = {}

        pattern = r'####\s+(.+?)\n(.*?)(?=####|$)'
        matches = re.findall(pattern, content, re.DOTALL)

        for header, text in matches:
            key = header.strip()
            subsections[key] = text.strip()

        return subsections

    def _parse_triple_equals(self, text: str) -> Dict[str, str]:
        """Parse LEGACY format (===SECTION===)"""
        sections = {}

        pattern = r'={3,}\s*([A-Z\s]+)\s*={3,}(.*?)(?===|$)'
        matches = re.findall(pattern, text, re.DOTALL | re.IGNORECASE)

        for header, content in matches:
            key = self._normalize_key(header.strip())
            sections[key] = content.strip()

        return sections

    def _empty_result(self) -> Dict:
        """Return empty result structure"""
        return {
            "sections": {},
            "metadata": {
                "total_sections": 0,
                "character_count": 0,
                "format_detected": "none"
            }
        }


def parse_enrichment(raw_profile: str) -> Dict:
    """Convenience function"""
    parser = EnrichmentParser()
    return parser.parse(raw_profile)
