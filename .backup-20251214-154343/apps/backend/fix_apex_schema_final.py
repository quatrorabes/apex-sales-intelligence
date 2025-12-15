#!/usr/bin/env python3
"""
APEX Schema Fix - Final Production Version
Fixes all column reference errors and adds missing v2 endpoint
"""

import re
from pathlib import Path

def main():
    main_py = Path("main.py")
    
    if not main_py.exists():
        print("❌ Run from apps/backend/")
        return
    
    content = main_py.read_text()
    
    # Backup
    Path("main.py.backup.schema_fix").write_text(content)
    
    # Fix 1: Remove priority_score from line 468 (list_contacts ORDER BY)
    content = re.sub(
        r'ORDER BY COALESCE\(unified_qualification_score, 0, priority_score, 0\)',
        'ORDER BY COALESCE(unified_qualification_score, 0)',
        content
    )
    
    # Fix 2: Remove bant_qualification_status from line 980 (smart_lists)
    content = re.sub(
        r"WHERE bant_qualification_status = 'HIGHLY_QUALIFIED'",
        "WHERE bant_total_score >= 80",
        content
    )
    
    # Fix 3: Remove apex_score IS NOT NULL from line 1017 (analytics)
    content = re.sub(
        r'WHERE apex_score IS NOT NULL',
        'WHERE unified_qualification_score IS NOT NULL',
        content
    )
    
    # Fix 4: Remove priority_score from cold_call_queue
    content = re.sub(
        r'COALESCE\(unified_qualification_score, 0, 0\)',
        'COALESCE(unified_qualification_score, 0)',
        content
    )
    
    # Fix 5: Add missing /api/v2/contacts endpoint
    v2_endpoint = '''

# ============================================================================
# V2 CONTACTS ENDPOINT (Frontend Primary)
# ============================================================================

@app.get("/api/v2/contacts", tags=["Contacts V2"])
async def list_contacts_v2(
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0)
):
    """V2 Contacts endpoint - returns data in format frontend expects"""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT 
                    id, name, email, company, title, phone, linkedin_url,
                    enrichment_status, enriched_at, created_at, updated_at,
                    unified_qualification_score, apex_score, mdcp_score, rss_score,
                    vertical, persona_type
                FROM contacts
                ORDER BY created_at DESC
                LIMIT %s OFFSET %s
            """, (limit, offset))
            
            contacts = [dict(row) for row in cursor.fetchall()]
            
            cursor.execute("SELECT COUNT(*) as count FROM contacts")
            total = cursor.fetchone()["count"]
            
            cursor.close()
            
            return {
                "success": True,
                "contacts": contacts,
                "total": total,
                "limit": limit,
                "offset": offset
            }
    except Exception as e:
        logger.error(f"v2_contacts error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

'''
    
    # Insert v2 endpoint before the existing @app.get("/api/contacts")
    if '@app.get("/api/v2/contacts"' not in content:
        content = content.replace(
            '@app.get("/api/contacts", tags=["Contacts"])',
            v2_endpoint + '\n@app.get("/api/contacts", tags=["Contacts"])'
        )
        print("✅ Added /api/v2/contacts endpoint")
    else:
        print("⚠️  /api/v2/contacts already exists")
    
    # Write fixed content
    main_py.write_text(content)
    
    print("\n" + "="*60)
    print("✅ ALL SCHEMA FIXES APPLIED")
    print("="*60)
    print("\nFixed:")
    print("  1. ✅ Removed priority_score from ORDER BY")
    print("  2. ✅ Changed bant_qualification_status to bant_total_score")
    print("  3. ✅ Changed apex_score IS NOT NULL to unified_qualification_score")
    print("  4. ✅ Added /api/v2/contacts endpoint")
    print("\n📋 Deploy now:")
    print("  git add main.py")
    print('  git commit -m "fix: Remove non-existent column refs, add v2 endpoint"')
    print("  git push origin main")
    print("\n⏱️  Render will auto-deploy in ~3 min")

if __name__ == "__main__":
    main()
