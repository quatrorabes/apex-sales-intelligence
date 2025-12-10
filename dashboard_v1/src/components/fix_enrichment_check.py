import re
from pathlib import Path

file = Path("ContactsView.tsx")
content = file.read_text()

# 1. Add apex_enrichment_data to the Contact type (around line 29-30)
old_type = '''    enrichment_status?: string;
    enriched_at?: string;'''

new_type = '''    enrichment_status?: string;
    enriched_at?: string;
    apex_enrichment_data?: string;'''

content = content.replace(old_type, new_type)

# 2. Fix the filter logic (lines 107-109)
old_filter = '''const matchesEnriched = filterEnriched === 'all' ||
                (filterEnriched === 'yes' && c.enrichment_status === 'completed') ||
                (filterEnriched === 'no' && c.enrichment_status !== 'completed');'''

new_filter = '''const matchesEnriched = filterEnriched === 'all' ||
                (filterEnriched === 'yes' && (c.enrichment_status === 'completed' || !!c.apex_enrichment_data)) ||
                (filterEnriched === 'no' && c.enrichment_status !== 'completed' && !c.apex_enrichment_data);'''

content = content.replace(old_filter, new_filter)

# 3. Fix the enriched icon display (line 450)
old_icon = '''{c.enrichment_status === 'completed' ? ('''
new_icon = '''{(c.enrichment_status === 'completed' || c.apex_enrichment_data) ? ('''
content = content.replace(old_icon, new_icon)

# 4. Fix the Zap icon displays (lines 529, 603)
old_zap1 = '''{c.enrichment_status === 'completed' && <Zap size={14} className="text-purple-400" />}'''
new_zap1 = '''{(c.enrichment_status === 'completed' || c.apex_enrichment_data) && <Zap size={14} className="text-purple-400" />}'''
content = content.replace(old_zap1, new_zap1)

old_zap2 = '''{c.enrichment_status === 'completed' && <Zap size={12} className="text-purple-400" />}'''
new_zap2 = '''{(c.enrichment_status === 'completed' || c.apex_enrichment_data) && <Zap size={12} className="text-purple-400" />}'''
content = content.replace(old_zap2, new_zap2)

file.write_text(content)
print("✅ Updated enrichment detection to check apex_enrichment_data!")
