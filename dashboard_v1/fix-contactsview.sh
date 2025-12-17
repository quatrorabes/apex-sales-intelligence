#!/bin/bash

# ============================================================================
# APEX SALES INTELLIGENCE - ContactsView.tsx FIX
# Adds onClick row navigation to contact detail page
# ============================================================================

set -e

PROJECT_ROOT="${1:-.}"
CONTACTS_VIEW="$PROJECT_ROOT/dashboardv1/src/components/ContactsView.tsx"

echo "🔧 Fixing ContactsView.tsx..."
echo "Target: $CONTACTS_VIEW"

if [ ! -f "$CONTACTS_VIEW" ]; then
    echo "❌ File not found: $CONTACTS_VIEW"
    exit 1
fi

# Create backup
BACKUP_DIR="$PROJECT_ROOT/dashboardv1/src/components"
BACKUP_FILE="$BACKUP_DIR/ContactsView.tsx.backup.$(date +%s)"
cp "$CONTACTS_VIEW" "$BACKUP_FILE"
echo "✅ Backup created: $BACKUP_FILE"

# Apply fixes using sed
echo ""
echo "📝 Applying fixes..."

# Fix 1: Already has useNavigate import, so skip this

# Fix 2: Add navigate hook initialization after export default line
sed -i.tmp '44a\    const navigate = useNavigate();' "$CONTACTS_VIEW"
echo "✓ Fix 2: Added navigate hook"

# Fix 3: Add handleContactClick function after selectAll function
cat >> "$CONTACTS_VIEW" << 'EOF'

    // ✅ NEW: Handle row click navigation
    const handleContactClick = (contactId: string) => {
        navigate(`/contacts/${contactId}`);
    };
EOF
echo "✓ Fix 3: Added handleContactClick function"

# Fix 4-6: These require more complex replacements - using the complete fixed file instead
echo "✓ Fix 4-6: Ready (apply complete file)"

# Clean up temp file
rm -f "$CONTACTS_VIEW.tmp"

echo ""
echo "✅ Script complete! Now apply the COMPLETE FIXED FILE below"
echo ""
echo "Deploy with:"
echo "  git add dashboardv1/src/components/ContactsView.tsx"
echo "  git commit -m 'fix: add onClick navigation to contact detail page'"
echo "  git push origin main"
echo ""
echo "Vercel redeploys in ~60 seconds ✨"
