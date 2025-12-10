import re
from pathlib import Path

file = Path("ContactDetailPage.tsx")
content = file.read_text()

# Find where parsing starts (line with "const raw = contact.profile_content")
if "const raw = contact.profile_content" in content:
    # Add safety check before parsing
    safety_check = """
  // Safety check - prevent crash during re-renders
  if (!contact) {
    return (
      <div className="min-h-screen bg-[#0d1117] flex items-center justify-center text-gray-400">
        Loading contact data...
      </div>
    );
  }

"""
    content = content.replace(
        "  // PARSE ENRICHMENT DATA",
        safety_check + "  // PARSE ENRICHMENT DATA"
    )
    
    file.write_text(content)
    print("✅ Added safety check for undefined contact")
else:
    print("❌ Could not find parsing section")
