#!/usr/bin/env python3

# File: fix_apex_production_blockers.py
# Run from: apps/backend/

import os
import sys
from pathlib import Path

# 1. Update main.py with missing endpoints
MAIN_PY_ADDITIONS = '''

# ============================================================
# MISSING ENDPOINTS - ADD BEFORE if __name__ == "__main__"
# ============================================================

@app.get("/api/v2/contacts")
async def list_contacts_v2(limit: int = 50, offset: int = 0):
	"""V2 contacts endpoint - frontend requires this"""
	try:
		conn = get_db_connection()
		cursor = conn.cursor()
		
		cursor.execute("""
			SELECT id, hubspot_id, first_name, last_name, email, phone,
					company, title, linkedin_url, enrichment_status, 
					enriched_at, created_at, updated_at,
					unified_qualification_score
			FROM contacts
			ORDER BY created_at DESC
			LIMIT ? OFFSET ?
		""", (limit, offset))
		
		contacts = [dict(row) for row in cursor.fetchall()]
		
		cursor.execute("SELECT COUNT(*) as total FROM contacts")
		total = cursor.fetchone()["total"]
		
		conn.close()
		
		return {
			"contacts": contacts,
			"total": total,
			"limit": limit,
			"offset": offset
		}
	except Exception as e:
		logger.error(f"v2_contacts error: {e}")
		raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/todays-board")
async def todays_board():
	"""Dashboard main board - top contacts"""
	try:
		conn = get_db_connection()
		cursor = conn.cursor()
		
		# FIXED: Removed apex_score reference
		cursor.execute("""
			SELECT id, first_name, last_name, company, title, email,
					unified_qualification_score, enrichment_status, enriched_at
			FROM contacts
			WHERE enrichment_status IN ('completed', 'enriched')
			ORDER BY COALESCE(unified_qualification_score, 0) DESC
			LIMIT 20
		""")
		
		contacts = [dict(row) for row in cursor.fetchall()]
		conn.close()
		
		return {
			"contacts": contacts,
			"total": len(contacts)
		}
	except Exception as e:
		logger.error(f"todays_board error: {e}")
		raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/user/profile")
async def user_profile(user_id: str = "default"):
	"""User profile (stub)"""
	return {
		"user_id": user_id,
		"name": "Apex User",
		"role": "admin",
		"preferences": {}
	}

# ============================================================
# END ADDITIONS
# ============================================================
'''

def main():
	backend_root = Path.cwd()
	main_py = backend_root / "main.py"
	
	if not main_py.exists():
		print("❌ main.py not found. Run from apps/backend/")
		sys.exit(1)
		
	content = main_py.read_text()
	
	# Check if endpoints already exist
	if "/api/todays-board" in content:
		print("⚠️  Endpoints already added")
		return
	
	# Find insertion point (before if __name__)
	if 'if __name__ == "__main__":' in content:
		parts = content.split('if __name__ == "__main__":')
		new_content = parts[0] + MAIN_PY_ADDITIONS + '\nif __name__ == "__main__":\n' + parts[1]
	else:
		new_content = content + MAIN_PY_ADDITIONS
		
	# Backup
	backup = backend_root / "main.py.backup"
	backup.write_text(content)
	
	# Write
	main_py.write_text(new_content)
	
	print("✅ Added missing endpoints to main.py")
	print("📦 Backup saved to main.py.backup")
	print("\n🚀 Next steps:")
	print("  1. git add main.py")
	print("  2. git commit -m 'fix: Add missing v2 endpoints and fix apex_score query'")
	print("  3. git push")
	print("  4. Wait 2-3 min for Render redeploy")
	print("  5. Test: curl https://apex-backend-i7b0.onrender.com/api/v2/contacts?limit=5")
	
if __name__ == "__main__":
	main()
	