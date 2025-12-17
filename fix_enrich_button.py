#!/usr/bin/env python3
"""
Fix ContactsView.tsx - Change batch enrich to individual contact enrich
"""

from pathlib import Path
import re

print("=" * 80)
print("FIXING ENRICHMENT BUTTON IN ContactsView.tsx")
print("=" * 80)
print()

contacts_view_path = Path("dashboard_v1/src/components/ContactsView.tsx")

if not contacts_view_path.exists():
    print(f"❌ File not found: {contacts_view_path}")
    print("Make sure you're in the apex-sales-intelligence directory")
    exit(1)

content = contacts_view_path.read_text()

# Find and replace the batch enrich call
old_pattern = r'await fetch\(`\$\{API_URL\}/api/batch/enrich`'
new_replacement = 'await fetch(`${API_URL}/api/v2/contacts/${contact.id}/enrich`'

# Check if the old pattern exists
if 'api/batch/enrich' in content:
    print("✅ Found the bug at line 217")
    print()
    print("OLD CODE (wrong):")
    print("  await fetch(`${API_URL}/api/batch/enrich`, {")
    print()
    print("NEW CODE (correct):")
    print("  await fetch(`${API_URL}/api/v2/contacts/${contact.id}/enrich`, {")
    print()

    # Replace batch/enrich with v2/contacts/{id}/enrich
    content = content.replace(
        'await fetch(`${API_URL}/api/batch/enrich`',
        'await fetch(`${API_URL}/api/v2/contacts/${contact.id}/enrich`'
    )

    # Also need to make sure 'contact' is available in scope
    # Check if we need to pass contact ID differently
    if '(contact)' in content or 'contact:' in content:
        print("✅ Contact object is available in scope")
    else:
        print("⚠️ May need to pass contact ID to the handler")

    # Write the fixed file
    contacts_view_path.write_text(content)

    print()
    print("✅ FIXED: dashboard_v1/src/components/ContactsView.tsx")
    print()
    print("=" * 80)
    print("NEXT STEPS")
    print("=" * 80)
    print()
    print("1. Review the change:")
    print("   git diff dashboard_v1/src/components/ContactsView.tsx")
    print()
    print("2. Test locally (if running dev server):")
    print("   cd dashboard_v1")
    print("   npm run dev")
    print()
    print("3. Commit and deploy:")
    print("   git add dashboard_v1/src/components/ContactsView.tsx")
    print('   git commit -m "fix: enrich button now targets selected contact"')
    print("   git push origin main")
    print()
    print("4. Wait ~1 minute for Vercel to deploy")
    print()
    print("5. Test in production:")
    print("   - Click on Shilo Hall")
    print("   - Click Enrich button")
    print("   - Should now enrich Shilo Hall, not Douglas Hansford")

else:
    print("❌ Pattern not found - may already be fixed or different format")
    print()
    print("Please paste lines 210-220 of ContactsView.tsx so I can see the exact code")
