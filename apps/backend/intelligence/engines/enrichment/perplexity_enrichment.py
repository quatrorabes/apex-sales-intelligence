#!/usr/bin/env python3
"""
SIMPLIFIED: Get raw, long-form profiles from Perplexity
No parsing - just comprehensive text responses
"""

import os
import json
import requests
from datetime import datetime
from typing import Dict

class PerplexityEnrichment:
    """Get comprehensive long-form profiles without parsing"""

    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("PERPLEXITY_API_KEY")
        if not self.api_key:
            raise ValueError("PERPLEXITY_API_KEY not set")

    def enrich_contact(self, contact: Dict) -> Dict:
        """Get comprehensive profile using YOUR exact prompt"""
        
        # Extract contact info
        person_info = self._extract_person_info(contact)
        name = person_info["name"]
        company = person_info.get("company", "")
        linkedin = contact.get("linkedin_url", "")
        
        print(f"\n🎯 GETTING COMPREHENSIVE PROFILE")
        print(f"   Name: {name}")
        print(f"   Company: {company}")
        
        # YOUR EXACT COMPREHENSIVE PROMPT
        master_prompt = f"""You are a professional profile-building assistant. Generate up-to-date profile using both public web sources for {name} at {company}. Use sources such as LinkedIn ({linkedin}) & Internet.

For a company ({company}), structure the profile as:
1. Overview – Description, mission, founding details, and HQ
2. Products & Services – Key offerings and markets served
3. Leadership – Key executives and founders
4. Market & Competitors – Industry, position, key competitors
5. Recent News – Major announcements, deals, or product launches

For a person ({name}), structure the profile as:
1. Overview – Current title and organization
2. Background – Work history, notable achievements
3. Education – Degrees and institutions
4. Recent Mentions – Any news, public appearances, LinkedIn posts, or online presence
5. Find instagram, facebook, and twitter user profiles.
6. Personality Detail - perform a Myers briggs assessment.
7. Compose and interpret Myers-Briggs Personality assessment summary.
8. Evaluate potential talking points regarding sales opportunities.
9. Search deals database for any past or current "deal"
10. Update all fields with new or inaccurate information
11. Find any relevant company news or fun facts. Populate results in "talking points" tab and on relevant company page.
12. Trigger Events - Identify any recent events that create sales opportunities (new funding, expansion, leadership changes)
13. Competitive Intelligence - What solutions are they currently using that we could replace?
14. Warm Introduction Paths - Find mutual connections or shared affiliations
15. Engagement Preferences - Best time to reach, preferred communication channels
16. Decision Making Style - How they evaluate vendors and make purchasing decisions
17. Budget Authority - Signs of budget availability or fiscal year timing
18. Success Metrics - What KPIs they care about based on their role

Additionally, provide:
- AI Score Reasoning: Why this is a high-value contact (100+ words)
- Relationship Tips: Based on their personality type
- Pain Points: Specific to their role and industry
- Outreach Approach: Multi-paragraph personalized approach

Provide comprehensive, detailed information for each section. Be specific with names, dates, amounts, and facts."""

        # Call Perplexity API
        print(f"\n   Calling Perplexity for comprehensive profile...")
        
        try:
            response = requests.post(
                "https://api.perplexity.ai/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "sonar-pro",  # ⭐ CORRECTED MODEL NAME
                    "messages": [
                        {
                            "role": "system",
                            "content": "You are a professional profile-building assistant. Generate comprehensive, detailed profiles with specific facts, numbers, and actionable intelligence."
                        },
                        {
                            "role": "user",
                            "content": master_prompt
                        }
                    ],
                    "temperature": 0.2,  # Lower for more factual responses
                    "max_tokens": 4000,  # Maximum response length
                    # Remove invalid parameters
                    # "return_citations": True,  # Not supported
                    # "search_domain_filter": [],  # Not supported
                    # "search_recency_filter": "year",  # Not supported
                    # "top_k": 10  # Not supported
                },
                timeout=60
            )
            
            if response.status_code == 200:
                # Get the raw response text
                result_json = response.json()
                full_response = result_json["choices"][0]["message"]["content"]
                print(f"   ✅ Got {len(full_response)} characters of profile data")
                
                # Save to file for review
                output_file = f"profile_{contact.get('id', 'unknown')}.txt"
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(f"COMPREHENSIVE PROFILE: {name} at {company}\n")
                    f.write(f"Generated: {datetime.now()}\n")
                    f.write("=" * 60 + "\n\n")
                    f.write(full_response)
                
                print(f"   💾 Full profile saved to: {output_file}")
                
                # Return the raw long-form text without parsing
                return {
                    "status": "success",
                    "enrichment_data": {
                        'person_name': name,
                        'company': company,
                        'overview': full_response[:5000],  # First 5000 chars for overview
                        'full_profile': full_response,  # Complete unprocessed profile
                        'raw_responses': [{"content": full_response, "model": "sonar-pro"}]
                    },
                    "person_name": name,
                    "company_name": company,
                    "overview": full_response[:2000],  # Shorter version for display
                    "perplexity_insights": full_response,  # Full text
                    "raw_file": output_file
                }
                
            else:
                print(f"   ❌ API error: {response.status_code}")
                print(f"   Response: {response.text}")  # Debug info
                return {
                    "status": "error", 
                    "message": f"API error: {response.status_code}",
                    "enrichment_data": {
                        'person_name': name,
                        'company': company,
                        'overview': f"API Error {response.status_code}",
                        'full_profile': "",
                        'raw_responses': []
                    }
                }
                
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
            return {
                "status": "error",
                "message": str(e),
                "enrichment_data": {
                    'person_name': name,
                    'company': company,
                    'overview': f"Error: {str(e)}",
                    'full_profile': "",
                    'raw_responses': []
                }
            }
    
    def _extract_person_info(self, contact: Dict) -> Dict:
        """Extract basic person info"""
        firstname = contact.get("firstname", "").strip() if contact.get("firstname") else ""
        lastname = contact.get("lastname", "").strip() if contact.get("lastname") else ""
        
        if firstname or lastname:
            name = f"{firstname} {lastname}".strip()
        elif contact.get("name"):
            name = contact.get("name").strip()
        else:
            name = ""
        
        return {
            "name": name,
            "company": contact.get("company", "").strip() if contact.get("company") else ""
        }


# ⭐ CRITICAL: This MUST be at module level (NO indentation!)
def enrich_contact(contact_id: int, contact: Dict) -> Dict:
    """Standalone function for API compatibility"""
    try:
        print(f"\n{'='*60}")
        print(f"🎯 COMPREHENSIVE PROFILE ENRICHMENT")
        print(f"{'='*60}")
        print(f"Contact ID: {contact_id}")
        print(f"Name: {contact.get('name', '')}")
        print(f"Company: {contact.get('company', '')}")
        
        # Initialize the enrichment class
        enricher = PerplexityEnrichment()
        
        # Call the class method
        result = enricher.enrich_contact(contact)
        
        print(f"✅ Profile enrichment complete")
        print(f"{'='*60}")
        
        return result
    
    except Exception as e:
        print(f"❌ Enrichment error: {str(e)}")
        return {
            "status": "error",
            "message": str(e),
            "enrichment_data": {
                "person_name": contact.get("name", ""),
                "company": contact.get("company", ""),
                "overview": f"Error during enrichment: {str(e)}",
                "full_profile": "",
                "raw_responses": []
            }
        }
