# 📞 AI CALL SCRIPT GENERATOR v3.0 (FIXED)
# Uses sonar-pro + profile_content

import os, sqlite3, requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("PERPLEXITY_API_KEY")
BASE_URL = "https://api.perplexity.ai/chat/completions"
MODEL = "sonar-pro"
DB_PATH = "sales_angel.db"

def get_conn():
    c = sqlite3.connect(DB_PATH, check_same_thread=False)
    c.row_factory = sqlite3.Row
    return c

def get_profile(cid:int):
    with get_conn() as c:
        r = c.execute("""SELECT firstname, lastname, company, phone, jobtitle,
                         score, tier, profile_content
                         FROM contacts WHERE id=? AND enriched=1""", (cid,)).fetchone()
    return dict(r) if r else None

def gen_script(profile, variant:int):
    name = f"{profile.get('firstname','')} {profile.get('lastname','')}"
    title = profile.get('jobtitle','')
    company = profile.get('company','')
    intel = (profile.get('profile_content') or '')[:1200]
    
    styles = {
        1: "Direct & Value-Focused",
        2: "Consultative & Rapport-Building", 
        3: "Executive / Insight-Led"
    }
    style = styles[variant]
    
    prompt = f"""You are writing a {style} cold-call script for {name}, {title} at {company}.

INTELLIGENCE:
{intel}

GOAL: Book a 15-minute meeting.

Format your response as:

════════════════════════════════════
CALL SCRIPT – {style}
{name} – {title} at {company}
════════════════════════════════════

📞 OPENER:
[Greeting + personal hook using intelligence]

🎯 HOOK / VALUE:
[1-sentence pain point + 1-sentence outcome]

❓ DISCOVERY QUESTIONS:
• [Question 1]
• [Question 2]
• [Question 3]

🛡️ OBJECTION HANDLING:
IF "Not interested": [response]
IF "Send me info": [response]
IF "Too busy": [response]

✅ CLOSE:
[Propose specific times: "How does Tuesday 2 PM or Wednesday 10 AM look?"]

📝 NOTES FOR REP:
• [Key insight 1]
• [Key insight 2]

════════════════════════════════════
"""
    
    payload = {
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 800,
        "temperature": 0.7,
        "top_p": 0.9
    }
    
    r = requests.post(BASE_URL, json=payload,
                     headers={"Authorization": f"Bearer {API_KEY}"},
                     timeout=45)
    r.raise_for_status()
    return r.json()["choices"][0]["message"]["content"].strip()

def save_scripts(cid:int, scripts:dict):
    with get_conn() as c:
        c.execute("""UPDATE contacts SET
                     call_script_1=?, call_script_2=?, call_script_3=?,
                     scripts_generated_at=? WHERE id=?""",
                 (scripts[1], scripts[2], scripts[3],
                  datetime.utcnow().isoformat(), cid))

def generate_all(cid:int):
    p = get_profile(cid)
    if not p:
        print("❌ Contact not enriched")
        return
    
    print(f"\n🎯 Generating call scripts for {p['firstname']} {p['lastname']}...")
    print(f"   {p['jobtitle']} at {p['company']}")
    print(f"   Score: {p['score']} | Tier: {p['tier']}\n")
    
    scripts = {}
    styles = {
        1: "Direct & Value-Focused",
        2: "Consultative & Rapport",
        3: "Executive / Insight-Led"
    }
    
    for v in (1, 2, 3):
        print(f"  Variant {v} ({styles[v]})... ", end="", flush=True)
        try:
            scripts[v] = gen_script(p, v)
            print(f"✅ ({len(scripts[v])} chars)")
        except Exception as e:
            print(f"❌ {e}")
            return
    
    save_scripts(cid, scripts)
    print("\n✅ All scripts generated and saved!\n")
    return scripts

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python call_script_generator.py <contact_id>")
        sys.exit(1)
    
    cid = int(sys.argv[1])
    generate_all(cid)
