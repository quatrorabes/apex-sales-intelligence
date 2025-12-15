from services.enrichment_parser import parse_enrichment

# Test with Dale's actual data
with open('dale_raw.txt', 'r') as f:
    dale_raw = f.read()

result = parse_enrichment(dale_raw)

print(f"Format: {result['metadata']['format_detected']}")
print(f"Sections found: {result['metadata']['total_sections']}")
print(f"Total chars: {result['metadata']['character_count']}")
print("\nSection keys:")
for key in sorted(result['sections'].keys()):
    char_count = len(result['sections'][key])
    preview = result['sections'][key][:80].replace('\n', ' ')
    print(f"  - {key}: {char_count} chars")
    print(f"    Preview: {preview}...")
