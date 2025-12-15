#!/usr/bin/env python3

"""
APEX Enrichment Parser v2.1
Handles BOTH old (===) and NEW (## ###) formats
"""
import re
from typing import Dict, Optional

class EnrichmentParser:
	"""Parse raw enrichment profiles into structured sections"""
	
	def parse(self, raw_profile: str) -> Dict[str, any]:
		"""
		Main parsing function - auto-detects format
		
		Returns:
			{
				"sections": {
					"person_overview": "text...",
					"person_background": "text...",
					"company_overview": "text...",
					"sales_opportunities": "text...",
					...
				},
				"metadata": {...}
			}
		"""
		if not raw_profile or not isinstance(raw_profile, str):
			return self._empty_result()
		
		# Detect format
		if "## " in raw_profile and " – Professional Profile" in raw_profile:
			format_type = "markdown_structured"
			sections = self._parse_markdown_structured(raw_profile)
		elif "=== PERSON RESEARCH" in raw_profile:
			format_type = "triple_equals"
			sections = self._parse_triple_equals(raw_profile)
		else:
			format_type = "unknown"
			sections = {"raw_text": raw_profile}
			
		return {
			"sections": sections,
			"metadata": {
				"total_sections": len(sections),
				"character_count": len(raw_profile),
				"format_detected": format_type
			}
		}
	
	def _parse_markdown_structured(self, text: str) -> Dict[str, str]:
		"""
		Parse NEW format:
		## Name – Professional Profile
		### Overview
		### Background & Experience
		## Company – Company Intelligence
		## Sales Opportunities
		"""
		sections = {}
		
		# Split by ## headers (top-level sections)
		main_pattern = r'##\s+(.+?)\n(.*?)(?=\n##|\Z)'
		main_matches = re.findall(main_pattern, text, re.DOTALL)
		
		for header, content in main_matches:
			header_clean = header.strip()
			
			# Map to section keys
			if "Professional Profile" in header_clean or "– Professional Profile" in header_clean:
				# Parse subsections within person profile
				subsections = self._parse_subsections(content)
				sections.update({f"person_{k}": v for k, v in subsections.items()})
				
			elif "Company Intelligence" in header_clean:
				# Parse company subsections
				subsections = self._parse_subsections(content)
				sections.update({f"company_{k}": v for k, v in subsections.items()})
				
			elif "Sales Opportunities" in header_clean or "Sales Intelligence" in header_clean:
				subsections = self._parse_subsections(content)
				sections.update({f"sales_{k}": v for k, v in subsections.items()})
				sections["sales_intelligence"] = content.strip()  # Also store full section
				
			else:
				# Generic section
				key = header_clean.lower().replace(" ", "_").replace("–", "").replace("-", "_")
				sections[key] = content.strip()
				
		return sections
	
	def _parse_subsections(self, content: str) -> Dict[str, str]:
		"""Parse ### subsections within a ## section"""
		subsections = {}
		pattern = r'###\s+(.+?)\n(.*?)(?=\n###|\n##|\Z)'
		matches = re.findall(pattern, content, re.DOTALL)
		
		for header, text in matches:
			key = header.strip().lower().replace(" ", "_").replace("&", "and")
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
	
	def _empty_result(self) -> Dict:
		return {
			"sections": {},
			"metadata": {
				"total_sections": 0,
				"character_count": 0,
				"format_detected": "none"
			}
		}
	
	
# Convenience function
def parse_enrichment(raw_profile: str) -> Dict:
	parser = EnrichmentParser()
	return parser.parse(raw_profile)
