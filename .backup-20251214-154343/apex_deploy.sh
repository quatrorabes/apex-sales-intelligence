# Today's Board should show prospects now
curl -s http://localhost:8000/api/todays-board | python3 -c "
import sys,json; d=json.load(sys.stdin)
print(f'Total: {d[\"total_contacts\"]}')
print(f'Hot prospects: {len(d[\"new_prospects\"][\"tiers\"][\"hot\"])}')"

# Pick one contact to test enrichment
sqlite3 apex.db "SELECT id, name, company FROM contacts WHERE enrichment_status='pending' LIMIT 1;"
