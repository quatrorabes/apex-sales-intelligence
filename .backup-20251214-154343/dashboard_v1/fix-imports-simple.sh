#!/bin/bash

echo "🔧 Fixing duplicate import statements..."

# For each TypeScript component file
for file in src/components/*.tsx; do
    # Check if file has the problem pattern
    if grep -Pzo 'import \{\n import \{ API_BASE_URL \}' "$file" > /dev/null 2>&1; then
        echo "Fixing: $(basename $file)"
        
        # Remove lines that are ONLY "import {" and followed by API_BASE_URL import
        perl -i -p0e 's/import \{\s*\n\s*import \{ API_BASE_URL \}/import { API_BASE_URL }/g' "$file"
    fi
done

echo "✅ Done!"
