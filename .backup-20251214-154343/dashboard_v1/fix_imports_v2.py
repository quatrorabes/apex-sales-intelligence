import os
import re

components_dir = 'src/components'
fixed_count = 0

for filename in os.listdir(components_dir):
    if filename.endswith('.tsx'):
        filepath = os.path.join(components_dir, filename)
        
        with open(filepath, 'r') as f:
            lines = f.readlines()
        
        new_lines = []
        skip_next = False
        
        for i, line in enumerate(lines):
            if skip_next:
                skip_next = False
                continue
            
            # Check if this is a standalone "import {" followed by API_BASE_URL import
            if line.strip() == 'import {' and i + 1 < len(lines):
                next_line = lines[i + 1]
                if 'API_BASE_URL' in next_line and next_line.strip().startswith('import'):
                    # Skip this line, next line will be kept
                    skip_next = False
                    continue
            
            new_lines.append(line)
        
        # Write back if changed
        if len(new_lines) != len(lines):
            with open(filepath, 'w') as f:
                f.writelines(new_lines)
            print(f'✅ Fixed: {filename}')
            fixed_count += 1

print(f'\n✅ Fixed {fixed_count} files')
