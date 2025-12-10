#!/usr/bin/env python3

#!/usr/bin/env python3
"""
APEX v2.0 - Wire QualificationTab into Dark-UI ContactDetailPage
Senior Lead Architect: Complete integration script
"""

import os
import re
import shutil
from datetime import datetime
from pathlib import Path

print("=" * 80)
print("APEX SALES INTELLIGENCE v2.0")
print("ContactDetailPage Qualification Tab Integration")
print("=" * 80)
print()

# Get repo path
print("Enter the full path to apex-sales-intelligence:")
print("(Example: /Users/yourname/apex-sales-intelligence)")
print("Or press Enter for default: ~/apex-sales-intelligence")
print()
repo_path = input("Path: ").strip()

if not repo_path:
		repo_path = str(Path.home() / "apex-sales-intelligence")
		print(f"Using default: {repo_path}")
	
REPO_ROOT = Path(repo_path)

if not REPO_ROOT.exists():
		print(f"❌ Repository not found at: {REPO_ROOT}")
		exit(1)
	
print(f"✓ Repository: {REPO_ROOT}")
print()

# Define file paths
PAGES_DIR = REPO_ROOT / "dashboard_v1/src/pages"
CONTACT_DETAIL_PAGE = PAGES_DIR / "ContactDetailPage.tsx"
APP_TSX = REPO_ROOT / "dashboard_v1/src/App.tsx"
QUAL_TAB = REPO_ROOT / "dashboard_v1/src/components/QualificationTab.tsx"

# Validate files exist
print("Validating files...")
if not CONTACT_DETAIL_PAGE.exists():
		print(f"❌ ContactDetailPage.tsx not found!")
		print(f"   Expected: {CONTACT_DETAIL_PAGE}")
		exit(1)
print(f"✓ ContactDetailPage.tsx (dark-UI with parsing)")

if not APP_TSX.exists():
		print(f"❌ App.tsx not found!")
		exit(1)
print(f"✓ App.tsx")

if not QUAL_TAB.exists():
		print(f"⚠️  QualificationTab.tsx not found")
		print(f"   Will patch ContactDetailPage anyway")
else:
		print(f"✓ QualificationTab.tsx")
	
print()
print("=" * 80)
print("STEP 1: Patch ContactDetailPage.tsx")
print("=" * 80)
print()

# Create timestamped backup
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup_file = PAGES_DIR / f"ContactDetailPage.tsx.backup-{timestamp}"
shutil.copy2(CONTACT_DETAIL_PAGE, backup_file)
print(f"✓ Backup: {backup_file.name}")
print()

# Read the file
with open(CONTACT_DETAIL_PAGE, 'r', encoding='utf-8') as f:
		content = f.read()
	
original_content = content
modifications = []

# 1. Add QualificationTab import
print("  [1/4] Adding QualificationTab import...")
if "import { QualificationTab }" not in content:
		# Find Award import and add after it
		pattern = r"(import \{[^}]*Award[^}]*\} from ['\"]lucide-react['\"];)"
		if re.search(pattern, content):
				content = re.sub(pattern, r"\1\nimport { QualificationTab } from '../components/QualificationTab';", content)
				print("        ✓ Import added after Award")
				modifications.append("Import")
		else:
				# Fallback: add after any lucide-react import
				pattern = r"(import \{[^}]+\} from ['\"]lucide-react['\"];)"
				content = re.sub(pattern, r"\1\nimport { QualificationTab } from '../components/QualificationTab';", content, count=1)
				print("        ✓ Import added")
				modifications.append("Import (fallback)")
else:
		print("        ⊙ Already imported")
	
# 2. Extend mainTab type
print("  [2/4] Extending mainTab type...")
if "| 'qualification'" not in content:
		pattern = r"(type MainTab = ['\"]intelligence['\"] \| ['\"]dossier['\"] \| ['\"]outreach['\"])"
		if re.search(pattern, content):
				content = re.sub(pattern, r"\1 | 'qualification'", content)
				print("        ✓ Type extended")
				modifications.append("Type")
		else:
				print("        ⚠ Type pattern not found")
