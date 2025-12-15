#!/usr/bin/env python3

"""
MODIFIED SECTION FOR ENRICHMENT DATA PREP FIX
============================================================
Insert these two functions BEFORE the EnhancedEnrichment class (around line 80)
Then REPLACE the existing enrichment endpoint (around line 1250)
============================================================
"""

# ════════════════════════════════════════════════════════════════════════════
# NEW HELPER FUNCTIONS (Add after imports, before EnhancedEnrichment class)
# ════════════════════════════════════════════════════════════════════════════

def prepare_enrichment_data(contact):
    """
    Extract and clean minimum required fields for enrichment.
    Handles missing/empty fields gracefully.
    
    Returns:
        dict: Cleaned contact data {name, title, company, email, phone, phone_mobile, linkedin_url}
    """
    # Extract core fields
    name = (contact.get('name') or contact.get('firstname', '') + ' ' + contact.get('lastname', '')).strip()
    
    # Clean title: extract just the title, remove company/license info
    raw_title = contact.get('title') or contact.get('job_title') or ''
    title = raw_title.split(' at ')[0].strip() if ' at ' in raw_title else raw_title[:50].strip()
    
    # Company
    company = (contact.get('company') or 'Unknown').strip()
    
    # Email
    email = (contact.get('email') or '').strip()
    
    # Phone: prefer mobile, fallback to main phone
    phone_mobile = (contact.get('phone_mobile') or '').strip()
    phone = (contact.get('phone') or '').strip()
    
    # Use mobile if available, otherwise main phone, otherwise empty
    best_phone = phone_mobile if phone_mobile else phone
    
    # LinkedIn URL (may be empty)
    linkedin_url = (contact.get('linkedin_url') or '').strip()
    
    return {
        'name': name,
        'title': title,
        'company': company,
        'email': email,
        'phone': best_phone,
        'phone_mobile': best_phone,  # Use same as phone if mobile not available
        'linkedin_url': linkedin_url,
        'original_title': raw_title  # Keep for reference
    }


def build_enrichment_prompt(seed_data):
    """
    Build Perplexity search prompt from seed data.
    Constructs research query with all available context.
    
    Args:
        seed_data: dict from prepare_enrichment_data()
        
    Returns:
        str: Formatted Perplexity research prompt
    """
    name = seed_data.get('name', 'Unknown')
    title = seed_data.get('title', 'Unknown')
    company = seed_data.get('company', 'Unknown')
    email = seed_data.get('email', '')
    phone = seed_data.get('phone', '')
    linkedin_url = seed_data.get('linkedin_url', '')
    
    # Build prompt with available contact info
    prompt = f"""Research professional: {name}
Title: {title}
Company: {company}"""
    
    # Add contact info if available
    if email:
        prompt += f"\nEmail: {email}"
    if phone:
        prompt += f"\nPhone: {phone}"
    
    # LinkedIn context
    if linkedin_url:
        prompt += f"\nLinkedIn: {linkedin_url}"
    else:
        prompt += "\nLinkedIn: [searching for LinkedIn profile]"
    
    # Research objectives
    prompt += """

Research Focus:
- Company background, recent news, growth trajectory
- Industry positioning and competitive landscape
- Pain points in their industry/role
- Recent funding, partnerships, or announcements
- Professional background and career progression
- Decision-making authority and influence
- Buying triggers and growth opportunities
- Communication style and personality indicators

Provide specific examples, quotes, and data points where possible."""
    
    return prompt

