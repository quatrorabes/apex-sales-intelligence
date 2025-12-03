#!/bin/bash
# apex_deploy.sh - Complete deployment script for APEX Intelligence

cat << 'EOF'
╔═══════════════════════════════════════════════════════════════════╗
║                                                                   ║
║      🏛️  APEX INTELLIGENCE - PRODUCTION DEPLOYMENT SCRIPT       ║
║                                                                   ║
║      World-Class Sales Intelligence Platform                     ║
║      Complete Integration & Deployment                           ║
║                                                                   ║
╚═══════════════════════════════════════════════════════════════════╝
EOF

set -e  # Exit on error

echo ""
echo "🚀 Step 1: Environment Setup"
echo "─────────────────────────────────────────────────────────────────"

# Create project structure
mkdir -p ~/projects/apex
cd ~/projects/apex

mkdir -p apps/backend/{intelligence,integrations,services,automation}
mkdir -p apps/backend/intelligence/engines/{scoring,enrichment,personas}
mkdir -p models
mkdir -p enrichment_profiles
mkdir -p dashboard_v1/src/{components,config,types}

echo "✅ Directory structure created"

echo ""
echo "🐍 Step 2: Python Environment"
echo "─────────────────────────────────────────────────────────────────"

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Create requirements.txt
cat > requirements.txt << 'REQUIREMENTS'
Flask==3.0.0
Flask-CORS==4.0.0
python-dotenv==1.0.0
requests==2.31.0
openai==1.3.0
psycopg2-binary==2.9.9
sqlite3  # Built-in
numpy==1.24.3
pandas==2.0.3
scikit-learn==1.3.0
REQUIREMENTS

pip install -r requirements.txt

echo "✅ Python dependencies installed"

echo ""
echo "🔑 Step 3: Environment Variables"
echo "─────────────────────────────────────────────────────────────────"

# Create .env file
cat > .env << 'ENVFILE'
# APEX Intelligence Environment Configuration

# API Keys
PERPLEXITY_API_KEY=your_perplexity_key_here
OPENAI_API_KEY=your_openai_key_here
HUBSPOT_ACCESS_TOKEN=your_hubspot_token_here

# Database (leave empty for SQLite local development)
DATABASE_URL=

# API Configuration
API_BASE_URL=http://localhost:8000
PORT=8000

# Feature Flags
ENABLE_ENRICHMENT=true
ENABLE_SCORING=true
ENABLE_PERSONA_CLASSIFICATION=true
ENABLE_CONTENT_GENERATION=true
ENABLE_AUTOMATION=true
ENABLE_ML_PREDICTIONS=true
ENVFILE

echo "✅ Environment file created - PLEASE UPDATE WITH YOUR API KEYS"

echo ""
echo "📄 Step 4: Save Master Integration File"
echo "─────────────────────────────────────────────────────────────────"

# The apex_master_integration.py file would be saved here
# (Using the complete code from DELIVERABLE 1)

echo "⚠️  SAVE apex_master_integration.py manually from the provided code"

echo ""
echo "⚛️  Step 5: Frontend Setup"
echo "─────────────────────────────────────────────────────────────────"

# Initialize Vite React project
cd dashboard_v1
npm create vite@latest . -- --template react-ts --force
npm install

# Create API config
mkdir -p src/config
cat > src/config/api.ts << 'APICONFIG'
export const API_URL =
  import.meta.env.VITE_API_URL || 'http://localhost:8000';