else:
		print("        ⊙ Already extended")
	
# 3. Add Qualification tab button
print("  [3/4] Adding tab button...")
if "{ id: 'qualification'" not in content:
		pattern = r"(\{ id: ['\"]outreach['\"], label: ['\"]Outreach['\"], icon: Send \})"
		if re.search(pattern, content):
				content = re.sub(pattern, r"\1,\n    { id: 'qualification', label: 'Qualification', icon: Award }", content)
				print("        ✓ Button added")
				modifications.append("Button")
		else:
				print("        ⚠ Outreach tab not found")
else:
		print("        ⊙ Already exists")
	
# 4. Add Qualification tab content
print("  [4/4] Adding tab content...")
if not re.search(r"mainTab === ['\"]qualification['\"]", content):
		qual_section = """
				{/* QUALIFICATION TAB */}
				{mainTab === 'qualification' && (
					<div className="space-y-6">
						<QualificationTab contactId={parseInt(id!)} />
					</div>
				)}"""
	
		pattern = r"(\{/\* OUTREACH TAB \*/\}[\s\S]*?mainTab === ['\"]outreach['\"][\s\S]*?</div>\s*\)\s*\})"
		if re.search(pattern, content):
				content = re.sub(pattern, r"\1" + qual_section, content)
				print("        ✓ Content added")
				modifications.append("Content")
		else:
				print("        ⚠ Outreach section not found")
else:
		print("        ⊙ Already exists")
	
# Write changes
if content != original_content:
		with open(CONTACT_DETAIL_PAGE, 'w', encoding='utf-8') as f:
				f.write(content)
		print()
		print(f"✅ ContactDetailPage.tsx patched! ({len(modifications)} changes)")
else:
		print()
		print("⊙ No changes needed")
	
print()
print("=" * 80)
print("STEP 2: Fix App.tsx Routing")
print("=" * 80)
print()

# Backup App.tsx
backup_app = APP_TSX.parent / f"App.tsx.backup-{timestamp}"
shutil.copy2(APP_TSX, backup_app)
print(f"✓ Backup: {backup_app.name}")
print()

# Read and fix
with open(APP_TSX, 'r', encoding='utf-8') as f:
		app_content = f.read()
	
original_app = app_content

print("  → Fixing import path...")
if "./components/ContactDetailPage" in app_content:
		app_content = app_content.replace(
				"from './components/ContactDetailPage'",
				"from './pages/ContactDetailPage'"
		)
		print("      ✓ Corrected to ./pages/ContactDetailPage")
elif "./pages/ContactDetailPage" in app_content:
		print("      ⊙ Already correct")
else:
		print("      ⚠ Import not found")
	
if app_content != original_app:
		with open(APP_TSX, 'w', encoding='utf-8') as f:
				f.write(app_content)
		print()
		print("✅ App.tsx fixed!")
else:
		print()
		print("⊙ No changes needed")
	
print()
print("=" * 80)
print("✅ INTEGRATION COMPLETE")
print("=" * 80)
print()
print(f"Repository: {REPO_ROOT}")
print(f"Backups: *backup-{timestamp}")
print()
print("=" * 80)
print("DEPLOY")
print("=" * 80)
print()
print(f"cd {REPO_ROOT}/dashboard_v1")
print("npm run build")
print('git add -A && git commit -m "feat: Wire QualificationTab to dark-UI"')
print("git push origin main")
print("vercel --prod")
print()
print("=" * 80)
print("TEST")
print("=" * 80)
print()
print("1. Open: /contacts/:id")
print("2. Verify: Dark-UI dossier (not white)")
print("3. Click: 'Qualification' tab (4th)")
print("4. Check: APEX/BANT/SPICE scores load")
print()
print("Backend: https://apex-backend-i7b0.onrender.com")
print("Frontend: https://apex-sales-intelligence.vercel.app")
print()
print("🚀 Ready to ship!")
print("=" * 80)
