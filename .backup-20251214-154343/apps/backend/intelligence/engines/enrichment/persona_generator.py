"""
=============================================================================
APEX PERSONA GENERATOR - GPT-4o Post-Processing Pipeline
=============================================================================
Location: apps/backend/intelligence/engines/enrichment/persona_generator.py

Transforms raw enrichment data into:
  - PDF Content (dark mode)
  - Executive Brief (one-pager)
  - CRM Summary (Salesforce/HubSpot ready)
  - Persona Sheet (MBTI, DISC, triggers, pain points)

Usage:
    from apps.backend.intelligence.engines.enrichment.persona_generator import process_profile
    result = process_profile(raw_data, contact_name, contact_id)
=============================================================================
"""

from openai import OpenAI
import json
import os
from datetime import datetime
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib import colors
from reportlab.lib.units import inch

# =============================================================================
# CONFIGURATION
# =============================================================================

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)

# Output directory - use data folder for outputs
OUTPUT_DIR = os.path.expanduser("~/projects/apex/data/outputs/personas")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# =============================================================================
# PROMPT TEMPLATE
# =============================================================================

PERSONA_REPORT_PROMPT = """
You are a professional analyst, researcher, and typesetter for a sales intelligence platform called Apex.

Your task is to take the RAW INPUT DATA provided below and generate FOUR deliverables in the exact structured formats described:

=====================================================================
DELIVERABLE 1 — PDF CONTENT (Dark Mode, Ultra-Modern Dashboard Style)

Generate formatted content for a professional sales intelligence report.
Use clear section headers. Include ALL relevant data points.
Sections to include:
- Contact Overview (name, title, company, location, contact info)
- Professional Background (career history, education, achievements)
- Company Intelligence (overview, products, leadership, competitors)
- Personality Profile (MBTI with dimensions, DISC with percentages)
- Communication Playbook (Do's, Don'ts, Best Opening Approach)
- Sales Intelligence (industry trends, pain points, buying triggers)
- Actionable Recommendations (specific outreach strategies)

Style: Clean, hierarchical, scannable. No markdown—use plain text with clear headers.

=====================================================================
DELIVERABLE 2 — EXECUTIVE ONE-PAGE BRIEF

A concise single-page summary for quick review.
Include:
- Who they are (3 sentences max)
- Why they matter (decision-making authority, budget influence)
- Key pain points (top 3)
- Recommended approach (2-3 sentences)
- Best time to engage (budget cycles, triggers)

Tone: Executive-ready, no fluff.

=====================================================================
DELIVERABLE 3 — CRM SUMMARY FORMAT (Salesforce / HubSpot Fields)

Provide in KEY: VALUE format, one per line.
Required fields:
- Full Name
- Title
- Company
- Email
- Phone
- LinkedIn URL
- Location
- Industry
- Company Size
- Estimated Revenue
- MBTI Type
- DISC Primary
- Lead Score (1-100, based on fit and engagement potential)
- Pain Points (comma-separated)
- Buying Triggers (comma-separated)
- Recommended Next Action
- Notes

=====================================================================
DELIVERABLE 4 — SALES OUTREACH PERSONA SHEET

Provide detailed persona analysis:

PERSONALITY ASSESSMENT:
- MBTI Type: [type] (Confidence: [Low/Medium/High])
- DISC Profile: [Primary]/[Secondary] with percentages
- StrengthsFinder (inferred): Top 3 likely strengths

COMMUNICATION STRATEGY:
- Preferred communication style
- Best meeting format (call, video, in-person)
- Optimal message length
- Response time expectations

ENGAGEMENT TACTICS:
- 3 Strong opening lines (personalized to their role/industry)
- Topics that resonate
- Topics to avoid

PAIN POINTS:
- Role-specific challenges (top 3)
- Company-level challenges (top 3)
- Industry-level pressures (top 3)

BUYING SIGNALS & TRIGGERS:
- What would make them take a meeting
- Budget cycle timing
- Decision-making process (solo, committee, champion)

STRATEGIC NOTES:
- Competitive landscape they face
- Recent company news to reference
- Rapport-building topics (hobbies, background, alma mater)

=====================================================================
RAW INPUT DATA:
{{RAW_DATA}}

=====================================================================

Return your final answer using this exact JSON schema:

{
  "pdf_content": "<string with formatted report content>",
  "executive_brief": "<string with one-page summary>",
  "crm_summary": "<string with KEY: VALUE pairs>",
  "persona_sheet": "<string with detailed persona analysis>"
}

Ensure ALL four keys appear. Do NOT include markdown code fencing.
"""

# =============================================================================
# GPT-4o PROCESSING
# =============================================================================

