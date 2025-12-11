import re
from pathlib import Path

file = Path("ContactDetailPage.tsx")
content = file.read_text()

# Add a helper function to clean markdown for display
helper_func = '''
// Clean markdown for raw display
function cleanMarkdownForDisplay(text: string): string {
  return text
    .replace(/^#{1,4}\s*/gm, '')  // Remove # headers
    .replace(/\*\*([^*]+)\*\*/g, '$1')  // Remove bold **text**
    .replace(/^\s*[-•]\s*/gm, '• ')  // Normalize bullets
    .replace(/\n{3,}/g, '\\n\\n')  // Reduce excessive newlines
    .trim();
}

'''

# Insert before parseNumberedSections
insert_point = content.find('function parseNumberedSections')
if insert_point > 0:
    content = content[:insert_point] + helper_func + content[insert_point:]

# Update raw section displays to use the cleaner
old_sales_raw = '''<div className="text-gray-300 whitespace-pre-wrap text-sm">{salesSection}</div>'''
new_sales_raw = '''<div className="text-gray-300 whitespace-pre-wrap text-sm">{cleanMarkdownForDisplay(salesSection)}</div>'''
content = content.replace(old_sales_raw, new_sales_raw)

old_person_raw = '''<div className="text-gray-300 whitespace-pre-wrap text-sm">{personSection}</div>'''
new_person_raw = '''<div className="text-gray-300 whitespace-pre-wrap text-sm">{cleanMarkdownForDisplay(personSection)}</div>'''
content = content.replace(old_person_raw, new_person_raw)

old_company_raw = '''<div className="text-gray-300 whitespace-pre-wrap text-sm">{companySection}</div>'''
new_company_raw = '''<div className="text-gray-300 whitespace-pre-wrap text-sm">{cleanMarkdownForDisplay(companySection)}</div>'''
content = content.replace(old_company_raw, new_company_raw)

file.write_text(content)
print("✅ Added markdown cleaner for raw fallback display!")

# Read again
content = Path("ContactDetailPage.tsx").read_text()

# Add sanity check - if too many small cards, use raw display instead
old_person_cards = '''const personCards = parseStarSections(personSection);'''
new_person_cards = '''const personCards = (() => {
    const cards = parseStarSections(personSection);
    // If too fragmented (>20 cards), fallback to raw
    if (cards.length > 20) return [];
    return cards;
  })();'''

content = content.replace(old_person_cards, new_person_cards)
Path("ContactDetailPage.tsx").write_text(content)
print("✅ Added fragmentation sanity check!")
