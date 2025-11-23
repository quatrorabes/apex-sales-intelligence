#!/usr/bin/env python3
"""
COMPREHENSIVE FIX - Addresses all 4 issues
Clean version without syntax errors
"""

import json
import os
from datetime import datetime
from typing import Dict, Optional

# ========================================
# FIX 1: ENHANCED ENRICHMENT WITH LINKEDIN
# ========================================

def enhanced_enrich_contact(contact_id: int, contact: Dict) -> Dict:
    """Enhanced enrichment that includes LinkedIn URL in search"""

    # Extract LinkedIn URL from contact
    linkedin_url = contact.get('linkedin_url', '') or contact.get('linkedin', '')

    # Build enhanced search query
    name = f"{contact.get('firstname', '')} {contact.get('lastname', '')}".strip()
    company = contact.get('company', '')

    # Include LinkedIn in search if available
    if linkedin_url:
        search_query = f"Find information about {name} from {company}. Their LinkedIn profile is {linkedin_url}"
    else:
        search_query = f"Find information about {name} from {company} including their LinkedIn profile"

    # Call enrichment with enhanced query
    from intelligence.enrichment import enrich_contact

    # Pass the LinkedIn info through the contact dict
    if linkedin_url:
        contact['linkedin_context'] = linkedin_url

    result = enrich_contact(contact_id, contact)

    # Verify and flag for missing info
    if not result.get('enrichment_data', {}).get('linkedin_url') and not linkedin_url:
        print(f"⚠️ No LinkedIn found for {name}")
        result['needs_verification'] = {'linkedin': True}

    return result


# ========================================
# FIX 2: ENSURE DASHBOARD TRANSFER
# ========================================

def verified_dashboard_transfer(contact_id: int, enrichment_result: Dict) -> bool:
    """Verified dashboard transfer with error checking"""
    from intelligence.outreach.dashboard_bridge import DashboardBridge

    try:
        bridge = DashboardBridge()

        # Ensure we have data to transfer
        if not enrichment_result.get('enrichment_data'):
            print(f"❌ No enrichment data to transfer for contact {contact_id}")
            return False

        # Transfer to dashboard
        success = bridge.transfer_to_dashboard(contact_id, enrichment_result)

        if success:
            # Verify it actually saved
            saved_data = bridge.get_dashboard_data(contact_id)
            if saved_data:
                print(f"✅ Dashboard verified: {saved_data['contact_info']['name']}")
                return True
            else:
                print(f"❌ Dashboard save failed - data not retrievable")
                return False

        return False

    except Exception as e:
        print(f"❌ Dashboard transfer error: {e}")
        return False


# ========================================
# FIX 3: CONTENT GENERATION WITH CONFIRMATION
# ========================================

def generate_content_with_confirmation(contact_id: int, dashboard_data: Dict) -> Dict:
    """Generate content with user confirmation option"""

    generated_content = {}

    # Check if auto-generate is enabled
    auto_generate = os.getenv('AUTO_GENERATE_CONTENT', 'false').lower() == 'true'

    if auto_generate:
        print(f"🤖 Auto-generating content for contact {contact_id}")
        generated_content = generate_all_content(dashboard_data)
    else:
        # Store pending for user confirmation
        print(f"📝 Content generation pending user confirmation")
        generated_content = {
            'status': 'pending_confirmation',
            'message': 'Click Generate Scripts to create email and call scripts'
        }

    return generated_content


# ========================================
# FIX 4: OPENAI CONTENT GENERATION
# ========================================

def generate_all_content(dashboard_data: Dict) -> Dict:
    """Actually call OpenAI to generate content"""

    try:
        # Import the actual generators
        from intelligence.outreach.email_generator import generate_email_variants
        from intelligence.outreach.call_script_generator_unified import generate_call_scripts

        contact_data = {
            'firstname': dashboard_data['contact_info']['name'].split()[0] if dashboard_data['contact_info']['name'] else '',
            'lastname': dashboard_data['contact_info']['name'].split()[-1] if dashboard_data['contact_info']['name'] else '',
            'company': dashboard_data['contact_info']['company'],
            'jobtitle': dashboard_data['contact_info']['title'],
            'email': dashboard_data['contact_info']['email']
        }

        enrichment_data = {
            'pain_points': dashboard_data['engagement']['pain_points'],
            'talking_points': dashboard_data['engagement']['talking_points'],
            'recent_activity': dashboard_data['intelligence']['recent_activity'],
            'myers_briggs': dashboard_data['intelligence']['myers_briggs']
        }

        # Generate email variants
        print(f"📧 Generating emails via OpenAI...")
        emails = generate_email_variants(contact_data, enrichment_data)

        # Generate call scripts
        print(f"📞 Generating call scripts via OpenAI...")
        scripts = generate_call_scripts(contact_data, enrichment_data)

        return {
            'status': 'generated',
            'emails': emails,
            'call_scripts': scripts,
            'generated_at': datetime.now().isoformat()
        }

    except Exception as e:
        print(f"❌ Content generation error: {e}")
        return {
            'status': 'error',
            'error': str(e)
        }

# File: intelligence/outreach/comprehensive_fix.py
# ADD or MODIFY this function:
    
import os
from intelligence.outreach.apex_script_orchestrator import ScriptOrchestrator

def generate_content_with_confirmation(contact_id: int, dashboard_data: dict) -> dict:
    """Generate content - check AUTO_GENERATE_CONTENT env variable"""
    
    # Check if auto-generation is enabled (default to True for immediate fix)
    auto_generate = os.getenv('AUTO_GENERATE_CONTENT', 'true').lower() == 'true'
    
    if not auto_generate:
        print("📝 Content generation pending user confirmation")
        return {}
    
    # Generate the scripts
    print(f"🚀 Generating scripts for contact {contact_id}")
    
    try:
        orchestrator = ScriptOrchestrator()
        
        # Prepare contact data from dashboard
        contact_data = {
            "name": dashboard_data.get("contact_info", {}).get("name", "Unknown"),
            "company": dashboard_data.get("company_info", {}).get("name", "Unknown Company"),
            "title": dashboard_data.get("contact_info", {}).get("title", ""),
            "industry": dashboard_data.get("company_info", {}).get("industry", ""),
            "pain_points": dashboard_data.get("engagement", {}).get("pain_points", []),
            "talking_points": dashboard_data.get("engagement", {}).get("talking_points", []),
            "recent_activity": dashboard_data.get("intelligence", {}).get("recent_activity", [])
        }
        
        # Generate scripts
        scripts = orchestrator.generate_all_scripts(contact_data)
        
        print(f"✅ Scripts generated successfully for contact {contact_id}")
        return scripts
    
    except Exception as e:
        print(f"❌ Error generating scripts: {e}")
        return {}
    