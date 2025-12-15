#!/usr/bin/env python3
"""
DASHBOARD BRIDGE - Complete Version with update_contact method
"""

import json
import os
from datetime import datetime
from typing import Dict

class DashboardBridge:
    """Direct bridge from enrichment to dashboard"""

    def __init__(self):
        self.enrichment_output_dir = "."
        self.dashboard_store = "dashboard_data.json"

    def transfer_to_dashboard(self, contact_id: int, enrichment_result: Dict) -> bool:
        """Transfer enrichment result directly to dashboard"""
        try:
            print(f"🔄 Transferring data to dashboard for contact {contact_id}")

            # Structure the data for dashboard
            dashboard_data = self._structure_for_dashboard(enrichment_result)

            # Load existing dashboard data
            if os.path.exists(self.dashboard_store):
                with open(self.dashboard_store, 'r') as f:
                    all_data = json.load(f)
            else:
                all_data = {}

            # Update with new data
            all_data[str(contact_id)] = dashboard_data

            # Save back to dashboard store
            with open(self.dashboard_store, 'w') as f:
                json.dump(all_data, f, indent=2)

            print(f"✅ Dashboard updated for contact {contact_id}")
            print(f"   Name: {dashboard_data['contact_info']['name']}")
            print(f"   Company: {dashboard_data['contact_info']['company']}")

            return True

        except Exception as e:
            print(f"❌ Error transferring to dashboard: {e}")
            return False

    def update_contact(self, contact_id: int, dashboard_data: Dict) -> bool:
        """Update a contact in the dashboard (method that was missing!)"""
        try:
            # Load existing dashboard data
            if os.path.exists(self.dashboard_store):
                with open(self.dashboard_store, 'r') as f:
                    all_data = json.load(f)
            else:
                all_data = {}

            # Update with new data
            all_data[str(contact_id)] = dashboard_data

            # Save back to dashboard store
            with open(self.dashboard_store, 'w') as f:
                json.dump(all_data, f, indent=2)

            print(f"✅ Dashboard updated for contact {contact_id}")
            return True

        except Exception as e:
            print(f"❌ Error updating dashboard: {e}")
            return False

    def _structure_for_dashboard(self, enrichment: Dict) -> Dict:
        """Structure enrichment data for dashboard display"""

        # Get the enrichment_data if nested
        if 'enrichment_data' in enrichment:
            data = enrichment['enrichment_data']
        else:
            data = enrichment

        return {
            "contact_info": {
                "name": data.get("person_name", "") or data.get("name", ""),
                "title": data.get("current_title", "") or data.get("title", ""),
                "company": data.get("company", ""),
                "email": data.get("email", ""),
                "phone": data.get("phone", ""),
                "linkedin": data.get("linkedin_url", "") or data.get("linkedin", "")
            },
            "intelligence": {
                "overview": data.get("overview", "") or data.get("person_overview", ""),
                "background": data.get("background", ""),
                "education": data.get("education", ""),
                "myers_briggs": data.get("myers_briggs", ""),
                "recent_activity": data.get("recent_activity", []) or data.get("recent_mentions", [])
            },
            "engagement": {
                "pain_points": data.get("pain_points", []),
                "talking_points": data.get("talking_points", []),
                "trigger_events": data.get("trigger_events", []),
                "recent_deals": data.get("recent_deals", [])
            },
            "scoring": {
                "persona": data.get("persona", ""),
                "score": data.get("score", 0),
                "priority": data.get("priority", "medium")
            },
            "company_intel": {
                "overview": data.get("company_overview", ""),
                "products": data.get("products_services", ""),
                "recent_news": data.get("recent_company_news", []),
                "market_position": data.get("market_position", "")
            },
            "metadata": {
                "last_enriched": datetime.now().isoformat(),
                "data_quality": self._assess_quality(data),
                "completeness": self._calculate_completeness(data)
            }
        }

    def _assess_quality(self, data: Dict) -> str:
        """Assess data quality"""
        important_fields = ['person_name', 'company', 'current_title', 'background']
        filled = sum(1 for field in important_fields if data.get(field))

        if filled >= 3:
            return "good"
        elif filled >= 2:
            return "moderate"
        else:
            return "limited"

    def _calculate_completeness(self, data: Dict) -> float:
        """Calculate completeness percentage"""
        all_fields = ['person_name', 'company', 'current_title', 'background', 
                      'education', 'pain_points', 'talking_points']
        filled = sum(1 for field in all_fields if data.get(field))
        return round((filled / len(all_fields)) * 100, 1)

    def get_dashboard_data(self, contact_id: int) -> Dict:
        """Get data from dashboard for a contact"""
        try:
            if os.path.exists(self.dashboard_store):
                with open(self.dashboard_store, 'r') as f:
                    all_data = json.load(f)
                return all_data.get(str(contact_id), {})
            return {}
        except:
            return {}


def hook_after_enrichment(contact_id: int, enrichment_result: Dict):
    """Call this RIGHT AFTER enrichment completes"""
    bridge = DashboardBridge()
    return bridge.transfer_to_dashboard(contact_id, enrichment_result)
