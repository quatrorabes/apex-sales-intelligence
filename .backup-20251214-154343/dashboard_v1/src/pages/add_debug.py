import re
from pathlib import Path

file = Path("ContactDetailPage.tsx")
content = file.read_text()

# Find the function start and add console.log
pattern = r"(export function ContactDetailPage.*?\{)"
if match := re.search(pattern, content):
    inject = match.end()
    debug = "\n  console.log('🔍 ContactDetailPage loaded, id:', id);\n"
    content = content[:inject] + debug + content[inject:]
    
    file.write_text(content)
    print("✅ Added debug logging")
else:
    print("❌ Could not find function")
