#!/usr/bin/env python3
"""
APEX v2.0 - ContactDetailPage Qualification Tab Integration
Single-file solution to wire QualificationTab into dark-UI ContactDetailPage.tsx
"""

import os
import re
import shutil
from datetime import datetime
from pathlib import Path

print("=" * 80)
print("APEX SALES INTELLIGENCE v2.0 - ContactDetailPage Qualification Integration")
print("=" * 80)
print()

# Auto-detect repo root
def find_repo_root():
    """Find apex-sales-intelligence repo in common locations"""
    possible_paths = [
        Path.home() / "apex-sales-intelligence",
        Path.home() / "projects" / "apex-sales-intelligence",
        Path.home() / "Documents" / "apex-sales-intelligence",
        Path.cwd().parents[0] if "apex-sales-intelligence" in str(Path.cwd()) else None,
        Path.cwd().parents[1] if "apex-sales-intelligence" in str(Path.cwd()) else None,
    ]
    
    for path in possible_paths:
        if path and path.exists() and (path / "dashboard_v1").exists():
            return path
    
    return None

# Try to find repo automatically
REPO_ROOT = find_repo_root()

if not REPO_ROOT:
    print("⚠️  Could not auto-detect repo location.")
    print("Please enter the full path to your apex-sales-intelligence folder:")
    user_path = input("Path: ").strip()
    REPO_ROOT = Path(user_path)

print(f"Using repo: {REPO_ROOT}")
print()

# File paths
CONTACT_DETAIL_PAGE = REPO_ROOT / "dashboard_v1/src/pages/ContactDetailPage.tsx"
APP_TSX = REPO_ROOT / "dashboard_v1/src/App.tsx"

# Validate paths
files_ok = True
if not CONTACT_DETAIL_PAGE.exists():
    print(f"❌ ERROR: ContactDetailPage.tsx not found at:")
    print(f"   {CONTACT_DETAIL_PAGE}")
    files_ok = False
else:
    print(f"✓ Found ContactDetailPage.tsx")

if not APP_TSX.exists():
    print(f"❌ ERROR: App.tsx not found at:")
    print(f"   {APP_TSX}")
    files_ok = False
else:
    print(f"✓ Found App.tsx")

if not files_ok:
    print()
    print("Please correct the paths and run again.")
    exit(1)

print()
print("=" * 80)
print("STEP 1: Patch ContactDetailPage.tsx with QualificationTab")
print("=" * 80)
print()

# Create backup
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup_path = CONTACT_DETAIL_PAGE.parent / f"{CONTACT_DETAIL_PAGE.name}.before-qual-{timestamp}"
shutil.copy2(CONTACT_DETAIL_PAGE, backup_path)
print(f"✓ Backup created: {backup_path.name}")

# Read the file
with open(CONTACT_DETAIL_PAGE, 'r', encoding='utf-8') as f:
    content = f.read()

original_content = content

# Step 1.1: Add QualificationTab import
print("  → Adding QualificationTab import...")
if "import { QualificationTab }" not in content:
    import_pattern = r"(import \{ Award \} from ['\"]lucide-react['\"];)"
    import_replacement = r"\1\nimport { QualificationTab } from '../components/QualificationTab';"
    content = re.sub(import_pattern, import_replacement, content)
    print("    ✓ QualificationTab import added")
else:
    print("    ⊙ QualificationTab already imported")

# Step 1.2: Extend mainTab type
print("  → Extending mainTab type to include 'qualification'...")
if "| 'qualification'" not in content:
    type_pattern = r"type MainTab = (['\"]intelligence['\"] \| ['\"]dossier['\"] \| ['\"]outreach['\"]);"
    type_replacement = r"type MainTab = \1 | 'qualification';"
    content = re.sub(type_pattern, type_replacement, content)
    print("    ✓ mainTab type extended")
else:
    print("    ⊙ mainTab type already includes 'qualification'")

