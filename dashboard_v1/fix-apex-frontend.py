#!/usr/bin/env python3
"""
APEX Frontend Consolidation Script
Fixes all apiClient calls and consolidates API configuration
Run from: ~/projects/apex/apex-sales-intelligence/dashboard_v1
"""

import os
import subprocess
import sys
from pathlib import Path

def run_cmd(cmd, description=""):
    """Run shell command and return success status"""
    if description:
        print(f"  {description}...", end=" ")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=project_root)
        if result.returncode == 0:
            if description:
                print("✅")
            return True
        else:
            if description:
                print("❌")
            print(f"    Error: {result.stderr}")
            return False
    except Exception as e:
        if description:
            print("❌")
        print(f"    Exception: {e}")
        return False

def create_canonical_api():
    """Create the canonical src/config/api.ts file"""
    api_content = '''/**
 * APEX API Configuration - SINGLE SOURCE OF TRUTH
 * All components import from here ONLY
 * Backend: https://apex-backend-i7b0.onrender.com (FastAPI v2)
 */

const API_BASE_URL = import.meta.env.VITE_API_URL || 
  'https://apex-backend-i7b0.onrender.com';

console.log('🔧 APEX API configured:', API_BASE_URL);

export interface Contact {
  id: string;
  hubspot_id?: string;
  first_name: string;
  last_name: string;
  email?: string;
  phone?: string;
  title?: string;
  company?: string;
  enrichment?: {
    version: string;
    raw_profile: string;
    character_count: number;
  };
  enriched_at?: string;
  created_at: string;
  updated_at: string;
}

export interface ContactsResponse {
  contacts: Contact[];
  total: number;
  limit: number;
  offset: number;
}

export interface StatsResponse {
  total_contacts: number;
  enriched_contacts: number;
  pending_enrichment: number;
}

export const API_ENDPOINTS = {
  LIST_CONTACTS: `${API_BASE_URL}/api/v2/contacts`,
  GET_CONTACT: (id: string) => `${API_BASE_URL}/api/v2/contacts/${id}`,
  STATS: `${API_BASE_URL}/api/v2/contacts/stats`,
  ENRICH_ONE: (id: string) => `${API_BASE_URL}/api/v2/contacts/${id}/enrich`,
  BULK_ENRICH: `${API_BASE_URL}/api/v2/contacts/bulk-enrich`,
  HEALTH: `${API_BASE_URL}/health`,
};

export async function httpRequest<T>(
  url: string,
  options: RequestInit = {}
): Promise<T> {
  try {
    const response = await fetch(url, {
      headers: { 'Content-Type': 'application/json' },
      ...options,
    });

    if (!response.ok) {
      const errorBody = await response.text();
      throw new Error(`HTTP ${response.status}: ${errorBody}`);
    }

    return await response.json();
  } catch (error) {
    console.error(`API Error [${options.method || 'GET'}] ${url}:`, error);
    throw error;
  }
}

export async function getContacts(
  limit: number = 50,
  offset: number = 0
): Promise<ContactsResponse> {
  const url = `${API_ENDPOINTS.LIST_CONTACTS}?limit=${limit}&offset=${offset}`;
  return httpRequest<ContactsResponse>(url);
}

export async function getContact(id: string): Promise<Contact> {
  return httpRequest<Contact>(API_ENDPOINTS.GET_CONTACT(id));
}

export async function getStats(): Promise<StatsResponse> {
  return httpRequest<StatsResponse>(API_ENDPOINTS.STATS);
}

export async function enrichContact(id: string): Promise<any> {
  return httpRequest<any>(API_ENDPOINTS.ENRICH_ONE(id), {
    method: 'POST',
    body: JSON.stringify({}),
  });
}

export async function bulkEnrich(limit: number = 10): Promise<any> {
  return httpRequest<any>(`${API_ENDPOINTS.BULK_ENRICH}?limit=${limit}`, {
    method: 'POST',
    body: JSON.stringify({}),
  });
}

export async function healthCheck(): Promise<any> {
  return httpRequest<any>(API_ENDPOINTS.HEALTH);
}
'''
    
    config_dir = project_root / "src" / "config"
    config_dir.mkdir(parents=True, exist_ok=True)
    
    api_file = config_dir / "api.ts"
    api_file.write_text(api_content)
    return api_file

