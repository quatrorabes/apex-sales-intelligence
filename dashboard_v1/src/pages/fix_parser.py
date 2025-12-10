import re
from pathlib import Path

file = Path("ContactDetailPage.tsx")
content = file.read_text()

# New multi-format extractSection function
new_extract = '''function extractSection(content: string | null, sectionType: string): string {
  if (!content) return '';

  // Detect format: JSON blob vs Markdown
  const trimmed = content.trim();
  if (trimmed.startsWith('{') || trimmed.startsWith('"')) {
    // JSON format - parse and extract
    try {
      const data = JSON.parse(trimmed.startsWith('"') ? trimmed : trimmed);
      const jsonMap: Record<string, string[]> = {
        person: ['EXECUTIVE SUMMARY', 'EXECUTIVE_SUMMARY', 'summary', 'overview'],
        company: ['COMPANY', 'company_overview', 'company'],
        sales: ['PAIN_POINTS', 'PAIN POINTS', 'OPPORTUNITIES', 'BUYING_TRIGGERS', 'pain_points'],
        personality: ['PERSONALITY_ASSESSMENT', 'PERSONALITY', 'personality']
      };
      const keys = jsonMap[sectionType] || [];
      for (const key of keys) {
        if (data[key]) {
          return Array.isArray(data[key]) ? data[key].join('\\n- ') : String(data[key]);
        }
      }
      return '';
    } catch {
      // Not valid JSON, try markdown
    }
  }

  // Markdown format - multiple pattern support
  const markdownPatterns: Record<string, RegExp[]> = {
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
      /###?\\s*Personality\\s*[&]?\\s*Working Style/i,
      /###?\\s*Communication style/i
    ]
  };

  const patterns = markdownPatterns[sectionType] || [];
  
  for (const pattern of patterns) {
    const match = content.match(pattern);
    if (match && match.index !== undefined) {
      const startIdx = match.index;
      const afterMarker = content.substring(startIdx);
      
      // Find next major section (## or === or ---)
      const nextMatch = afterMarker.substring(match[0].length).match(/\\n##\\s|\\n===|\\n---/);
      if (nextMatch && nextMatch.index !== undefined) {
        return afterMarker.substring(0, match[0].length + nextMatch.index).trim();
      }
      return afterMarker.trim();
    }
  }

  return '';
}'''

# Find and replace the old extractSection function
old_pattern = r'function extractSection\(content: string \| null, sectionType: string\): string \{[^}]+\{[^}]+\}[^}]+\{[^}]+\}[^}]+\}'

# Simpler: replace from line 31 to line 62
lines = content.split('\n')
new_lines = []
skip_until = -1

for i, line in enumerate(lines):
    if i == 30:  # Line 31 (0-indexed)
        new_lines.append(new_extract)
        skip_until = 62  # Skip until line 63
    elif i < skip_until:
        continue
    else:
        new_lines.append(line)

content = '\n'.join(new_lines)
file.write_text(content)
print("✅ Parser updated with multi-format support!")
