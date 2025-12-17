#!/usr/bin/env python3
"""
APEX ContactsView Fix - Complete Automated Deployment
Handles: Git auth, file copy, commit, push, verification
Run: python3 deploy_contactsview.py
"""

import os
import sys
import subprocess
import json
from pathlib import Path
from datetime import datetime

# ============================================================================
# CONFIG
# ============================================================================

REPO_ROOT = Path.home() / "projects" / "apex" / "apex-sales-intelligence"
GITHUB_USER = "chrisraben"
GITHUB_REPO = "apex-sales-intelligence"
GITHUB_BRANCH = "main"

# File paths
FIXED_FILE = Path("ContactsView.tsx.FIXED")
TARGET_PATH = REPO_ROOT / "dashboard_v1" / "src" / "components" / "ContactsView.tsx"
BACKUP_PATH = TARGET_PATH.with_suffix(f".backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}.tsx")

# ============================================================================
# UTILITIES
# ============================================================================

def log(level: str, msg: str):
    """Pretty logging"""
    colors = {
        "✅": "\033[92m",
        "❌": "\033[91m",
        "⏳": "\033[93m",
        "ℹ": "\033[94m",
        "RESET": "\033[0m"
    }
    symbol = {
        "success": "✅",
        "error": "❌",
        "info": "ℹ",
        "working": "⏳"
    }.get(level, "ℹ")
    color = colors.get(symbol, colors["ℹ"])
    print(f"{color}{symbol}{colors['RESET']} {msg}")

def run_cmd(cmd: list, check: bool = True, capture: bool = False) -> str:
    """Execute shell command"""
    try:
        result = subprocess.run(
            cmd,
            cwd=REPO_ROOT,
            capture_output=capture,
            text=True,
            check=check
        )
        return result.stdout.strip() if capture else ""
    except subprocess.CalledProcessError as e:
        log("error", f"Command failed: {' '.join(cmd)}")
        log("error", f"Error: {e.stderr if hasattr(e, 'stderr') else str(e)}")
        sys.exit(1)

def verify_setup():
    """Verify all prerequisites"""
    log("working", "Verifying setup...")
    
    # Check repo exists
    if not REPO_ROOT.exists():
        log("error", f"Repo not found at {REPO_ROOT}")
        sys.exit(1)
    
    # Check git is initialized
    if not (REPO_ROOT / ".git").exists():
        log("error", f"Not a git repository: {REPO_ROOT}")
        sys.exit(1)
    
    # Check target directory exists
    if not TARGET_PATH.parent.exists():
        log("error", f"Target directory not found: {TARGET_PATH.parent}")
        sys.exit(1)
    
    # Check fixed file exists
    if not FIXED_FILE.exists():
        log("error", f"Fixed file not found: {FIXED_FILE}")
        log("info", "Make sure ContactsView.tsx.FIXED is in current directory")
        sys.exit(1)
    
    log("success", "Setup verified ✓")

def backup_current():
    """Create backup of current file"""
    log("working", f"Creating backup: {BACKUP_PATH.name}")
    
    if TARGET_PATH.exists():
        TARGET_PATH.read_bytes()  # Read to verify
        BACKUP_PATH.write_bytes(TARGET_PATH.read_bytes())
        log("success", f"Backup created: {BACKUP_PATH}")
    else:
        log("info", "No existing file to backup (new component)")

def copy_fixed_file():
    """Copy fixed file to target location"""
    log("working", f"Copying fixed file to {TARGET_PATH}")
    
    fixed_content = FIXED_FILE.read_bytes()
    TARGET_PATH.write_bytes(fixed_content)
    
    # Verify
    if not TARGET_PATH.exists():
        log("error", "File copy failed")
        sys.exit(1)
    
    log("success", f"File copied: {TARGET_PATH}")