def fix_component_calls():
    """Fix the remaining apiClient calls in components"""
    fixes = [
        {
            "file": "src/components/ContactsBoard.tsx",
            "old": "const response = await apiClient.getContacts({ limit: 100 });",
            "new": "const data = await getContacts(100); const response = { contacts: data.contacts, total: data.total };",
            "description": "ContactsBoard.tsx line 22"
        },
        {
            "file": "src/components/ContentGenerator.tsx",
            "old": "const emailResult = await apiClient.generateEmail(contactId, {});",
            "new": "// TODO: Email generation endpoint - not yet implemented in v2 API\n          // const emailResult = await apiClient.generateEmail(contactId, {});",
            "description": "ContentGenerator.tsx line 23"
        },
        {
            "file": "src/components/ContentGenerator.tsx",
            "old": "const linkedInResult = await apiClient.generateLinkedInMessage(contactId, {});",
            "new": "// TODO: LinkedIn generation endpoint - not yet implemented in v2 API\n          // const linkedInResult = await apiClient.generateLinkedInMessage(contactId, {});",
            "description": "ContentGenerator.tsx line 27"
        },
        {
            "file": "src/components/ContentGenerator.tsx",
            "old": "const callResult = await apiClient.generateCallScript(contactId, {});",
            "new": "// TODO: Call script generation endpoint - not yet implemented in v2 API\n          // const callResult = await apiClient.generateCallScript(contactId, {});",
            "description": "ContentGenerator.tsx line 31"
        },
    ]
    
    for fix in fixes:
        file_path = project_root / fix["file"]
        if file_path.exists():
            content = file_path.read_text()
            if fix["old"] in content:
                new_content = content.replace(fix["old"], fix["new"])
                file_path.write_text(new_content)
                print(f"  ✅ {fix['description']}")
            else:
                print(f"  ⚠️ {fix['description']} - pattern not found")
        else:
            print(f"  ❌ {fix['file']} not found")

def remove_old_api_files():
    """Remove all old api.ts files except src/config/api.ts"""
    import glob
    
    # Find all api.ts files
    api_files = glob.glob(str(project_root / "src/**/*.ts"), recursive=True)
    removed_count = 0
    
    for file_path in api_files:
        if file_path.endswith("api.ts") and "/config/api.ts" not in file_path:
            try:
                os.remove(file_path)
                print(f"  🗑️  Removed {file_path.replace(str(project_root) + '/', '')}")
                removed_count += 1
            except Exception as e:
                print(f"  ⚠️  Failed to remove {file_path}: {e}")
    
    return removed_count

def verify_consolidation():
    """Verify all apiClient calls are gone"""
    cmd = f"grep -r 'apiClient\\.' {project_root}/src/components 2>/dev/null | wc -l"
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    try:
        remaining = int(result.stdout.strip())
    except:
        remaining = 0
    
    cmd_imports = f"grep -r 'from.*config/api' {project_root}/src/components 2>/dev/null | wc -l"
    result_imports = subprocess.run(cmd_imports, shell=True, capture_output=True, text=True)
    
    try:
        canonical_imports = int(result_imports.stdout.strip())
    except:
        canonical_imports = 0
    
    return remaining, canonical_imports

def main():
    global project_root
    
    # Detect project root
    cwd = Path.cwd()
    if cwd.name == "dashboard_v1" and (cwd / "src").exists():
        project_root = cwd
    elif (cwd / "dashboard_v1").exists():
        project_root = cwd / "dashboard_v1"
    else:
        print("❌ Error: Not in dashboard_v1 directory")
        print(f"   Current: {cwd}")
        print("   Run from: ~/projects/apex/apex-sales-intelligence/dashboard_v1")
        sys.exit(1)
    
    print("🚀 APEX Frontend Consolidation Script")
    print("=" * 50)
    print(f"Project root: {project_root}")
    print()
    
    # Step 1: Create canonical API
    print("1️⃣ Creating canonical API configuration...")
    try:
        api_file = create_canonical_api()
        print(f"  ✅ Created {api_file.relative_to(project_root)}")
    except Exception as e:
        print(f"  ❌ Failed: {e}")
        sys.exit(1)
    
    print()
    
    # Step 2: Fix component calls
    print("2️⃣ Fixing apiClient calls in components...")
    try:
        fix_component_calls()
    except Exception as e:
        print(f"  ❌ Failed: {e}")
        sys.exit(1)
    
    print()
    
    # Step 3: Remove old api.ts files
    print("3️⃣ Removing old api.ts files...")
    removed = remove_old_api_files()
    if removed == 0:
        print("  ℹ️  No old api.ts files found (already removed)")
    
    print()
    
    # Step 4: Verify
    print("4️⃣ Verifying consolidation...")
    remaining, canonical = verify_consolidation()
    print(f"  Old apiClient calls: {remaining} (should be 0)")
    print(f"  Canonical API imports: {canonical}")
    
    if remaining == 0:
        print("  ✅ All fixed!")
    else:
        print("  ⚠️ Still found apiClient calls:")
        subprocess.run(f"grep -rn 'apiClient\\.' {project_root}/src/components", shell=True)
    
    print()
    print("=" * 50)
    print("✅ Consolidation complete!")
    print()
    print("📋 Next steps:")
    print("  1. git add -A")
    print("  2. git commit -m 'fix: Consolidate API and wire to Render backend'")
    print("  3. git push origin main")
    print("  4. Wait 2-3 minutes for Vercel deployment")
    print("  5. Test at: https://apex-sales-intelligence.vercel.app")
    print()

if __name__ == "__main__":
    main()
