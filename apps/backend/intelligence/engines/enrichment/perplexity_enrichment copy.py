#!/usr/bin/env python3
"""
FORCE REAL WEB SEARCH - No Restrictions!
backend/intelligence/enrichment/perplexity_enrichment.py
"""

import os
import json
import requests
from datetime import datetime
from typing import Dict, Optional

class PerplexityEnrichment:
    """Force REAL web searching without restrictions"""

    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("PERPLEXITY_API_KEY")
        if not self.api_key:
            raise ValueError("PERPLEXITY_API_KEY not set")

    def enrich_contact(self, contact: Dict) -> Dict:
        """Multi-query approach to force real searching"""
        person_info = self._extract_person_info(contact)

        name = person_info["name"]
        company = person_info.get("company", "")

        print(f"\n🔍 FORCING REAL WEB SEARCH...")
        print(f"   Name: {name}")
        print(f"   Company: {company}")

        all_responses = []

        # QUERY 1: Direct web search command
        query1 = f"""Search the web and find information about {name} who works at {company}. 
        Do NOT say "no information found" - actually search Google, LinkedIn, company websites, news sites.
        Find their job title, work history, education, and contact information."""

        print(f"\n   Query 1: Direct person search...")
        response1 = self._call_api_with_search(query1)
        all_responses.append(response1)

        # QUERY 2: Company-specific search
        query2 = f"""Search the web for {company}. Find their website, executive team, products, services, and recent news.
        Look for {name} on their team page or leadership page."""

        print(f"   Query 2: Company search...")
        response2 = self._call_api_with_search(query2)
        all_responses.append(response2)

        # QUERY 3: LinkedIn-specific search
        query3 = f"""Search LinkedIn for {name} {company}. Find their profile, work history, education, and connections."""

        print(f"   Query 3: LinkedIn search...")
        response3 = self._call_api_with_search(query3)
        all_responses.append(response3)

        # QUERY 4: News and deals search
        query4 = f"""Search Google News and press releases for {name} {company}. Find any deals, transactions, or announcements involving them."""

        print(f"   Query 4: News/deals search...")
        response4 = self._call_api_with_search(query4)
        all_responses.append(response4)

        # Combine all responses
        combined_response = "\n\n".join(all_responses)

        # Save for debugging
        with open(f"search_results_{contact.get('id', 'unknown')}.txt", "w") as f:
            f.write(f"Contact: {name} from {company}\n")
            f.write(f"Timestamp: {datetime.now()}\n")
            f.write("=" * 60 + "\n")
            for i, response in enumerate(all_responses, 1):
                f.write(f"\nQUERY {i} RESPONSE:\n")
                f.write("=" * 40 + "\n")
                f.write(response)
                f.write("\n")

        print(f"\n💾 All responses saved to: search_results_{contact.get('id', 'unknown')}.txt")

        # Parse combined results
        enrichment_data = self._parse_all_responses(combined_response, person_info)

        return {
            "status": "success",
            "enrichment_data": enrichment_data,
            "person_name": enrichment_data.get("person_name", name),
            "company_name": enrichment_data.get("company", company),
            "pain_points": [],
            "talking_points": [],
            "myers_briggs": "",
            "overview": enrichment_data.get("overview", ""),
            "background": enrichment_data.get("background", ""),
            "trigger_events": []
        }

    def _extract_person_info(self, contact: Dict) -> Dict:
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

    def _call_api_with_search(self, query: str) -> str:
        """Call API with explicit search instructions"""
        try:
            # Try different approaches
            approaches = [
                {
                    "model": "sonar-pro",
                    "system": "You are a web search assistant. Search the internet for information. Do not say 'no information found' - actually search and find data.",
                    "temperature": 0.5
                },
                {
                    "model": "sonar",
                    "system": "Search the web and provide all available information. Use Google, LinkedIn, news sites, and company websites.",
                    "temperature": 0.7
                }
            ]

            for approach in approaches:
                response = requests.post(
                    "https://api.perplexity.ai/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": approach["model"],
                        "messages": [
                            {
                                "role": "system",
                                "content": approach["system"]
                            },
                            {
                                "role": "user",
                                "content": query
                            }
                        ],
                        "temperature": approach["temperature"],
                        "max_tokens": 4000,
                        "return_citations": True,
                        "return_images": False,
                        "return_related_questions": False,
                        "search_recency_filter": "year",  # Broader time range
                        "top_k": 10  # More search results
                    },
                    timeout=60
                )

                if response.status_code == 200:
                    content = response.json()["choices"][0]["message"]["content"]

                    # Check if we got real results
                    if "no information" not in content.lower() and "not found" not in content.lower():
                        print(f"      ✓ Got results with {approach['model']}")
                        return content
                    else:
                        print(f"      ⚠️ No results with {approach['model']}, trying next...")
                        continue
                else:
                    print(f"      ❌ API error {response.status_code}")
                    continue

            return "No results obtained"

        except Exception as e:
            print(f"❌ Error: {str(e)}")
            return ""

    def _parse_all_responses(self, combined: str, person_info: Dict) -> Dict:
        """Parse combined responses"""
        import re

        data = {
            "person_name": person_info["name"],
            "company": person_info["company"],
            "current_title": "",
            "overview": "",
            "background": "",
            "education": "",
            "work_history": []
        }

        # Look for job titles
        title_patterns = [
            r"(?:is|serves as|works as)\s+(?:a|an|the)?\s*([^,\.\n]+(?:President|VP|Director|Manager|Officer)[^,\.\n]*)",
            r"([^,\.\n]*(?:President|VP|Director|Manager|Officer)[^,\.\n]*)\s+at\s+",
        ]

        for pattern in title_patterns:
            match = re.search(pattern, combined, re.IGNORECASE)
            if match:
                data["current_title"] = match.group(1).strip()
                print(f"\n   ✓ Found title: {data['current_title'][:50]}")
                break

        # Look for education
        edu_pattern = r"([^,\.\n]*(?:University|College|Institute)[^,\.\n]*(?:BA|BS|MBA|MS|PhD)?[^,\.\n]*)"
        edu_match = re.search(edu_pattern, combined, re.IGNORECASE)
        if edu_match:
            data["education"] = edu_match.group(1).strip()
            print(f"   ✓ Found education: {data['education'][:50]}")

        # Build overview
        if data["current_title"]:
            data["overview"] = f"{data['person_name']} - {data['current_title']} at {data['company']}"

        return data


def enrich_contact(contact_id: int, contact: Dict) -> Dict:
    """Force real web searching"""
    try:
        print(f"\n" + "=" * 80)
        print(f"🚀 FORCING REAL WEB SEARCH - NO RESTRICTIONS")
        print("=" * 80)
        print(f"Contact ID: {contact_id}")
        print(f"Name: {contact.get('name', '')}")
        print(f"Company: {contact.get('company', '')}")
        print(f"\nThis will change your life")

        enricher = PerplexityEnrichment()
        result = enricher.enrich_contact(contact)

        print(f"\n✅ Search complete - check saved file for all results")
        print("=" * 80)

        return result

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return {"status": "error", "message": str(e)}
