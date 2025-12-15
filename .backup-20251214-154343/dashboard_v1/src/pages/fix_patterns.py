import re
from pathlib import Path

file = Path("ContactDetailPage.tsx")
content = file.read_text()

old_patterns = '''  const markdownPatterns: Record<string, RegExp[]> = {
    person: [
      /===\\s*PERSON RESEARCH[^=]*===/i,
      /##\\s*.+–\\s*Professional Profile/i,
      /###?\\s*Overview/i,
      /###?\\s*Background/i
    ],
    company: [
      /===\\s*COMPANY RESEARCH[^=]*===/i,
      /##\\s*.+–\\s*Company Intelligence/i,
      /###?\\s*Company Overview/i
    ],
    sales: [
      /===\\s*SALES INTELLIGENCE\\s*===/i,
      /##\\s*Sales Opportunities/i,
      /###?\\s*Trigger Events/i,
      /###?\\s*Pain Points/i
    ],
    personality: [
      /###?\\s*PERSONALITY ANALYSIS/i,
      /###?\\s*Personality\\s*[&]?\\s*Working Style/i,'''

new_patterns = '''  const markdownPatterns: Record<string, RegExp[]> = {
    person: [
      /===\\s*PERSON RESEARCH[^=]*===/i,
      /##\\s*.+–\\s*Professional Profile/i,
      /##\\s*1\\.\\s*Overview/i,
      /##\\s*2\\.\\s*Professional Background/i,
      /###?\\s*Overview/i,
      /###?\\s*Background/i
    ],
    company: [
      /===\\s*COMPANY RESEARCH[^=]*===/i,
      /##\\s*.+–\\s*Company Intelligence/i,
      /##\\s*8\\.\\s*Company Overview/i,
      /##\\s*\\d+\\.\\s*Company/i,
      /###?\\s*Company Overview/i
    ],
    sales: [
      /===\\s*SALES INTELLIGENCE\\s*===/i,
      /##\\s*Sales Opportunities/i,
      /##\\s*\\d+\\.\\s*Pain Points/i,
      /##\\s*\\d+\\.\\s*Trigger/i,
      /###?\\s*Trigger Events/i,
      /###?\\s*Pain Points/i,
      /PAIN.?POINTS/i,
      /OPPORTUNITIES/i
    ],
    personality: [
      /###?\\s*PERSONALITY ANALYSIS/i,
      /##\\s*6\\.\\s*Personality/i,
      /##\\s*7\\.\\s*Myers-Briggs/i,
      /##\\s*\\d+\\.\\s*Personality/i,
      /###?\\s*Personality\\s*[&]?\\s*Working Style/i,'''

content = content.replace(old_patterns, new_patterns)
file.write_text(content)
print("✅ Patterns updated!")
