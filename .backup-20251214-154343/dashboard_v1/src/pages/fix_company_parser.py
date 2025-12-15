import re
from pathlib import Path

file = Path("ContactDetailPage.tsx")
content = file.read_text()

# Add a new markdown section parser after parseNumberedSections
new_parser = '''
// Parse markdown ## and ### sections (for company intelligence)
function parseMarkdownSections(text: string): ParsedSection[] {
  if (!text) return [];
  
  const sections: ParsedSection[] = [];
  
  // Split on ## headers (level 2)
  const parts = text.split(/(?=^##\s)/m).filter(p => p.trim());
  
  for (const part of parts) {
    const lines = part.split('\\n');
    const headerLine = lines[0] || '';
    
    // Extract title from ## Header or ### Header
    const titleMatch = headerLine.match(/^#{2,3}\s+(.+)/);
    if (!titleMatch) continue;
    
    const title = titleMatch[1].trim();
    const body = lines.slice(1).join('\\n').trim();
    
    // Extract bullet points and content
    const contentItems = body
      .split('\\n')
      .map(l => l.replace(/^[-•*]\s*/, '').replace(/\*\*/g, '').trim())
      .filter(l => l.length > 0 && !l.startsWith('##'));
    
    if (title && contentItems.length > 0) {
      sections.push({ title, content: contentItems });
    }
  }
  
  return sections;
}

'''

# Insert after parseNumberedSections function
# Find the end of parseNumberedSections
insert_point = content.find('function parseStarSections')
if insert_point > 0:
    content = content[:insert_point] + new_parser + content[insert_point:]

# Update companyCards to try both parsers
old_company_parse = 'const companyCards = parseNumberedSections(companySection);'
new_company_parse = '''const companyCards = (() => {
    const numbered = parseNumberedSections(companySection);
    if (numbered.length > 0) return numbered;
    return parseMarkdownSections(companySection);
  })();'''

content = content.replace(old_company_parse, new_company_parse)

file.write_text(content)
print("✅ Added markdown section parser for company data!")
