#!/usr/bin/env python3

#!/usr/bin/env python3
"""
APEX Intelligence Compiler
Transforms raw Perplexity search results into comprehensive intelligence dossiers
Uses GPT-4 to extract and structure deep intelligence
"""

import os
import json
from openai import OpenAI
from typing import Dict, List
from datetime import datetime


class IntelligenceCompiler:
		"""Compile deep intelligence dossiers from raw search results"""
	
		def __init__(self):
				self.openai_key = os.getenv('OPENAI_API_KEY')
				if not self.openai_key:
						raise ValueError("OPENAI_API_KEY not set in environment")
				self.client = OpenAI(api_key=self.openai_key)
			
		def compile_dossier(self, contact: Dict, raw_results: List[Dict]) -> Dict:
			"""Compile dossier from raw Perplexity profile"""
			
			# Get the full profile text
			if raw_results and len(raw_results) > 0:
				full_profile = raw_results[0].get('content', '')
			else:
				full_profile = "No profile data available"
				
			# Now let GPT-4 structure it
			prompt = f"""Take this comprehensive profile and structure it into sections:
		
		PROFILE DATA:
		{full_profile}
		
		Create a structured intelligence dossier with:
		- Overview (summary)
		- Background (work history)
		- Pain points (specific to their role)
		- Talking points (for sales outreach)
		- Personality profile
		- Trigger events
		- etc.
		
		Return as JSON."""
			
			# GPT-4 processes the raw text
			# ... rest of your GPT-4 code
			
CONTACT: {name} at {company}

SEARCH RESULTS:
{combined_text[:12000]}

Generate a comprehensive intelligence dossier in JSON format with these EXACT sections:

{{
	"overview": {{
		"current_title": "exact title found",
		"organization": "company name",
		"location": "city, state",
		"summary": "2-3 sentence overview of their role and expertise"
	}},
	
	"background": {{
		"years_experience": "X+ years",
		"career_summary": "paragraph about their career arc",
		"work_history": [
			{{
				"company": "Company Name",
				"title": "Title",
				"dates": "2020-Present",
				"achievements": ["achievement 1", "achievement 2"]
			}}
		],
		"major_achievements": [
			"Closed $XXM in deals",
			"Top performer award",
			"etc"
		]
	}},
	
	"education": [
		{{
			"school": "University Name",
			"degree": "B.S. in Field",
			"year": "1995",
			"honors": "if any"
		}}
	],
	
	"online_presence": {{
		"linkedin": {{
			"active": true/false,
			"activity": "description of their activity",
			"engagement_level": "high/medium/low"
		}},
		"twitter": "handle or null",
		"instagram": "handle or null",
		"facebook": "profile info or null",
		"other": []
	}},
	
	"company_intelligence": {{
		"company_overview": "what the company does",
		"market_position": "their standing in industry",
		"competitors": ["Company 1", "Company 2", "Company 3"],
		"key_executives": [
			{{"name": "CEO Name", "title": "CEO"}}
		],
		"recent_news": [
			"News item 1",
			"News item 2"
		]
	}},
	
	"skills_expertise": [
		"Credit analysis",
		"SBA lending",
		"Business development",
		"etc"
	],
	
	"personality_profile": {{
		"mbti_inference": "ENTJ",
		"assessment": "paragraph about their personality",
		"working_style": "how they work",
		"communication_preference": "email/phone/linkedin"
	}},
	
	"sales_intelligence": {{
		"talking_points": [
			"Point 1: why this matters",
			"Point 2: their pain point",
			"Point 3: opportunity"
		],
		"value_propositions": [
			"What resonates with them"
		],
		"objection_handlers": {{
			"common_objection": "how to handle it"
		}},
		"best_approach": "email first / call directly / linkedin message"
	}},
	
	"deals_database": [
		{{
			"deal_type": "CRE Purchase",
			"amount": "$8M",
			"year": "2022",
			"notes": "details if available"
		}}
	],
	
	"fun_facts": [
		"Interesting fact 1",
		"Company milestone",
		"Personal interest"
	],
	
	"action_items": [
		"Update HubSpot with this intel",
		"Schedule follow-up based on timing signals",
		"Personalize outreach with talking points"
	]
}}

