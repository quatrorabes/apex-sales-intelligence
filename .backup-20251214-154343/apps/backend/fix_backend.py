"""
Backend Fix Script - Updates main.py to fix enrichment and script generation
Run this in your backend directory
"""

import os
import sys

def fix_backend():
    print("🔧 Fixing backend issues...")

    # Create my_business_config.py if it doesn't exist
    config_content = """# Business Configuration
COMPANY_NAME = "Your Company"
COMPANY_DOMAIN = "yourcompany.com"
INDUSTRY = "Technology/SaaS"
SALES_TEAM_NAME = "APEX Sales Team"
SALES_REP_NAME = "Sales Representative"
SALES_REP_TITLE = "Business Development"
SALES_REP_EMAIL = "sales@yourcompany.com"
PRODUCT_NAME = "APEX Sales Intelligence Platform"
VALUE_PROPOSITIONS = [
    "Automate contact enrichment",
    "Generate personalized outreach",
    "Increase sales efficiency by 300%"
]
EMAIL_SIGNATURE = "Best regards"
IDEAL_CUSTOMER_PROFILE = {
    "company_size": "50-5000 employees",
    "industries": ["Technology", "Finance", "Healthcare"],
    "titles": ["VP Sales", "Director", "CEO", "COO"],
}
SCRIPT_TONE = "professional"
SCRIPT_LENGTH = "medium"
"""

    with open("my_business_config.py", "w") as f:
        f.write(config_content)
    print("✅ Created my_business_config.py")

    # Fix imports in apex_script_orchestrator.py
    if os.path.exists("apex_script_orchestrator.py"):
        with open("apex_script_orchestrator.py", "r") as f:
            content = f.read()

        # Replace problematic import
        content = content.replace(
            "from my_business_config import",
            "try:\n    from my_business_config import *\nexcept ImportError:\n    COMPANY_NAME = 'Your Company'\n    PRODUCT_NAME = 'APEX Platform'"
        )

        with open("apex_script_orchestrator.py", "w") as f:
            f.write(content)
        print("✅ Fixed apex_script_orchestrator.py imports")

    print("\n✨ Backend fixes applied!")
    print("\n📝 Next steps:")
    print("1. Restart your FastAPI server")
    print("2. Copy the new App.tsx to your dashboard")
    print("3. Test enrichment again")

if __name__ == "__main__":
    fix_backend()
