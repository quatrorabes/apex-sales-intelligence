#!/usr/bin/env python3
"""
Enhanced Full-Output Perplexity Enrichment with GPT-4 Polishing
- Perplexity sonar-pro for research
- GPT-4 for professional polish with user-specific customization
"""
import os
import requests
import json
import sqlite3
from datetime import datetime
from dotenv import load_dotenv
import openai

load_dotenv()

class EnhancedEnrichment:
    """Two-stage enrichment: Research → Polish"""
    
    def __init__(self, api_key=None, openai_key=None, db_path=None):
        self.perplexity_key = api_key or os.getenv("PERPLEXITY_API_KEY")
        self.openai_key = openai_key or os.getenv("OPENAI_API_KEY")
        
        if not self.perplexity_key:
            raise ValueError("PERPLEXITY_API_KEY required")
        if not self.openai_key:
            raise ValueError("OPENAI_API_KEY required for polishing")
        
        self.openai_client = openai.OpenAI(api_key=self.openai_key)
        self.db_path = db_path or os.path.join(os.path.expanduser("~/projects/apex"), "apex.db")
        self.output_dir = "enrichment_profiles"
        os.makedirs(self.output_dir, exist_ok=True)
    
    def get_user_preferences(self, user_id='default_user'):
        """Get user preferences from database"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            
            prefs = conn.execute("""
                SELECT products, services, value_propositions, 
                       target_customers, personal_differentiators, 
                       company_differentiators
                FROM user_preferences 
                WHERE user_id = ?
            """, (user_id,)).fetchone()
            
            conn.close()
            
            if not prefs:
                # Return defaults if no preferences set
                return {
                    'products': ["SBA 504 loans", "SBA 7a loans"],
                    'services': ["Free consultation", "Rate quotes"],
                    'value_propositions': ["10% down vs 30%", "Build equity"],
                    'target_customers': ["Business owners", "Medical practices"],
                    'personal_differentiators': ["20+ years experience"],
                    'company_differentiators': ["Top 10 SBA lender"]
                }
            
            # Parse JSON arrays
            return {
                'products': json.loads(prefs['products'] or '[]'),
                'services': json.loads(prefs['services'] or '[]'),
                'value_propositions': json.loads(prefs['value_propositions'] or '[]'),
                'target_customers': json.loads(prefs['target_customers'] or '[]'),
                'personal_differentiators': json.loads(prefs['personal_differentiators'] or '[]'),
                'company_differentiators': json.loads(prefs['company_differentiators'] or '[]')
            }
            
        except Exception as e:
            print(f"⚠️  Could not load user preferences: {e}")
            return None
    
    def enrich_contact(self, contact):
        """Enrich with enhanced strategic questions and polish"""
        name = contact.get('name', '')
        company = contact.get('company', '')
        title = contact.get('title', '')
        contact_id = contact.get('id', 'unknown')
        
        print("=" * 80)
        print(f"ENHANCED ENRICHMENT: {name} at {company}")
        print("=" * 80)
        
        # Stage 1: Perplexity Research
        query = self.build_enhanced_query(contact)
        print("\n🔍 STAGE 1: PERPLEXITY RESEARCH (sonar-pro)")
        print("-" * 40)
        print(query[:500] + "...truncated for display")
        print("-" * 40)
        
        raw_profile = self.call_perplexity(query)
        
        if not raw_profile:
            print("❌ No result from Perplexity")
            return None
        
        print(f"✅ STAGE 1 COMPLETE: {len(raw_profile)} characters")
        
        # Stage 2: GPT-4 Polishing with User Preferences
        print("\n✨ STAGE 2: GPT-4 POLISHING...")
        print("-" * 40)
        
        user_prefs = self.get_user_preferences()
        polished_profile = self.polish_profile(raw_profile, contact, user_prefs)
        
        if not polished_profile:
            print("⚠️  Polishing failed, using raw profile")
            polished_profile = raw_profile
        else:
            print(f"✅ STAGE 2 COMPLETE: {len(polished_profile)} characters")
        
        # Save both versions
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_filename = f"{self.output_dir}/profile_{contact_id}_{name.replace(' ', '_')}_{timestamp}"
        
        raw_filename = f"{base_filename}_raw.txt"
        self.save_profile(raw_filename, contact, raw_profile, "sonar-pro (raw)")
        
        polished_filename = f"{base_filename}_polished.txt"
        self.save_profile(polished_filename, contact, polished_profile, "sonar-pro + gpt-4 (polished)")
        
        # Save JSON with both
        json_filename = f"{base_filename}.json"
        with open(json_filename, 'w', encoding='utf-8') as f:
            json.dump({
                'contact': contact,
                'raw_profile': raw_profile,
                'polished_profile': polished_profile,
                'generated_at': datetime.now().isoformat(),
                'raw_length': len(raw_profile),
                'polished_length': len(polished_profile),
                'filenames': {
                    'raw': raw_filename,
                    'polished': polished_filename
                }
            }, f, indent=2)
        
        print("=" * 80)
        print("✅ TWO-STAGE ENRICHMENT COMPLETE!")
        print("=" * 80)
        print(f"📄 Raw profile: {raw_filename}")
        print(f"✨ Polished profile: {polished_filename}")
        print(f"📊 JSON data: {json_filename}")
        print(f"📏 Raw size: {len(raw_profile)} characters")
        print(f"📏 Polished size: {len(polished_profile)} characters")
        
        return {
            'success': True,
            'profile_text': polished_profile,
            'raw_profile': raw_profile,
            'filename': polished_filename,
            'character_count': len(polished_profile)
        }
    
    def polish_profile(self, raw_profile, contact, user_prefs):
        """Polish the raw Perplexity output into sales-ready format with user customization"""
        name = contact.get('name', '')
        title = contact.get('title', '')
        company = contact.get('company', '')
        
        # Extract user's offerings
        products = user_prefs.get('products', []) if user_prefs else []
        services = user_prefs.get('services', []) if user_prefs else []
        values = user_prefs.get('value_propositions', []) if user_prefs else []
        personal = user_prefs.get('personal_differentiators', []) if user_prefs else []
        company_edge = user_prefs.get('company_differentiators', []) if user_prefs else []
        
        products_str = ', '.join(products[:3]) if products else "your products"
        services_str = ', '.join(services[:3]) if services else "your services"
        values_str = '; '.join(values[:3]) if values else "your value proposition"
        
        polish_prompt = f"""You are an AI tasked with converting business profile information into a refined, professional dossier for sales reps.