CRITICAL INSTRUCTIONS:
- Extract REAL information from search results - do NOT make up data
- If information is not found, use "Not available" or leave empty []
- Infer MBTI based on communication style, career choices, achievements
- Generate sales talking points based on their role, company, and achievements
- Focus on ACTIONABLE intelligence for sales/relationship building
- Be thorough but concise - quality over quantity

Return ONLY valid JSON. No other text."""
			
				try:
						response = self.client.chat.completions.create(
								model="gpt-4-turbo",
								messages=[
										{
												"role": "system",
												"content": "You are an elite business intelligence analyst specializing in deep research and actionable sales intelligence. You extract structured insights from unstructured data and create comprehensive dossiers."
										},
										{
												"role": "user",
												"content": prompt
										}
								],
								temperature=0.3,
								max_tokens=4000,
								response_format={"type": "json_object"}
						)
					
						dossier_text = response.choices[0].message.content
						dossier = json.loads(dossier_text)
					
						print(f"✅ Intelligence dossier compiled successfully")
						return dossier
			
				except Exception as e:
						print(f"❌ Error compiling dossier: {e}")
						return self._generate_fallback_dossier(contact, combined_text)
			
		def _generate_fallback_dossier(self, contact: Dict, combined_text: str) -> Dict:
				"""Generate basic dossier if GPT-4 fails"""
				return {
						"overview": {
								"current_title": contact.get('title', 'Not available'),
								"organization": contact.get('company', ''),
								"location": "Not available",
								"summary": f"Professional at {contact.get('company', 'their organization')}"
						},
						"background": {
								"years_experience": "Not available",
								"career_summary": "Limited information available",
								"work_history": [],
								"major_achievements": []
						},
						"education": [],
						"online_presence": {},
						"company_intelligence": {},
						"skills_expertise": [],
						"personality_profile": {},
						"sales_intelligence": {
								"talking_points": ["Schedule discovery call to learn more"],
								"value_propositions": [],
								"objection_handlers": {},
								"best_approach": "email first"
						},
						"deals_database": [],
						"fun_facts": [],
						"action_items": ["Gather more information via direct outreach"]
				}
	
		def _assess_data_quality(self, dossier: Dict) -> str:
				"""Assess quality of compiled intelligence"""
				score = 0
			
				# Check completeness of key sections
				if dossier.get('overview', {}).get('current_title'):
						score += 20
				if len(dossier.get('background', {}).get('work_history', [])) > 0:
						score += 20
				if len(dossier.get('education', [])) > 0:
						score += 15
				if dossier.get('company_intelligence', {}).get('company_overview'):
						score += 15
				if len(dossier.get('skills_expertise', [])) > 0:
						score += 10
				if len(dossier.get('sales_intelligence', {}).get('talking_points', [])) > 0:
						score += 20
					
				if score >= 80:
						return "EXCELLENT"
				elif score >= 60:
						return "GOOD"
				elif score >= 40:
						return "FAIR"
				else:
						return "LIMITED"
			
		def _calculate_completeness(self, dossier: Dict) -> int:
				"""Calculate completeness score 0-100"""
				sections = [
						'overview',
						'background',
						'education',
						'online_presence',
						'company_intelligence',
						'skills_expertise',
						'personality_profile',
						'sales_intelligence',
						'deals_database',
						'fun_facts',
						'action_items'
				]
			
				completed = sum(1 for section in sections if dossier.get(section))
				return int((completed / len(sections)) * 100)
	
	
# Quick test function
def compile_intelligence(contact: Dict, raw_results: List[Dict]) -> Dict:
		"""Quick function to compile intelligence"""
		compiler = IntelligenceCompiler()
		return compiler.compile_dossier(contact, raw_results)


if __name__ == "__main__":
		print("🧠 APEX Intelligence Compiler")
		print("Transforms raw search results into actionable intelligence dossiers")
	