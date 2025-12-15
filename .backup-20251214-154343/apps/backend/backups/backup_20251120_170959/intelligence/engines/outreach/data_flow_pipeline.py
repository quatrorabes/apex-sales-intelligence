#!/usr/bin/env python3
"""
DATA FLOW PIPELINE - LOGIC ONLY
This file contains ONLY the processing logic
ALL endpoints go in main.py
"""

import json
import os
from datetime import datetime
from typing import Dict, Optional

# ===============================
# PROCESSING LOGIC ONLY
# ===============================

class EnrichmentProcessor:
    """Process enrichment output and prepare for dashboard"""

    def __init__(self):
        self.output_file = "output.txt"

    def process_output_file(self) -> Dict:
        """Read and process output.txt file"""
        try:
            if not os.path.exists(self.output_file):
                print(f"❌ {self.output_file} not found")
                return {}

            with open(self.output_file, 'r') as f:
                content = f.read()

            if content.strip().startswith('{'):
                data = json.loads(content)
            else:
                data = self._parse_text_output(content)

            dashboard_data = self._structure_for_dashboard(data)
            return dashboard_data

        except Exception as e:
            print(f"❌ Error processing output.txt: {e}")
            return {}

    def _parse_text_output(self, content: str) -> Dict:
        """Parse text-format output into structured data"""
        data = {
            "person_name": "",
            "company": "",
            "title": "",
            "overview": "",
            "background": "",
            "pain_points": [],
            "talking_points": [],
            "trigger_events": [],
            "myers_briggs": "",
            "recent_deals": []
        }

        lines = content.split('\n')
        current_section = None

        for line in lines:
            line = line.strip()

            if 'Overview' in line:
                current_section = 'overview'
            elif 'Background' in line:
                current_section = 'background'
            elif 'Pain Points' in line:
                current_section = 'pain_points'
            elif 'Talking Points' in line:
                current_section = 'talking_points'
            elif line and current_section:
                if current_section in ['pain_points', 'talking_points']:
                    if line.startswith('•') or line.startswith('-'):
                        data[current_section].append(line.strip('•- '))
                else:
                    data[current_section] = line

        return data

    def _structure_for_dashboard(self, data: Dict) -> Dict:
        """Structure data for dashboard display"""
        return {
            "contact_info": {
                "name": data.get("person_name", "Unknown"),
                "title": data.get("current_title", data.get("title", "")),
                "company": data.get("company", ""),
                "email": data.get("email", ""),
                "phone": data.get("phone", ""),
                "linkedin": data.get("linkedin_url", "")
            },
            "intelligence": {
                "overview": data.get("overview", ""),
                "background": data.get("background", ""),
                "education": data.get("education", ""),
                "myers_briggs": data.get("myers_briggs", ""),
                "recent_activity": data.get("recent_activity", [])
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
            "generated_scripts": {
                "email": None,
                "call_script": None,
                "linkedin": None
            },
            "metadata": {
                "last_enriched": datetime.now().isoformat(),
                "data_quality": self._assess_quality(data),
                "completeness": self._calculate_completeness(data)
            }
        }

    def _assess_quality(self, data: Dict) -> str:
        """Assess data quality"""
        filled_fields = sum(1 for v in data.values() if v)
        total_fields = len(data)
        ratio = filled_fields / total_fields if total_fields > 0 else 0

        if ratio > 0.8:
            return "excellent"
        elif ratio > 0.6:
            return "good"
        elif ratio > 0.4:
            return "moderate"
        else:
            return "limited"

    def _calculate_completeness(self, data: Dict) -> float:
        """Calculate completeness percentage"""
        filled = sum(1 for v in data.values() if v)
        total = len(data)
        return round((filled / total) * 100, 1) if total > 0 else 0


def generate_all_scripts(dashboard_data: Dict) -> Dict:
    """Generate all communication scripts"""
    from intelligence.outreach.apex_script_orchestrator import ScriptOrchestrator

    orchestrator = ScriptOrchestrator()

    enriched_data = {
        "person_name": dashboard_data["contact_info"]["name"],
        "current_title": dashboard_data["contact_info"]["title"],
        "company": dashboard_data["contact_info"]["company"],
        "pain_points": dashboard_data["engagement"]["pain_points"],
        "recent_deals": dashboard_data["engagement"]["recent_deals"],
        "myers_briggs": dashboard_data["intelligence"]["myers_briggs"]
    }

    vertical = detect_vertical(enriched_data)
    scripts = orchestrator.route_for_generation(enriched_data, vertical)

    return scripts.get("communications", {})


def detect_vertical(data: Dict) -> str:
    """Detect the appropriate vertical"""
    title = data.get("current_title", "").lower()
    company = data.get("company", "").lower()

    if 'broker' in title or 'agent' in title:
        return "CRE_BROKER"
    elif 'bank' in company or 'capital' in company:
        return "CRE_LENDER"
    elif 'sba' in title or 'cdc' in company:
        return "SBA_LENDER"
    else:
        return "CRE_BROKER"


class DashboardUpdater:
    """Update dashboard with processed data"""

    def __init__(self):
        self.dashboard_file = "dashboard_data.json"

    def update_contact(self, contact_id: int, dashboard_data: Dict) -> bool:
        """Update a contact in the dashboard"""
        try:
            if os.path.exists(self.dashboard_file):
                with open(self.dashboard_file, 'r') as f:
                    all_data = json.load(f)
            else:
                all_data = {}

            all_data[str(contact_id)] = dashboard_data

            with open(self.dashboard_file, 'w') as f:
                json.dump(all_data, f, indent=2)

            print(f"✅ Dashboard updated for contact {contact_id}")
            return True

        except Exception as e:
            print(f"❌ Error updating dashboard: {e}")
            return False

    def get_contact(self, contact_id: int) -> Optional[Dict]:
        """Get contact data from dashboard"""
        try:
            if os.path.exists(self.dashboard_file):
                with open(self.dashboard_file, 'r') as f:
                    all_data = json.load(f)
                return all_data.get(str(contact_id))
            return None
        except:
            return None


def run_complete_pipeline(contact_id: int) -> Dict:
    """Run the complete data processing pipeline"""

    print(f"🚀 Starting Pipeline for Contact {contact_id}")
    print("=" * 60)

    # Process enrichment output
    print("📄 Processing enrichment output...")
    processor = EnrichmentProcessor()
    dashboard_data = processor.process_output_file()

    if not dashboard_data:
        return {"status": "error", "message": "No enrichment data found"}

    print(f"   ✓ Processed: {dashboard_data['contact_info']['name']}")
    print(f"   ✓ Company: {dashboard_data['contact_info']['company']}")
    print(f"   ✓ Data Quality: {dashboard_data['metadata']['data_quality']}")
    print(f"   ✓ Completeness: {dashboard_data['metadata']['completeness']}%")

    # Generate scripts
    print("\n✍️ Generating communication scripts...")
    try:
        scripts = generate_all_scripts(dashboard_data)
        dashboard_data["generated_scripts"] = scripts
        print(f"   ✓ Scripts generated successfully")
    except Exception as e:
        print(f"   ⚠️ Script generation failed: {e}")

    # Update dashboard
    print("\n📊 Updating dashboard...")
    updater = DashboardUpdater()
    success = updater.update_contact(contact_id, dashboard_data)

    if success:
        print("\n✅ Pipeline Complete!")
        return {
            "status": "success",
            "contact_id": contact_id,
            "contact_name": dashboard_data['contact_info']['name'],
            "data_quality": dashboard_data['metadata']['data_quality'],
            "scripts_generated": bool(dashboard_data.get("generated_scripts"))
        }
    else:
        return {"status": "error", "message": "Failed to update dashboard"}