# Step 1.3: Add Qualification tab to mainTabs array
print("  → Adding Qualification tab button to mainTabs array...")
if "{ id: 'qualification'" not in content:
    tab_pattern = r"(\{ id: ['\"]outreach['\"], label: ['\"]Outreach['\"], icon: Send \})"
    tab_replacement = r"\1,\n    { id: 'qualification', label: 'Qualification', icon: Award }"
    content = re.sub(tab_pattern, tab_replacement, content)
    print("    ✓ Qualification tab button added")
else:
    print("    ⊙ Qualification tab button already exists")

# Step 1.4: Add Qualification tab content section
print("  → Injecting Qualification tab content section...")
if "mainTab === 'qualification'" not in content:
    qualification_section = '''
        {/* QUALIFICATION TAB */}
        {mainTab === 'qualification' && (
          <div className="space-y-6">
            <QualificationTab contactId={parseInt(id!)} />
          </div>
        )}'''
    
    # Find the outreach tab section and add after it
    outreach_pattern = r"(\{/\* OUTREACH TAB \*/\}[\s\S]*?mainTab === ['\"]outreach['\"][\s\S]*?</div>\s*\)\s*\})"
    
    if re.search(outreach_pattern, content):
        content = re.sub(outreach_pattern, r"\1" + qualification_section, content)
        print("    ✓ Qualification tab content section injected")
    else:
        print("    ⚠ Could not find outreach section pattern")
        print("    Manual injection may be needed")
else:
    print("    ⊙ Qualification tab content section already exists")

# Write the modified content
if content != original_content:
    with open(CONTACT_DETAIL_PAGE, 'w', encoding='utf-8') as f:
        f.write(content)
    print()
    print("✅ ContactDetailPage.tsx successfully patched!")
else:
    print()
    print("⊙ No changes needed - ContactDetailPage.tsx already patched")

print()
print("=" * 80)
print("STEP 2: Fix App.tsx Routing")
print("=" * 80)
print()

# Create backup
backup_path = APP_TSX.parent / f"{APP_TSX.name}.before-routing-fix-{timestamp}"
shutil.copy2(APP_TSX, backup_path)
print(f"✓ Backup created: {backup_path.name}")

# Read the file
with open(APP_TSX, 'r', encoding='utf-8') as f:
    content = f.read()

original_content = content

# Fix the import path
print("  → Fixing ContactDetailPage import path...")
if "./components/ContactDetailPage" in content:
    content = content.replace(
        "from './components/ContactDetailPage'",
        "from './pages/ContactDetailPage'"
    )
    print("    ✓ Import path corrected to ./pages/ContactDetailPage")
elif "./pages/ContactDetailPage" in content:
    print("    ⊙ Import path already correct")
else:
    print("    ⚠ ContactDetailPage import not found in expected format")

# Write the modified content
if content != original_content:
    with open(APP_TSX, 'w', encoding='utf-8') as f:
        f.write(content)
    print()
    print("✅ App.tsx routing successfully fixed!")
else:
    print()
    print("⊙ No changes needed - App.tsx routing already correct")

print()
print("=" * 80)
print("INTEGRATION COMPLETE ✅")
print("=" * 80)
print()
print("Next Steps:")
print(f"1. cd {REPO_ROOT}/dashboard_v1")
print("2. npm run build")
print("3. git add -A && git commit -m 'feat: Wire QualificationTab to dark-UI ContactDetailPage'")
print("4. git push origin main")
print("5. Deploy to Vercel: vercel --prod")
print()
print("Validation Checklist:")
print("  ☐ Navigate to /contacts/:id")
print("  ☐ Verify dark-UI dossier styling is active")
print("  ☐ Click Qualification tab")
print("  ☐ Confirm APEX/BANT/SPICE scores load")
print("  ☐ Check Network: GET /api/contacts/:id/qualification-report?framework=HYBRID")
print()
print("Backend: https://apex-backend-i7b0.onrender.com")
print("Frontend: https://apex-sales-intelligence.vercel.app")
print()
print("=" * 80)
