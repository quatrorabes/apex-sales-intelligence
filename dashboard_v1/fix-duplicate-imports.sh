echo "🔍 Finding files with duplicate import statements..."

for file in src/components/*.tsx; do
    # Check if file has consecutive "import {" lines
    if grep -q "^import {" "$file"; then
        # Count consecutive import { lines
        DUPES=$(grep -A 1 "^import {" "$file" | grep "^import {" | wc -l | tr -d ' ')
        
        if [ "$DUPES" -gt "1" ]; then
            echo "⚠️  Found duplicate in: $(basename $file)"
            
            # Show the problem lines
            grep -n "^import {" "$file" | head -3
            echo ""
        fi
    fi
done

echo ""
echo "🔧 Manual fix required for files listed above"
echo "Open each file and remove duplicate 'import {' lines"