def generate_persona_outputs(raw_data: str, model: str = "gpt-4o") -> dict:
    """
    Send raw enrichment data to GPT-4o for structured output generation.
    """
    prompt = PERSONA_REPORT_PROMPT.replace("{{RAW_DATA}}", raw_data)
    
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a professional sales intelligence analyst. Always return valid JSON."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.3,
            max_tokens=8000
        )
        
        result = json.loads(response.choices[0].message.content)
        
        required_keys = ["pdf_content", "executive_brief", "crm_summary", "persona_sheet"]
        for key in required_keys:
            if key not in result:
                result[key] = f"[{key} generation failed]"
        
        return result
        
    except Exception as e:
        print(f"❌ GPT-4o persona generation error: {e}")
        return {
            "pdf_content": f"Error: {str(e)}",
            "executive_brief": f"Error: {str(e)}",
            "crm_summary": f"Error: {str(e)}",
            "persona_sheet": f"Error: {str(e)}"
        }

# =============================================================================
# PDF GENERATION (Dark Mode)
# =============================================================================

def generate_dark_pdf(text: str, filename: str, contact_name: str = "Contact", landscape_mode: bool = False) -> str:
    """Generate a dark-mode PDF from text content."""
    filepath = os.path.join(OUTPUT_DIR, filename)
    pagesize = landscape(letter) if landscape_mode else letter
    
    doc = SimpleDocTemplate(filepath, pagesize=pagesize,
        leftMargin=0.75*inch, rightMargin=0.75*inch,
        topMargin=0.75*inch, bottomMargin=0.75*inch)
    
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle('DarkTitle', parent=styles['Heading1'],
        fontName='Helvetica-Bold', fontSize=18, leading=22,
        textColor=colors.white, spaceAfter=20)
    
    heading_style = ParagraphStyle('DarkHeading', parent=styles['Heading2'],
        fontName='Helvetica-Bold', fontSize=13, leading=16,
        textColor=colors.HexColor('#60a5fa'), spaceBefore=16, spaceAfter=8)
    
    body_style = ParagraphStyle('DarkBody', parent=styles['Normal'],
        fontName='Helvetica', fontSize=10, leading=14,
        textColor=colors.HexColor('#e5e7eb'), spaceAfter=6)
    
    story = []
    story.append(Paragraph(f"Sales Intelligence Report: {contact_name}", title_style))
    story.append(Paragraph(f"Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}", body_style))
    story.append(Spacer(1, 20))
    
    for line in text.split('\n'):
        line = line.strip()
        if not line:
            story.append(Spacer(1, 8))
        elif line.startswith('===') or line.startswith('---'):
            continue
        elif line.isupper() or (line.endswith(':') and len(line) < 60):
            story.append(Paragraph(line.replace(':', ''), heading_style))
        else:
            safe_line = line.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            story.append(Paragraph(safe_line, body_style))
    
    doc.build(story)
    return filepath

# =============================================================================
# MAIN PIPELINE
# =============================================================================

def process_profile(raw_data: str, contact_name: str = "Contact", contact_id: int = 0) -> dict:
    """
    Full pipeline: GPT processing + PDF generation.
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_name = contact_name.replace(" ", "_").replace(",", "")
    
    print(f"🧠 Processing persona for {contact_name}...")
    
    outputs = generate_persona_outputs(raw_data)
    print(f"✅ GPT-4o outputs generated")
    
    landscape_pdf = generate_dark_pdf(outputs["pdf_content"],
        f"persona_{contact_id}_{safe_name}_{timestamp}_landscape.pdf",
        contact_name, landscape_mode=True)
    
    portrait_pdf = generate_dark_pdf(outputs["pdf_content"],
        f"persona_{contact_id}_{safe_name}_{timestamp}_portrait.pdf",
        contact_name, landscape_mode=False)
    
    print(f"📄 PDFs generated")
    
    # Save text outputs
    brief_path = os.path.join(OUTPUT_DIR, f"brief_{contact_id}_{safe_name}_{timestamp}.txt")
    with open(brief_path, 'w') as f:
        f.write(outputs["executive_brief"])
    
    crm_path = os.path.join(OUTPUT_DIR, f"crm_{contact_id}_{safe_name}_{timestamp}.txt")
    with open(crm_path, 'w') as f:
        f.write(outputs["crm_summary"])
    
    persona_path = os.path.join(OUTPUT_DIR, f"persona_{contact_id}_{safe_name}_{timestamp}.txt")
    with open(persona_path, 'w') as f:
        f.write(outputs["persona_sheet"])
    
    print(f"💾 All outputs saved to {OUTPUT_DIR}")
    
    return {
        "status": "success",
        "contact_name": contact_name,
        "contact_id": contact_id,
        "timestamp": timestamp,
        "files": {
            "pdf_landscape": landscape_pdf,
            "pdf_portrait": portrait_pdf,
            "executive_brief": brief_path,
            "crm_summary": crm_path,
            "persona_sheet": persona_path
        },
        "outputs": {
            "executive_brief": outputs["executive_brief"],
            "crm_summary": outputs["crm_summary"],
            "persona_sheet": outputs["persona_sheet"]
        }
    }

# =============================================================================
# STANDALONE TEST
# =============================================================================

if __name__ == "__main__":
    test_data = "Person Name: Test Contact\nCompany: Test Corp\nRole: CEO"
    result = process_profile(test_data, "Test Contact", 9999)
    print(json.dumps(result, indent=2))