**Data Input:**
Contact: {name}, {title} at {company}

**Sales Rep's Offerings:**
Products: {products_str}
Services: {services_str}
Value Props: {values_str}

**CRITICAL FORMATTING - Use EXACT structure:**

===================================
PROFESSIONAL PROFILE: {name.upper()}
===================================

## 1. Overview – Current Title and Organization
- [Bullet points with - prefix]

## 2. Background – Work History, Notable Achievements
- [Bullet points with - prefix]

## 3. Education – Degrees and Institutions
- [Bullet points with - prefix]

## 4. Recent Mentions – News, Public Appearances, Online Presence
- [Bullet points with - prefix]

## 5. Social Profiles – Online Presence
- [Bullet points with - prefix]

## 6. Personality Detail – Myers-Briggs Assessment
[Paragraph assessment]

## 7. Myers-Briggs Personality Assessment Summary
- [Bullet points with - prefix]

===================================
CORPORATE PROFILE: {company.upper()}
===================================

## 8. Company Overview – Description, Mission, Founding Details, HQ
- [Bullet points with - prefix]

## 8.1. Products & Services – Key Offerings and Markets Served
- [Bullet points with - prefix]

## 8.2. Leadership – Key Executives and Founders
- [Bullet points with - prefix]

## 8.3. Market & Competitors – Industry, Position, Key Competitors
- [Bullet points with - prefix]

## 8.4. Recent News – Major Announcements or Deals
- [Bullet points with - prefix]

## 8.5. Company Fun Facts
- [Bullet points with - prefix]

===================================
STRATEGIC INTELLIGENCE SECTION
===================================

## 9. Pain Points – {title} at {company}
Identify 5 specific pain points for someone in {name}'s role:
- [Pain point 1]
- [Pain point 2]
- [Pain point 3]
- [Pain point 4]
- [Pain point 5]

## 10. Product Fit – How {products_str} Benefits {name}
Explain 5 ways "{products_str}" could benefit {name} or their business, emphasizing:
- {values_str}
- How it solves their pain points from Section 9
- [Benefit 1]
- [Benefit 2]
- [Benefit 3]
- [Benefit 4]
- [Benefit 5]

