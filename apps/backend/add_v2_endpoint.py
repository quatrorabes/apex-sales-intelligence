#!/usr/bin/env python3
import re
from pathlib import Path

main_py = Path("main.py")
content = main_py.read_text()

# Check if already exists
if '@app.get("/api/v2/contacts"' in content:
    print("✅ /api/v2/contacts already exists")
    exit(0)

# Add before @app.get("/api/contacts")
v2_endpoint = '''
@app.get("/api/v2/contacts", tags=["Contacts V2"])
async def list_contacts_v2(
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0)
):
    """V2 Contacts - Frontend primary endpoint"""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM contacts
                ORDER BY created_at DESC
                LIMIT %s OFFSET %s
            """, (limit, offset))
            contacts = [dict(row) for row in cursor.fetchall()]
            
            cursor.execute("SELECT COUNT(*) FROM contacts")
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

content = content.replace(
    '@app.get("/api/contacts", tags=["Contacts"])',
    v2_endpoint + '@app.get("/api/contacts", tags=["Contacts"])'
)

main_py.write_text(content)
print("✅ Added /api/v2/contacts endpoint")
print("\nDeploy:")
print("  git add main.py")
print('  git commit -m "feat: Add v2 contacts endpoint for frontend"')
print("  git push origin main")
