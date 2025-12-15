#!/bin/bash

#!/bin/bash
# APEX Custom Enrichment Migration Script
# Moves apex_custom_enrichment.py into backend architecture

set -e

echo "=========================================="
echo "🚀 APEX Custom Enrichment Migration"
echo "=========================================="

# Check if file exists in root
if [ ! -f "apex_custom_enrichment.py" ]; then
	echo "❌ Error: apex_custom_enrichment.py not found in root directory"
	exit 1
fi

echo "✅ Found apex_custom_enrichment.py"

# Create target directory if it doesn't exist
TARGET_DIR="apps/backend/intelligence/engines/enrichment"
mkdir -p "$TARGET_DIR"

# Move file
echo "📦 Moving apex_custom_enrichment.py → $TARGET_DIR/"
mv apex_custom_enrichment.py "$TARGET_DIR/"

echo "✅ File moved successfully"

# Create __init__.py if it doesn't exist
if [ ! -f "$TARGET_DIR/__init__.py" ]; then
	echo "📝 Creating $TARGET_DIR/__init__.py"
	cat > "$TARGET_DIR/__init__.py" << 'EOF'
"""
APEX Enrichment Engines
"""
from .apex_custom_enrichment import ApexCustomEnrichment
from .enhanced_enrichment import EnhancedEnrichment

__all__ = ['ApexCustomEnrichment', 'EnhancedEnrichment']
EOF
fi

echo "✅ Migration complete!"
echo ""
echo "Next steps:"
echo "1. Run: python scripts/test_apex_custom_import.py"
echo "2. Update API route: apps/backend/api/routes/enrichment.py"
echo "3. Test with: python scripts/test_rj_opeka_enrichment.py"
echo ""
