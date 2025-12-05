#!/bin/bash
# Fix the broken intelligence/__init__.py file

echo "🔧 Fixing intelligence/__init__.py import error..."

cd ~/projects/apex/apps/backend

# Backup the current file
cp intelligence/__init__.py intelligence/__init__.py.backup 2>/dev/null

# Replace with a simple, working version
cat > intelligence/__init__.py << 'EOF'
# intelligence/__init__.py
"""
Intelligence Module
Contains scoring and enrichment capabilities
"""

# Module initialization - submodules handle their own imports
# No direct imports here to avoid circular dependencies
EOF

echo "✅ Fixed intelligence/__init__.py"
echo ""

# Now test the import
echo "Testing import..."
python -c 'from intelligence.enrichment import enrich_contact; print("✅ Import works!")'

if [ $? -eq 0 ]; then
    echo "✅ Success! The import is now working."
else
    echo "⚠️ Still having issues. Let's check what files exist:"
    echo ""
    echo "Files in intelligence/:"
    ls -la intelligence/
    echo ""
    echo "Files in intelligence/enrichment/:"
    ls -la intelligence/enrichment/
fi
