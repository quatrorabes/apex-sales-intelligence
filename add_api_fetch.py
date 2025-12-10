#!/usr/bin/env python3
"""Add API fetch to ContactDetail.tsx"""

import re
from pathlib import Path

FILE = Path("dashboard_v1/src/components/ContactDetail.tsx")

with open(FILE, 'r') as f:
    content = f.read()

# 1. Add axios import after React
if "import axios" not in content:
    content = re.sub(
        r"(import React.*from ['\"]react['\"];)",
        r"\1\nimport axios from 'axios';",
        content
    )

# 2. Add API_BASE_URL constant
if "API_BASE_URL" not in content:
    # Add after imports
    last_import = content.rfind("import ")
    next_line = content.find("\n", last_import) + 1
    content = (content[:next_line] + 
               "\nconst API_BASE_URL = 'https://apex-backend-i7b0.onrender.com';\n\n" +
               content[next_line:])

# 3. Find function start and add state + useEffect
func_pattern = r"(export (?:default )?function ContactDetail.*?\{)"
match = re.search(func_pattern, content)

if match:
    inject_point = match.end()
    
    # Add state and fetch logic
    fetch_code = """
  const [contact, setContact] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchContact = async () => {
      try {
        console.log('Fetching contact:', id);
        const response = await axios.get(`${API_BASE_URL}/api/contacts/${id}`);
        console.log('Contact data:', response.data);
        setContact(response.data.contact);
      } catch (error) {
        console.error('Failed to fetch contact:', error);
      } finally {
        setLoading(false);
      }
    };

    if (id) {
      fetchContact();
    }
  }, [id]);

  if (loading) {
    return <div className="min-h-screen bg-[#0d1117] flex items-center justify-center text-gray-400">Loading...</div>;
  }

  if (!contact) {
    return <div className="min-h-screen bg-[#0d1117] flex items-center justify-center text-red-400">Contact not found</div>;
  }
"""
    
    content = content[:inject_point] + fetch_code + content[inject_point:]

# Write back
with open(FILE, 'w') as f:
    f.write(content)

print("✅ Added API fetch to ContactDetail.tsx")
print()
print("Next steps:")
print("  cd dashboard_v1")
print("  npm run build")
print("  git add -A && git commit -m 'fix: Add API fetch to ContactDetail' && git push")
