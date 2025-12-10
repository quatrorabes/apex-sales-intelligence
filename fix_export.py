#!/usr/bin/env python3
"""APEX v2.0 - Fix ContactDetailPage Export"""

import re
from pathlib import Path

CONTACT_DETAIL_PAGE = Path("dashboard_v1/src/pages/ContactDetailPage.tsx")

if not CONTACT_DETAIL_PAGE.exists():
    print(f"❌ File not found: {CONTACT_DETAIL_PAGE}")
    exit(1)

with open(CONTACT_DETAIL_PAGE, 'r', encoding='utf-8') as f:
    content = f.read()

print("Checking exports...")

has_named = "export { ContactDetailPage }" in content or "export const ContactDetailPage" in content
has_default = "export default ContactDetailPage" in content

if not has_named and not has_default:
    print("❌ NO EXPORT - Adding named export")
    content = content.rstrip() + "\n\nexport { ContactDetailPage };\n"
    with open(CONTACT_DETAIL_PAGE, 'w', encoding='utf-8') as f:
        f.write(content)
    print("✅ Fixed!")
elif has_default and not has_named:
    print("⚠️  Has default export, changing to named")
    content = re.sub(r'export default ContactDetailPage[;]?', '', content)
    content = content.rstrip() + "\n\nexport { ContactDetailPage };\n"
    with open(CONTACT_DETAIL_PAGE, 'w', encoding='utf-8') as f:
        f.write(content)
    print("✅ Fixed!")
else:
    print("✓ Export looks good")

print("\nNow run: npm run build")