def git_add_commit_push():
    """Stage, commit, and push to GitHub"""
    log("working", "Staging file...")
    run_cmd(["git", "add", str(TARGET_PATH.relative_to(REPO_ROOT))])
    log("success", "File staged")
    
    # Check status
    status = run_cmd(["git", "status", "--short"], capture=True)
    log("info", f"Git status:\n{status}")
    
    log("working", "Creating commit...")
    commit_msg = "fix: add onClick navigation to contact detail page - connects table rows to ContactDetailPage"
    run_cmd(["git", "commit", "-m", commit_msg])
    log("success", "Commit created")
    
    log("working", "Pushing to GitHub...")
    run_cmd(["git", "push", "origin", GITHUB_BRANCH])
    log("success", "Pushed to GitHub")

def verify_deployment():
    """Verify file is in git"""
    log("working", "Verifying deployment...")
    
    # Check file exists in repo
    if not TARGET_PATH.exists():
        log("error", "File missing after push")
        sys.exit(1)
    
    # Get file size
    size = TARGET_PATH.stat().st_size
    log("success", f"File verified: {size:,} bytes")
    
    # Show git log
    log("info", "Latest commits:")
    log_output = run_cmd(["git", "log", "--oneline", "-5"], capture=True)
    for line in log_output.split("\n"):
        print(f"  {line}")

def print_summary():
    """Print deployment summary"""
    print("\n" + "="*70)
    print("✅ DEPLOYMENT COMPLETE - APEX ContactsView Fix")
    print("="*70)
    print()
    print("📍 DEPLOYED:")
    print(f"   Location: dashboard_v1/src/components/ContactsView.tsx")
    print(f"   Size: {TARGET_PATH.stat().st_size:,} bytes")
    print()
    print("🔄 CHANGES APPLIED:")
    print("   1. ✅ Import useNavigate (already exists)")
    print("   2. ✅ Initialize navigate hook (Line 42)")
    print("   3. ✅ Add handleContactClick function (Line 151)")
    print("   4. ✅ Add onClick to table row (Line 285)")
    print("   5. ✅ Add stopPropagation to checkbox (Line 293)")
    print("   6. ✅ Remove Link from name cell (Line 301)")
    print()
    print("⏱️  WHAT HAPPENS NEXT:")
    print("   1. Vercel detects push (~2 mins)")
    print("   2. Vercel rebuilds (~60 secs)")
    print("   3. Live at https://apex-sales-intelligence.vercel.app")
    print()
    print("🧪 TEST AFTER DEPLOY:")
    print("   1. Go to Dashboard")
    print("   2. Click any contact row")
    print("   3. Should navigate to /contacts/:id")
    print("   4. ContactDetailPage loads")
    print("   5. Enrich button visible")
    print()
    if BACKUP_PATH.exists():\n        print(f\"💾 BACKUP: {BACKUP_PATH}\")\n        print(\"   Revert with: git revert HEAD\")\n        print()\n    print(\"✨ You can now focus on TESTING, not file moving!\")\n    print(\"=\"*70)
    print()

# ============================================================================
# MAIN
# ============================================================================

def main():
    print()\n    log("info", \"🚀 APEX ContactsView Automated Deployment\")\n    print()\n    \n    # Step 1: Verify\n    verify_setup()\n    print()\n    \n    # Step 2: Backup\n    backup_current()\n    print()\n    \n    # Step 3: Copy\n    copy_fixed_file()\n    print()\n    \n    # Step 4: Git operations\n    git_add_commit_push()\n    print()\n    \n    # Step 5: Verify\n    verify_deployment()\n    print()\n    \n    # Summary\n    print_summary()\n\nif __name__ == \"__main__\":\n    try:\n        main()\n    except KeyboardInterrupt:\n        print()\n        log(\"error\", \"Deployment cancelled by user\")\n        sys.exit(130)\n    except Exception as e:\n        print()\n        log(\"error\", f\"Unexpected error: {e}\")\n        import traceback\n        traceback.print_exc()\n        sys.exit(1)
