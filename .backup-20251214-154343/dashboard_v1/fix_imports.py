import os
import re

# Directory containing component files
components_dir = 'src/components'

fixed_count = 0

for filename in os.listdir(components_dir):
    if filename.endswith('.tsx'):
        filepath = os.path.join(components_dir, filename)
        
        with open(filepath, 'r') as f:
            content = f.read()
        
        # Pattern: standalone "import {" followed by API_BASE_URL import
        original = content
        
        # Fix the duplicate import pattern
        content = re.sub(
            r'import \{\s*\n\s*import \{ API_BASE_URL \}',
            r'import { API_BASE_URL }',
            content
        )
        
        if content != original:
            with open(filepath, 'w') as f:
                f.write(content)
            print(f'✅ Fixed: {filename}')
            fixed_count += 1

print(f'\n✅ Fixed {fixed_count} files')