## 11. Key Insights – Deep, Non-Obvious Intelligence
3 critical insights about {name} or {company} valuable when discussing "{products_str}":
- [Insight 1]
- [Insight 2]
- [Insight 3]

## 12. Final Note – Strategic Summary
[One paragraph synthesizing {name}'s position, needs, how {products_str} helps, and best engagement approach]

===================================

**Instructions:**
- Use EXACT section numbers and titles
- Expand with rich, professional language
- Keep all facts from original
- Make it sales-ready and specific to "{products_str}"
- Section 10 must connect pain points to product benefits

**Raw Profile:**
{raw_profile}

Maintain EXACT structure!"""
        
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {
                        "role": "system", 
                        "content": "You are a professional business profile writer. Follow the exact formatting structure provided."
                    },
                    {
                        "role": "user", 
                        "content": polish_prompt
                    }
                ],
                temperature=0.5,
                max_tokens=4000
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"❌ Polishing error: {e}")
            return None
    
    def build_enhanced_query(self, contact):
        """Build enhanced query - KEEP OPEN ENDED for Perplexity"""
        name = contact.get('name', '')
        title = contact.get('title', '')
        company = contact.get('company', '')
        email = contact.get('email', '')
        phone = contact.get('phone', '')
        linkedin_url = contact.get('linkedin_url', '')
        
        context = f"{name}, {title} at {company}\n"
        context += f"Email: {email}\nPhone: {phone}\n"
        if linkedin_url:
            context += f"Profile: {linkedin_url}\n"
            context += f"Use this LinkedIn profile ({linkedin_url}) as PRIMARY source.\n"
        
        query = f"""{context}

You are a professional profile-building assistant. Generate a comprehensive, up-to-date profile using public web sources and LinkedIn.

For the person ({name}), provide:
1. Overview: Current title and organization
2. Background: Work history, notable achievements  
3. Education: Degrees and institutions
4. Recent Mentions: News, posts, online presence
5. Social Profiles: LinkedIn, Instagram, Facebook, Twitter
6. Personality Detail: Myers-Briggs assessment inferred
7. Myers-Briggs Summary

For the company ({company}), provide:
8. Overview: Description, mission, founding, HQ
8.1. Products & Services
8.2. Leadership
8.3. Market & Competitors
8.4. Recent News
8.5. Company Fun Facts

STRATEGIC INTELLIGENCE:
9. Pain Points: 5 specific pain points for {title}
10. Business Needs: 5 specific business/financial needs
11. Key Insights: 3 non-obvious insights about {name} or {company}
12. Final Note: Strategic summary

Find the correct company where {name} works as {title}."""
        
        return query
    
    def call_perplexity(self, query):
        """Call Perplexity API"""
        url = "https://api.perplexity.ai/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.perplexity_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "sonar-pro",
            "messages": [{"role": "user", "content": query}]
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers)
            if response.status_code == 200:
                return response.json()["choices"][0]["message"]["content"]
            else:
                print(f"❌ API Error: {response.status_code}")
                return None
        except Exception as e:
            print(f"❌ Request error: {e}")
            return None
    
    def save_profile(self, filename, contact, profile_text, model_info):
        """Save profile to file"""
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write("ENHANCED ENRICHMENT PROFILE\n")
            f.write(f"Generated: {datetime.now().isoformat()}\n")
            f.write(f"Model: {model_info}\n")
            f.write("=" * 80 + "\n")
            f.write("CONTACT DETAILS\n")
            f.write(f"Name: {contact.get('name')}\n")
            f.write(f"Title: {contact.get('title')}\n")
            f.write(f"Company: {contact.get('company')}\n")
            f.write(f"Email: {contact.get('email')}\n")
            f.write(f"Phone: {contact.get('phone')}\n")
            f.write("=" * 80 + "\n")
            f.write("PROFILE\n")
            f.write("-" * 80 + "\n")
            f.write(profile_text)
            f.write("\n" + "=" * 80 + "\n")


if __name__ == "__main__":
    # Test
    test_contact = {
        'id': 1,
        'name': 'John Doe',
        'title': 'Vice President',
        'company': 'Sample Company',
        'email': 'john@example.com',
        'phone': '555-1234',
        'linkedin_url': 'https://linkedin.com/in/johndoe'
    }
    
    enricher = EnhancedEnrichment()
    result = enricher.enrich_contact(test_contact)
    
    if result:
        print("\n✅ Test completed successfully!")
