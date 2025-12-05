
#!/usr/bin/env python3
"""
Apex API Server - PRODUCTION VERSION
Enhanced Enrichment with Myers-Briggs + DISC
"""

import os
import sys
import json
from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime
import sqlite3
from dotenv import load_dotenv
import requests
import logging
import traceback
from openai import OpenAI

# ============= SETUP =============
load_dotenv('/Users/chrisrabenold/projects/apex/.env')

BACKEND_PATH = '/Users/chrisrabenold/projects/apex/apps/backend'
if BACKEND_PATH not in sys.path:
    sys.path.insert(0, BACKEND_PATH)

GENERATORS_PATH = os.path.join(BACKEND_PATH, 'intelligence/engines/outreach/generators')
if GENERATORS_PATH not in sys.path:
    sys.path.insert(0, GENERATORS_PATH)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# API Keys
HUBSPOT_TOKEN = os.getenv('HUBSPOT_ACCESS_TOKEN') or os.getenv('HUBSPOT_API_KEY')
PERPLEXITY_API_KEY = os.getenv('PERPLEXITY_API_KEY')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

logger.info(f"HubSpot Token: {HUBSPOT_TOKEN[:20] if HUBSPOT_TOKEN else 'NONE'}...")
logger.info(f"Perplexity Key: {'✅ Found' if PERPLEXITY_API_KEY else '❌ Missing'}")
logger.info(f"OpenAI Key: {'✅ Found' if OPENAI_API_KEY else '❌ Missing'}")


