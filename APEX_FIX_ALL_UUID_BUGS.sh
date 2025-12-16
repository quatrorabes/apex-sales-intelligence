#!/bin/bash
set -e

echo "🔧 Fixing ALL UUID bugs..."

# Fix ContactDetail.tsx (components)
sed -i '' 's/id: number;/id: string;  \/\/ UUID from PostgreSQL/' dashboard_v1/src/components/ContactDetail.tsx

# Delete unused files
rm -f dashboard_v1/src/components/ContactDetailModal.tsx
rm -f dashboard_v1/src/pages/AllContactsView.tsx
rm -f dashboard_v1/src/components/ContactsList.tsx
rm -f dashboard_v1/src/components/ContactsBoard.tsx

echo "✅ Fixed ContactDetail.tsx"
echo "✅ Deleted 4 unused files"
echo ""
echo "📤 Deploy:"
echo "  git add -A"
echo "  git commit -m 'fix: UUID support in ContactDetail + cleanup'"
echo "  git push origin main"
