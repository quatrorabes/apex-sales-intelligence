#!/bin/bash
# Fix all duplicate import statements

set -e

echo "🔧 Fixing duplicate imports in all component files..."
echo ""

FIXED=0

for file in src/components/*.tsx; do
    # Create temp file
    TEMP="${file}.temp"
    
    # Check if file has the problematic pattern:
    # Line N: import {
    # Line N+1: import { API_BASE_URL } from "../config/api";
    
    if grep -q "^import {$" "$file" && grep -q 'import { API_BASE_URL } from "../config/api";' "$file"; then
        echo "Fixing: $(basename $file)"
        
        # Use awk to remove standalone "import {" lines that come before API_BASE_URL import
        awk '
        BEGIN { prev = "" }
        {
            # If current line is API_BASE_URL import and previous was just "import {"
            if ($0 ~ /^import { API_BASE_URL } from/) {
                if (prev == "import {") {
                    # Skip the previous "import {" line, print current
                    print $0
                    prev = ""
                    next
                }
            }
            
            # Print previous line if it exists
            if (prev != "") {
                print prev
            }
            
            # Store current line as previous
            prev = $0
        }
        END {
            # Print last line
            if (prev != "") print prev
        }
        ' "$file" > "$TEMP"
        
        mv "$TEMP" "$file"
        ((FIXED++))
    fi
done

echo ""
echo "✅ Fixed $FIXED files"
echo ""
echo "Running build test..."
npm run build