# ============= INLINE ENHANCED ENRICHMENT (with Myers-Briggs + DISC) =============
class EnhancedEnrichment:
    """
    Profile Builder - 3-Stage Enrichment Pipeline
    Stage 1: Perplexity Research
    Stage 2: GPT-4 Intelligence Layer (with MBTI + DISC)
    Stage 3: Database Persistence
    """
    
    def __init__(self):
        self.perplexity_key = PERPLEXITY_API_KEY
        self.openai_key = OPENAI_API_KEY
        self.output_dir = '/Users/chrisrabenold/projects/apex/enrichment_profiles'
        
        if not self.perplexity_key or not self.openai_key:
            raise ValueError("Missing Perplexity or OpenAI API keys")
        
        # Create output directory if it doesn't exist
        os.makedirs(self.output_dir, exist_ok=True)
    
    def enrich_contact(self, contact: dict) -> dict:
        """Main enrichment pipeline"""
        name = contact.get('name') or f"{contact.get('firstname', '')} {contact.get('lastname', '')}".strip()
        company = contact.get('company', '')
        
        logger.info("=" * 80)
        logger.info(f"🔍 PROFILE BUILDER: {name} at {company}")
        logger.info("=" * 80)
        
        # STAGE 1: Perplexity Research
        logger.info("📡 STAGE 1: PERPLEXITY RESEARCH")
        query = self.build_profile_builder_query(contact)
        raw_profile = self.call_perplexity(query)
        
        if not raw_profile:
            return {'success': False, 'error': 'Perplexity returned no data'}
        
        logger.info(f"✅ STAGE 1 COMPLETE: {len(raw_profile)} characters")
        
        # STAGE 2: GPT-4 Structuring
        logger.info("🧠 STAGE 2: GPT-4 INTELLIGENCE LAYER")
        polished_profile = self.gpt4_intelligence_layer(raw_profile, contact)
        
        if not polished_profile:
            polished_profile = raw_profile
            logger.warning("⚠️ Stage 2 failed, using raw profile")
        else:
            logger.info(f"✅ STAGE 2 COMPLETE: {len(polished_profile)} characters")
        
        # Save debug file
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{self.output_dir}/profile_{contact.get('id', 'unknown')}_{timestamp}.txt"
            with open(filename, 'w') as f:
                f.write(f"# Profile: {name}\n")
                f.write("=" * 80 + "\n")
                f.write(polished_profile)
            logger.info(f"💾 Saved: {filename}")
        except Exception as e:
            logger.warning(f"Could not save profile file: {e}")
        
        logger.info("=" * 80)
        logger.info("✅ THREE-STAGE ENRICHMENT COMPLETE!")
        logger.info("=" * 80)
        
        return {
            'success': True,
            'profile_text': polished_profile,
            'character_count': len(polished_profile)
        }
    
    def build_profile_builder_query(self, contact: dict) -> str:
        """Build comprehensive research query with Myers-Briggs + DISC"""
        name = contact.get('name') or f"{contact.get('firstname', '')} {contact.get('lastname', '')}".strip()
        title = contact.get('title', '')
        company = contact.get('company', '')
        linkedin_url = contact.get('linkedin_url', '')
        
        context = f"{name}, {title} at {company}"
        if linkedin_url:
            context += f" | LinkedIn: {linkedin_url} (PRIMARY SOURCE)"
        
        query = f"""{context}

Generate a COMPREHENSIVE SALES INTELLIGENCE PROFILE using LinkedIn, news, and public sources.

REQUIRED SECTIONS (use exact markdown headers):

# COMPREHENSIVE SALES INTELLIGENCE PROFILE: {name.upper()}

## EXECUTIVE SUMMARY
2-3 sentence overview of who they are, their role, and why they matter as a prospect.

---

## {name.upper()} - PROFESSIONAL PROFILE

### Overview

**Current Role & Organization**
Describe their current position, company, and scope of responsibility.

**Key Responsibilities & Areas of Focus**
Bullet list of their main responsibilities and focus areas.

**Reporting Structure & Team Dynamics**
Who they likely report to and who reports to them (infer from title if needed).

### Background & Experience

**Career Trajectory**
Previous roles with dates and companies. Show progression.

**Core Competencies & Specializations**
Key skills and areas of expertise.

**Professional Positioning**
How they position themselves professionally.

### Education & Credentials

**Formal Education**
Degrees, institutions, graduation years.

**Professional Certifications & Credentials**
Any certifications, licenses, or professional credentials.

**Ongoing Professional Development**
Conferences, courses, continued learning.

### Professional Strengths & Working Style

**Inferred Leadership Approach**
Based on their role and background, how do they likely lead?

**Communication Style & Client Engagement**
How do they communicate? Formal/informal? Data-driven/relationship-focused?

**Decision-Making Patterns**
Fast/slow? Collaborative/autonomous? Risk-taking/conservative?

**Core Values & Professional Motivations**
What drives them professionally?

### Personality Assessment

**Myers-Briggs Type Indicator (MBTI)**
- **Inferred Type**: [e.g., ENTJ, ISFP, INTJ, etc.]
- **Confidence Level**: [High/Medium/Low] based on available data
- **Evidence**: What behaviors/content/role suggest this type?
- **Key Traits**:
  - Trait 1 and how it manifests
  - Trait 2 and how it manifests
  - Trait 3 and how it manifests
- **Work Style Implications**: How this personality type shows up at work
- **Best Communication Approach**: How to communicate with this MBTI type

**DISC Profile Assessment**
- **Primary Style**: [D - Dominance / I - Influence / S - Steadiness / C - Conscientiousness]
- **Secondary Style**: [D/I/S/C if apparent]
- **Percentage Estimate**: [e.g., D: 40%, I: 30%, S: 20%, C: 10%]
- **Behavioral Indicators**: What suggests this DISC profile?
- **Communication Preferences**: 
  - Do: [What TO do when communicating]
  - Don't: [What NOT to do]
- **Decision-Making Style**: How they make decisions based on DISC
- **Motivators**: What motivates this DISC type
- **Stressors**: What stresses this DISC type

### Social Presence & Professional Engagement

**Digital Footprint & Online Presence**
Where they are active online.

**LinkedIn Activity & Thought Leadership**
- Activity level (high/medium/low)
- Content themes they engage with or share
- Connection count if visible

**Twitter/X Presence**
Handle and main topics (or "Not publicly available").

**Speaking Engagements & Industry Participation**
Conferences, podcasts, webinars, panels.

**Media Presence & Published Content**
Articles, interviews, quotes in publications.

---

## {company.upper()} - COMPANY INTELLIGENCE

### Business Model & Market Position

**Service Delivery Model**
How they deliver value to customers.

**Value Proposition**
What makes them different/valuable.

### Products & Services

**Core Offerings**
Main products or services with brief descriptions.

**Target Markets & Customer Segments**
Who they sell to.

**Pricing & Go-to-Market Strategy**
How they price and sell (if known).

### Market Position & Competitive Landscape

**Industry Category**
What industry/category they operate in.

**Market Size & Opportunity**
Size of their addressable market.

**Competitive Landscape**
Key competitors and positioning.

**Competitive Advantages & Differentiation**
What makes them win.

**Market Share & Growth Trajectory**
Growth trends if available.

### Leadership & Organizational Structure

**Leadership Profile**
CEO and key executives.

**Organizational Support Structure**
Company size, key departments.

**Company Culture & Values**
Culture, values, work environment.

### Recent Activity & Strategic Initiatives

**Current Market Activity**
Recent news and developments (with dates).

**Strategic Initiatives**
Major projects or initiatives.

**Professional Recognition & Industry Standing**
Awards, rankings, recognition.

---

## SALES OPPORTUNITY ANALYSIS

### Trigger Events & Urgency Factors

**Current Conditions Creating Opportunity**
What's happening NOW that creates urgency?

**Regulatory & Market Changes**
Industry changes affecting them.

**Technology & Process Evolution**
Digital transformation, new tools, process changes.

**Seasonal & Cyclical Factors**
Timing considerations.

### Pain Points & Business Challenges

**Role-Specific Pain Points for {title}**
5 specific pain points someone in their exact role faces:
- **Pain Point 1**: [Specific challenge with context]
- **Pain Point 2**: [Specific challenge with context]
- **Pain Point 3**: [Specific challenge with context]
- **Pain Point 4**: [Specific challenge with context]
- **Pain Point 5**: [Specific challenge with context]

**Industry-Specific Challenges**
Challenges specific to their industry.

### Engagement Strategy

**Top 5 Reasons to Engage Now**
1. [Compelling reason with context]
2. [Compelling reason with context]
3. [Compelling reason with context]
4. [Compelling reason with context]
5. [Compelling reason with context]

**Recommended Opening Line**
A personalized, specific first sentence for outreach that references something real about them.

**Recommended Talking Points**
- Talking point 1
- Talking point 2
- Talking point 3

**Topics to Avoid**
Any sensitive areas to steer clear of.

### Key Insights (Non-Obvious Intelligence)

3 strategic insights that aren't immediately obvious:
- **Insight 1**: [Deep observation with implications]
- **Insight 2**: [Deep observation with implications]
- **Insight 3**: [Deep observation with implications]

---

## STRATEGIC SUMMARY

One comprehensive paragraph summarizing: Who they are, what matters to them, their personality style, the best approach to engage them, and why now is the right time.

---

Be thorough. Cite sources with [1], [2], etc. Include specific dates and numbers. If data is unavailable, state "Not publicly available" rather than guessing.
"""
        return query.strip()
    
    def call_perplexity(self, query: str) -> str:
        """Stage 1: Call Perplexity API"""
        url = "https://api.perplexity.ai/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.perplexity_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "sonar-pro",
            "messages": [{"role": "user", "content": query}],
            "temperature": 0.2,
            "max_tokens": 4000
        }
        
        try:
            logger.info("📡 Calling Perplexity API...")
            response = requests.post(url, json=payload, headers=headers, timeout=90)
            
            if response.status_code == 200:
                data = response.json()
                logger.info("✅ Perplexity API successful")
                return data['choices'][0]['message']['content']
            else:
                logger.error(f"❌ Perplexity error: {response.status_code}")
                logger.error(response.text)
                return None
        except Exception as e:
            logger.error(f"❌ Perplexity request error: {e}")
            return None
    
    def gpt4_intelligence_layer(self, raw_profile: str, contact: dict) -> str:
      """Stage 2: GPT-4 structures into rich tabbed format"""
      name = contact.get('name') or f"{contact.get('firstname', '')} {contact.get('lastname', '')}".strip()
      title = contact.get('title', '')
      company = contact.get('company', '')
      
      prompt = f"""You are an elite sales intelligence analyst. Transform this research into a comprehensive, professionally formatted dossier.
    
    CONTACT: {name}, {title} at {company}
    
    RAW RESEARCH:
    {raw_profile}
    
    OUTPUT THIS EXACT STRUCTURE WITH RICH FORMATTING:
    
    # 1. OVERVIEW
    
    ## 1.1 Executive Summary
    [2-3 sentence summary of who they are and why they matter as a prospect]
    
    ## 1.2 Contact Snapshot
    
    | Field | Details |
    |-------|---------|
    | **Name** | {name} |
    | **Title** | {title} |
    | **Company** | {company} |
    | **Experience** | [Years in industry] |
    | **Location** | [City, State] |
    | **Specializations** | [Key areas of expertise] |
    
    ## 1.3 Career Highlights
    - **[Year-Present]:** [Current role] at [Company] - [Key achievement]
    - **[Year-Year]:** [Previous role] at [Company] - [Key achievement]
    - **[Year-Year]:** [Earlier role] at [Company] - [Key achievement]
    
    ## 1.4 Education & Credentials
    | Credential | Institution | Year |
    |------------|-------------|------|
    | [Degree/Cert] | [School] | [Year] |
    
    ---
    
    # 2. PROFESSIONAL STYLE
    
    ## 2.1 Myers-Briggs Assessment
    
    | Dimension | Type | Evidence |
    |-----------|------|----------|
    | **Energy** | [E/I] | [Why] |
    | **Information** | [S/N] | [Why] |
    | **Decisions** | [T/F] | [Why] |
    | **Structure** | [J/P] | [Why] |
    
    **Inferred Type:** [XXXX] | **Confidence:** [High/Medium/Low]
    
    **Work Style:** [2-3 sentences on how this manifests professionally]
    
    ## 2.2 DISC Profile
    
    | Style | Score | Behavioral Indicators |
    |-------|-------|----------------------|
    | **D** - Dominance | [X]% | [How this shows up] |
    | **I** - Influence | [X]% | [How this shows up] |
    | **S** - Steadiness | [X]% | [How this shows up] |
    | **C** - Conscientiousness | [X]% | [How this shows up] |
    
    **Primary Style:** [D/I/S/C] | **Secondary:** [D/I/S/C]
    
    ## 2.3 Communication Playbook
    
    ### ✅ DO THIS
    - [Specific approach that works]
    - [Specific approach that works]
    - [Specific approach that works]
    
    ### ❌ DON'T DO THIS
    - [What to avoid]
    - [What to avoid]
    - [What to avoid]
    
    ---
    
    # 3. COMPANY INTELLIGENCE
    
    ## 3.1 Company Overview
    
    | Attribute | Details |
    |-----------|---------|
    | **Company** | {company} |
    | **Industry** | [Industry sector] |
    | **Founded** | [Year] |
    | **Headquarters** | [Location] |
    | **Employees** | [Size range] |
    | **Revenue** | [If available] |
    | **Business Model** | [Brief description] |
    
    ## 3.2 Products & Services
    
    | Offering | Description | Target Market |
    |----------|-------------|---------------|
    | [Product 1] | [Description] | [Who buys] |
    | [Product 2] | [Description] | [Who buys] |
    | [Product 3] | [Description] | [Who buys] |
    
    ## 3.3 Market Position
    - **Competitive Advantages:** [What makes them win]
    - **Key Competitors:** [Competitor 1], [Competitor 2], [Competitor 3]
    - **Market Share:** [Position in market]
    
    ## 3.4 Recent Developments
    
    | Date | Development |
    |------|-------------|
    | [Date] | [News item] |
    | [Date] | [News item] |
    
    ---
    
    # 4. PAIN POINTS
    
    ## 4.1 Role-Specific Challenges
    
    ### 🎯 Challenge 1: [Title]
    **Problem:** [2-3 sentences on this challenge for {title}]
    **Impact:** [Business impact]
    
    ### 🎯 Challenge 2: [Title]
    **Problem:** [2-3 sentences]
    **Impact:** [Business impact]
    
    ### 🎯 Challenge 3: [Title]
    **Problem:** [2-3 sentences]
    **Impact:** [Business impact]
    
    ### 🎯 Challenge 4: [Title]
    **Problem:** [2-3 sentences]
    **Impact:** [Business impact]
    
    ### 🎯 Challenge 5: [Title]
    **Problem:** [2-3 sentences]
    **Impact:** [Business impact]
    
    ## 4.2 Industry Pressures
    - [Industry challenge 1]
    - [Industry challenge 2]
    - [Industry challenge 3]
    
    ---
    
    # 5. SALES INTEL
    
    ## 5.1 Why NOW?
    [2-3 sentences on timing and urgency]
    
    ## 5.2 Opportunity Assessment
    
    | Factor | Rating | Evidence |
    |--------|--------|----------|
    | **Authority** | 🟢/🟡/🔴 | [Why] |
    | **Need** | 🟢/🟡/🔴 | [Why] |
    | **Timing** | 🟢/🟡/🔴 | [Why] |
    | **Budget** | 🟢/🟡/🔴 | [Why] |
    
    ## 5.3 Strategic Insights
    - 💡 **Insight 1:** [Non-obvious observation]
    - 💡 **Insight 2:** [Non-obvious observation]
    - 💡 **Insight 3:** [Non-obvious observation]
    
    ---
    
    # 6. OUTREACH
    
    ## 6.1 Recommended Opening
    > "[Personalized opening line referencing something specific about them]"
    
    ## 6.2 Talking Points
    
    | Topic | What to Say | Why It Resonates |
    |-------|-------------|------------------|
    | [Topic 1] | [Message] | [Connection to their situation] |
    | [Topic 2] | [Message] | [Connection to their situation] |
    | [Topic 3] | [Message] | [Connection to their situation] |
    
    ## 6.3 Topics to Avoid
    - ⚠️ [Sensitive topic]
    - ⚠️ [Sensitive topic]
    
    ## 6.4 Engagement Strategy
    [3-4 sentences on best channel, timing, and approach based on their personality]
    
    ---
    
    **RULES:**
    - Use EXACT numbered headers (# 1., ## 1.1, etc.)
    - Use markdown tables where shown
    - Be SPECIFIC - no generic content
    - Include {company} details in Section 3
    """
      
      try:
        client = OpenAI(api_key=self.openai_key)
        response = client.chat.completions.create(
          model="gpt-4-turbo",
          messages=[
            {"role": "system", "content": "You are an elite sales intelligence analyst. Output beautifully formatted markdown with tables, clear sections, and actionable insights."},
            {"role": "user", "content": prompt}
          ],
          temperature=0.3,
          max_tokens=4000
        )
        return response.choices[0].message.content
      except Exception as e:
        logger.error(f"❌ GPT-4 error: {e}")
        return None
      

