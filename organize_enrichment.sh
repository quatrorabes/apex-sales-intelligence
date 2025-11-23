#!/bin/bash
# Setup script based on your actual directory structure

echo "🔧 Setting up organized enrichment module structure..."

# Navigate to backend directory
cd ~/projects/apex/apps/backend

# Create the enrichment subdirectory under intelligence
echo "📁 Creating intelligence/enrichment directory..."
mkdir -p intelligence/enrichment

# Create __init__.py files if they don't exist
echo "📄 Creating __init__.py files..."
touch intelligence/__init__.py
touch intelligence/enrichment/__init__.py

# Move the best version of the module to the proper location
echo "📦 Moving perplexity module to organized location..."
cp perplexity_deep_enrichment_module_fixed*.py intelligence/enrichment/perplexity_enrichment.py 2>/dev/null || cp perplexity_deep_enrichment_module.py intelligence/enrichment/perplexity_enrichment.py

# Create the enrichment __init__.py with imports
cat > intelligence/enrichment/__init__.py << 'EOF'
'''
Enrichment Module
Handles all contact enrichment operations
'''

from .perplexity_enrichment import enrich_contact, PerplexityEnrichment

__all__ = ['enrich_contact', 'PerplexityEnrichment']
EOF

echo "✅ Directory structure created:"
echo "   apps/backend/"
echo "   └── intelligence/"
echo "       ├── __init__.py"
echo "       └── enrichment/"
echo "           ├── __init__.py"
echo "           └── perplexity_enrichment.py"

# Clean up old files from root and backend
echo ""
echo "🧹 Cleaning up old enrichment files..."
echo "Moving old files to archive-apex for backup:"

# Move old enrichment files to archive
cd ~/projects/apex
mv enhanced_person_enrichment_fixed.py archive-apex/ 2>/dev/null
mv fixed_comprehensive_enrichment.py archive-apex/ 2>/dev/null
mv main_py_integration.py archive-apex/ 2>/dev/null
mv quick_enrichment.py archive-apex/ 2>/dev/null

echo ""
echo "✅ Setup complete!"
echo ""
echo "📝 Next steps:"
echo "1. Update main.py import:"
echo "   Change: from perplexity_deep_enrichment_module import enrich_contact"
echo "   To:     from intelligence.enrichment import enrich_contact"
echo ""
echo "2. Restart the server:"
echo "   cd ~/projects/apex/apps/backend"
echo "   python main.py"