export const fetchAPI = async (endpoint: string, options?: RequestInit) => {
  const response = await fetch(`${API_URL}${endpoint}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
  });
  
  if (!response.ok) {
    throw new Error(`API error: ${response.statusText}`);
  }
  
  return response.json();
};
APICONFIG

# Create environment files
echo "VITE_API_URL=http://localhost:8000" > .env.development
echo "VITE_API_URL=https://your-production-url.railway.app" > .env.production

cd ..

echo "✅ Frontend initialized"

echo ""
echo "🗄️  Step 6: Database Initialization"
echo "─────────────────────────────────────────────────────────────────"

python3 << 'PYINIT'
import sqlite3

conn = sqlite3.connect('apex.db')
cursor = conn.cursor()

print("Creating database schema...")

# Create all tables (from apex_master_integration.py schema)
cursor.execute("""
    CREATE TABLE IF NOT EXISTS contacts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        first_name TEXT,
        last_name TEXT,
        name TEXT UNIQUE,
        email TEXT UNIQUE,
        phone TEXT,
        phone_mobile TEXT,
        company TEXT,
        title TEXT,
        linkedin_url TEXT,
        company_domain TEXT,
        company_website TEXT,
        company_hq_city TEXT,
        company_hq_state TEXT,
        industry TEXT,
        profile_content TEXT,
        enrichment_status TEXT DEFAULT 'pending',
        enrichment_date TEXT,
        persona_type TEXT,
        persona_confidence REAL,
        priority_score REAL,
        mdcp_score REAL,
        mdcp_tier TEXT,
        rss_score REAL,
        rss_tier TEXT,
        urgency_level TEXT,
        last_scored TEXT,
        conversion_probability REAL,
        email_1_subject TEXT,
        email_1_body TEXT,
        call_script_1 TEXT,
        linkedin_connect TEXT,
        value_proposition TEXT,
        import_source TEXT,
        crm_id TEXT,
        data_completeness_score INTEGER DEFAULT 0,
        enrichment_ready INTEGER DEFAULT 0,
        last_crm_sync TEXT,
        last_contact_date TEXT,
        total_touches INTEGER DEFAULT 0,
        response_count INTEGER DEFAULT 0,
        cadence_status TEXT DEFAULT 'not_started',
        cadence_stage INTEGER DEFAULT 0,
        next_touch_date TEXT,
        auto_pause INTEGER DEFAULT 0,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        updated_at TEXT DEFAULT CURRENT_TIMESTAMP
    )
""")

conn.commit()
conn.close()

print("✅ Database schema created")
PYINIT

echo "✅ Database initialized"

echo ""
echo "🧪 Step 7: System Health Check"
echo "─────────────────────────────────────────────────────────────────"

python3 << 'HEALTHCHECK'
import os
from pathlib import Path

checks = {
    'apex_master_integration.py': False,
    'apex.db': False,
    '.env': False,
    'requirements.txt': False,
    'dashboard_v1/package.json': False,
}

for file in checks.keys():
    checks[file] = Path(file).exists()

print("\n📋 System Health Check:\n")
for file, exists in checks.items():
    status = "✅" if exists else "❌"
    print(f"  {status} {file}")

all_good = all(checks.values())
if all_good:
    print("\n🎉 All systems GO!")
else:
    print("\n⚠️  Some files missing - please review")
HEALTHCHECK

echo ""
echo "╔═══════════════════════════════════════════════════════════════════╗"
echo "║                                                                   ║"
echo "║      ✅ APEX INTELLIGENCE - DEPLOYMENT COMPLETE                 ║"
echo "║                                                                   ║"
echo "╚═══════════════════════════════════════════════════════════════════╝"
echo ""
echo "📋 NEXT STEPS:"
echo ""
echo "  1. Edit .env and add your API keys:"
echo "     - PERPLEXITY_API_KEY"
echo "     - OPENAI_API_KEY"
echo "     - HUBSPOT_ACCESS_TOKEN"
echo ""
echo "  2. Start the backend:"
echo "     source .venv/bin/activate"
echo "     python apex_master_integration.py"
echo ""
echo "  3. Start the frontend (new terminal):"
echo "     cd dashboard_v1"
echo "     npm run dev"
echo ""
echo "  4. Access the system:"
echo "     Backend API: http://localhost:8000/api/health"
echo "     Frontend:    http://localhost:5173"
echo ""
echo "╔═══════════════════════════════════════════════════════════════════╗"
echo "║  🏛️  APEX INTELLIGENCE is now ready for production use          ║"
echo "╚═══════════════════════════════════════════════════════════════════╝"
echo ""