# Mark enrichment as available since we have inline class
ENRICHMENT_AVAILABLE = True
logger.info("✅ Inline EnhancedEnrichment loaded (with MBTI + DISC)")


# ============= TRY TO IMPORT SCORING =============
SCORING_AVAILABLE = False
try:
    from intelligence.engines.scoring.apex_intelligence_engine import ApexScoringEngine
    from intelligence.engines.scoring.scoring_wrapper import (
        score_contact_from_db,
        bulk_score_contacts,
        get_apex_scores
    )
    SCORING_AVAILABLE = True
    logger.info("✅ Scoring engines loaded")
except ImportError as e:
    logger.error(f"❌ Scoring engines not available: {e}")
    logger.warning("⚠️ Using fallback scoring")

    # Fallback scoring functions
    def score_contact_from_db(conn, contact_id, trigger='manual'):
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM contacts WHERE id = ?', (contact_id,))
        row = cursor.fetchone()
        if not row:
            return {'error': 'Contact not found'}

        columns = [desc[0] for desc in cursor.description]
        contact = dict(zip(columns, row))

        score = 50
        if contact.get('email'): score += 10
        if contact.get('phone'): score += 10
        if contact.get('company'): score += 10
        if contact.get('title'): score += 10
        if contact.get('linkedin_url'): score += 10

        tier = 'HOT' if score >= 80 else 'WARM' if score >= 70 else 'QUALIFIED'
        urgency = 'IMMEDIATE' if score >= 80 else 'HIGH' if score >= 70 else 'MEDIUM'

        cursor.execute('''
            UPDATE contacts 
            SET mdcp_score = ?, mdcp_tier = ?,
                rss_score = ?, rss_tier = ?,
                priority_score = ?, urgency_level = ?,
                recommended_action = ?,
                calculation_version = 'fallback_v1',
                last_scored = ?
            WHERE id = ?
        ''', (score, tier, score, tier, score, urgency,
              f'{urgency} priority contact',
              datetime.now().isoformat(), contact_id))
        conn.commit()

        return {
            'success': True,
            'contact_id': contact_id,
            'scores': {
                'mdcp_score': score,
                'mdcp_tier': tier,
                'rss_score': score,
                'rss_tier': tier,
                'priority_score': score,
                'urgency_level': urgency
            }
        }

    def bulk_score_contacts(conn, contact_ids, trigger='batch'):
        results = []
        for cid in contact_ids:
            try:
                result = score_contact_from_db(conn, cid, trigger)
                results.append(result)
            except Exception as e:
                results.append({'contact_id': cid, 'error': str(e)})
        return results

    def get_apex_scores(conn):
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, name, company, email, lead_type, lifecycle_stage,
                   mdcp_score as mdcp_total, mdcp_tier,
                   rss_score as rss_total, rss_tier,
                   priority_score, urgency_level,
                   recommended_action, last_scored
            FROM contacts
            WHERE mdcp_score IS NOT NULL
            ORDER BY priority_score DESC
        ''')
        columns = [desc[0] for desc in cursor.description]
        contacts = [dict(zip(columns, row)) for row in cursor.fetchall()]
        return {
            'status': 'success',
            'count': len(contacts),
            'contacts': contacts
        }


# ============= TRY TO IMPORT CADENCE ENGINES =============
try:
    from intelligence.engines.outreach.auto_sequence_engine import AutoSequenceEngine
    from intelligence.engines.scoring.cadence_router import CadenceRouter
    logger.info("✅ Cadence engines loaded")
except ImportError as e:
    logger.warning(f"⚠️ Cadence engines not available: {e}")
    AutoSequenceEngine = None
    CadenceRouter = None


# Initialize Flask
app = Flask(__name__)
CORS(app)

# Configuration
DATABASE = '/Users/chrisrabenold/projects/apex/apex.db'
PORT = 8000


# ============= DATABASE HELPERS =============
def get_db():
    """Get database connection"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def ensure_scoring_columns():
    """Ensure all scoring columns exist"""
    conn = get_db()
    cursor = conn.cursor()

    columns_to_add = [
        ('mdcp_score', 'REAL'),
        ('mdcp_tier', 'TEXT'),
        ('rss_score', 'REAL'),
        ('rss_tier', 'TEXT'),
        ('priority_score', 'REAL'),
        ('urgency_level', 'TEXT'),
        ('recommended_action', 'TEXT'),
        ('calculation_version', 'TEXT'),
        ('last_scored', 'TEXT'),
        ('lead_type', 'TEXT')
    ]

    for col_name, col_type in columns_to_add:
        try:
            cursor.execute(f'ALTER TABLE contacts ADD COLUMN {col_name} {col_type}')
            logger.info(f"✅ Added column: {col_name}")
        except sqlite3.OperationalError:
            pass

    conn.commit()
    conn.close()
    logger.info("✅ Database schema checked")

def ensure_user_preferences_table():
    """Ensure user_preferences table exists for Why Me? functionality"""
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_preferences (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT UNIQUE NOT NULL DEFAULT 'default_user',
            products TEXT DEFAULT '[]',
            services TEXT DEFAULT '[]',
            value_propositions TEXT DEFAULT '[]',
            target_customers TEXT DEFAULT '[]',
            personal_differentiators TEXT DEFAULT '[]',
            company_differentiators TEXT DEFAULT '[]',
            scoring_profile TEXT DEFAULT 'DEFAULT',
            custom_ideal_titles TEXT DEFAULT '[]',
            custom_avoid_titles TEXT DEFAULT '[]',
            ideal_company_size_min INTEGER,
            ideal_company_size_max INTEGER,
            ideal_industries TEXT DEFAULT '[]',
            target_seniority_levels TEXT DEFAULT '[]',
            exclude_c_suite BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    cursor.execute('''
        INSERT OR IGNORE INTO user_preferences (user_id) 
        VALUES ('default_user')
    ''')

    conn.commit()
    conn.close()
    logger.info("✅ User preferences table checked")


# Run DB setup
ensure_scoring_columns()
ensure_user_preferences_table()


# ============= API ROUTES =============

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'enrichment_available': ENRICHMENT_AVAILABLE,
        'scoring_available': SCORING_AVAILABLE,
        'features': {
            'myers_briggs': True,
            'disc_profile': True
        }
    })


# ============= CONTACTS ENDPOINTS =============

@app.route('/api/contacts', methods=['GET'])
def get_contacts():
    """Get all contacts with optional filtering and pagination"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        status = request.args.get('status')
        limit = request.args.get('limit', 50, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        # Build query
        query = 'SELECT * FROM contacts'
        count_query = 'SELECT COUNT(*) FROM contacts'
        params = []
        count_params = []
        
        if status:
            query += ' WHERE enrichment_status = ?'
            count_query += ' WHERE enrichment_status = ?'
            params.append(status)
            count_params.append(status)
            
        query += ' ORDER BY created_at DESC LIMIT ? OFFSET ?'
        params.extend([limit, offset])
        
        cursor.execute(query, params)
        contacts = [dict(row) for row in cursor.fetchall()]
        
        # Get total count
        cursor.execute(count_query, count_params)
        total = cursor.fetchone()[0]
        
        conn.close()
        
        return jsonify({
            'contacts': contacts,
            'total': total,
            'page': (offset // limit) + 1,
            'hasMore': offset + limit < total
        })
    
    except Exception as e:
        logger.error(f"❌ Error fetching contacts: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/contacts/<int:contact_id>', methods=['GET'])
def get_contact(contact_id):
    """Get a single contact by ID"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM contacts WHERE id = ?', (contact_id,))
        contact = cursor.fetchone()
        conn.close()

        if contact:
            return jsonify(dict(contact))
        else:
            return jsonify({'error': 'Contact not found'}), 404

    except Exception as e:
        logger.error(f"❌ Error fetching contact: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/contacts/<int:contact_id>', methods=['PATCH'])
def update_contact(contact_id):
    """Update contact fields (e.g., notes)"""
    try:
        data = request.get_json()
        conn = get_db()
        cursor = conn.cursor()

        fields = []
        values = []
        for key, value in data.items():
            if key != 'id':
                fields.append(f"{key} = ?")
                values.append(value)

        if not fields:
            return jsonify({'error': 'No fields to update'}), 400

        values.append(contact_id)
        query = f"UPDATE contacts SET {', '.join(fields)} WHERE id = ?"

        cursor.execute(query, values)
        conn.commit()
        conn.close()

        return jsonify({'success': True})

    except Exception as e:
        logger.error(f"❌ Error updating contact: {e}")
        return jsonify({'error': str(e)}), 500


# ============= ENRICHMENT ENDPOINTS =============

@app.route('/api/contacts/<int:contact_id>/enrich', methods=['POST'])
def enrich_contact(contact_id):
    """Enrich a contact using enhanced enrichment with MBTI + DISC"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM contacts WHERE id = ?", (contact_id,))
        row = cursor.fetchone()

        if not row:
            conn.close()
            return jsonify({"success": False, "error": "Contact not found"}), 404

        contact = dict(row)
        
        # Set status to processing immediately
        cursor.execute("""
            UPDATE contacts 
            SET enrichment_status = 'processing'
            WHERE id = ?
        """, (contact_id,))
        conn.commit()
        conn.close()

        if not ENRICHMENT_AVAILABLE:
            return jsonify({
                "success": False,
                "error": "Enrichment engine not available"
            }), 500

        name = contact.get('name') or f"{contact.get('firstname', '')} {contact.get('lastname', '')}".strip()
        logger.info(f"🔍 Starting enrichment for {name}")

        enricher = EnhancedEnrichment()
        result = enricher.enrich_contact(contact)

        if result and result.get('success'):
            conn = get_db()
            conn.execute("""
                UPDATE contacts SET
                profile_content = ?,
                enriched = 1,
                enriched_at = ?,
                enrichment_status = 'completed'
                WHERE id = ?
            """, (
                result['profile_text'],
                datetime.now().isoformat(),
                contact_id
            ))
            conn.commit()
            conn.close()

            logger.info(f"✅ Enrichment complete for contact {contact_id}")
            return jsonify({
                'success': True,
                'contact_id': contact_id,
                'status': 'completed',
                'profile_length': result['character_count'],
                'features': ['myers_briggs', 'disc_profile', 'pain_points', 'engagement_strategy']
            }), 200
        else:
            # Mark as failed
            conn = get_db()
            conn.execute("""
                UPDATE contacts 
                SET enrichment_status = 'failed'
                WHERE id = ?
            """, (contact_id,))
            conn.commit()
            conn.close()
            
            return jsonify({
                'success': False,
                'status': 'failed',
                'error': result.get('error', 'Enrichment failed')
            }), 500

    except Exception as e:
        logger.error(f"❌ Enrichment error: {e}")
        traceback.print_exc()
        
        # Mark as failed in DB
        try:
            conn = get_db()
            conn.execute("""
                UPDATE contacts 
                SET enrichment_status = 'failed'
                WHERE id = ?
            """, (contact_id,))
            conn.commit()
            conn.close()
        except:
            pass
            
        return jsonify({
            'success': False,
            'status': 'failed',
            'error': str(e)
        }), 500

@app.route('/api/contacts/<int:contact_id>/enrichment-status', methods=['GET'])
def get_enrichment_status(contact_id):
    """Get enrichment status for a contact (for polling)"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, enrichment_status, enriched_at, 
                   mdcp_score, priority_score, profile_content
            FROM contacts 
            WHERE id = ?
        """, (contact_id,))
        row = cursor.fetchone()
        conn.close()

        if not row:
            return jsonify({
                'success': False,
                'error': 'Contact not found'
            }), 404

        contact = dict(row)
        status = contact.get('enrichment_status', 'none')
        
        # Extract "why_now" from profile_content if available
        why_now = None
        profile = contact.get('profile_content')
        if profile and '## Sales Opportunities' in profile:
            try:
                why_section = profile.split('## Sales Opportunities')[1].split('##')[0]
                why_now = why_section.strip()[:200] + '...'
            except:
                pass

        return jsonify({
            'contact_id': contact_id,
            'status': status,
            'last_enriched': contact.get('enriched_at'),
            'mdcp_score': contact.get('mdcp_score'),
            'priority_score': contact.get('priority_score'),
            'why_now': why_now
        }), 200

    except Exception as e:
        logger.error(f"❌ Error getting enrichment status: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/contacts/<int:contact_id>/intelligence', methods=['GET'])
def get_contact_intelligence(contact_id):
    """Get full intelligence data for a contact"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM contacts WHERE id = ?", (contact_id,))
        row = cursor.fetchone()
        conn.close()

        if not row:
            return jsonify({
                'success': False,
                'error': 'Contact not found'
            }), 404

        contact_data = {
            'id': row['id'],
            'name': row['name'],
            'firstname': row['firstname'],
            'lastname': row['lastname'],
            'email': row['email'],
            'company': row['company'],
            'title': row['title'],
            'phone': row['phone'],
            'linkedin_url': row['linkedin_url'],
            'enrichment_status': row['enrichment_status'],
            'mdcp_score': row['mdcp_score'],
            'rss_score': row['rss_score'],
            'priority_score': row['priority_score'],
            'urgency_level': row['urgency_level'],
            'mdcp_tier': row['mdcp_tier'],
            'rss_tier': row['rss_tier']
        }

        enrichment_data = {}
        if row.get('enrichment_data'):
            try:
                enrichment_data = json.loads(row['enrichment_data'])
            except:
                pass

        return jsonify({
            'success': True,
            'contact': contact_data,
            'enrichment_data': enrichment_data
        }), 200

    except Exception as e:
        logger.error(f"Error fetching intelligence: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/contacts/<int:contact_id>/reset-enrichment', methods=['POST'])
def reset_enrichment(contact_id):
    """Reset enrichment status"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE contacts 
            SET enrichment_status = 'pending',
                profile_content = NULL,
                enriched = 0,
                enriched_at = NULL
            WHERE id = ?
        """, (contact_id,))
        conn.commit()
        conn.close()

        return jsonify({'success': True, 'message': 'Enrichment reset - ready for re-enrichment'})

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ============= TODAY'S BOARD ENDPOINT =============
    
@app.route('/api/todays-board', methods=['GET'])
def get_todays_board():
    """Daily prioritized action list - shows ALL contacts"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        now = datetime.now()
        date_str = now.strftime('%B %d, %Y')
        time_str = now.strftime('%I:%M %p')
        
        # Get ALL contacts
        cursor.execute("""
            SELECT id, name, email, phone, company, title,
                   mdcp_score, priority_score, enrichment_status,
                   enriched_at as last_enriched
            FROM contacts
            ORDER BY id DESC
            LIMIT 100
        """)
        
        all_contacts = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        logger.info(f"📊 Found {len(all_contacts)} contacts for Today's Board")
        
        # Organize by tiers
        urgent = []
        warm = []
        hot = []
        qualified = []
        potential = []
        
        for c in all_contacts:
            # Calculate score from data completeness
            score = 50
            if c.get('email'): score += 10
            if c.get('phone'): score += 10
            if c.get('company'): score += 10
            if c.get('title'): score += 10
            
            c['mdcp_score'] = float(score)
            c['priority_score'] = float(score)
            c['enrichment_status'] = c.get('enrichment_status') or 'pending'
            c['why_now'] = f"⚡ Ready to enrich - Data score: {score}"
            
            # Categorize
            if score >= 90:
                c['urgency_tier'] = 'urgent'
                c['urgency_label'] = '🔥 URGENT'
                c['contact_type'] = 'relationship'
                urgent.append(c)
            elif score >= 80:
                c['urgency_tier'] = 'hot_prospect'
                c['urgency_label'] = '🎯 HOT'
                c['contact_type'] = 'prospect'
                hot.append(c)
            elif score >= 70:
                c['urgency_tier'] = 'warm'
                c['urgency_label'] = '⏰ WARM'
                c['contact_type'] = 'relationship'
                warm.append(c)
            elif score >= 60:
                c['urgency_tier'] = 'qualified_prospect'
                c['urgency_label'] = '✅ QUALIFIED'
                c['contact_type'] = 'prospect'
                qualified.append(c)
            else:
                c['urgency_tier'] = 'potential_prospect'
                c['urgency_label'] = '🔍 POTENTIAL'
                c['contact_type'] = 'prospect'
                potential.append(c)
                    
        return jsonify({
            'success': True,
            'date': date_str,
            'time': time_str,
            'total_actions': len(urgent) + len(hot) + len(warm) + len(qualified),
            'recommendation': f"Start enriching {len(urgent)} urgent and {len(hot)} hot contacts",
            'relationships': {
                'total': len(urgent) + len(warm),
                'urgent_count': len(urgent),
                'warm_count': len(warm),
                'nurture_count': 0,
                'stable_count': 0,
                'tiers': {
                    'urgent': urgent,
                    'warm': warm,
                    'nurture': [],
                    'stable': []
                }
            },
            'new_prospects': {
                'total': len(hot) + len(qualified) + len(potential),
                'hot_count': len(hot),
                'qualified_count': len(qualified),
                'potential_count': len(potential),
                'tiers': {
                    'hot': hot,
                    'qualified': qualified,
                    'potential': potential
                }
            }
        })
    
    except Exception as e:
        logger.error(f"Today's Board error: {e}")
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


# ============= STARTUP =============
    
if __name__ == '__main__':
    logger.info("=" * 60)
    logger.info("🚀 APEX API SERVER - PRODUCTION")
    logger.info("=" * 60)
    logger.info(f"📊 Database: {DATABASE}")
    logger.info(f"🔌 Port: {PORT}")
    logger.info(f"🧠 Enrichment: {'✅ Available (MBTI + DISC)' if ENRICHMENT_AVAILABLE else '❌ Unavailable'}")
    logger.info(f"📈 Scoring: {'✅ Available' if SCORING_AVAILABLE else '⚠️ Fallback Mode'}")
    logger.info("=" * 60)
    app.run(host='0.0.0.0', port=PORT, debug=True)

  