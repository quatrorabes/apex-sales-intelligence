#!/bin/bash
# Identify enriched contact and check data format

echo "========================================================================"
echo "ENRICHMENT DATA INVESTIGATION"
echo "========================================================================"
echo ""

echo "1. Who is contact f6e4e0f2-0597-47a2-b4f5-869fa94b6a12?"
echo "------------------------------------------------------------"
psql $DATABASE_URL -c "SELECT id, name, title, company, enrichment_status, enriched_at FROM contacts WHERE id = 'f6e4e0f2-0597-47a2-b4f5-869fa94b6a12';"
echo ""

echo "2. What does the enrichment_data look like?"
echo "------------------------------------------------------------"
psql $DATABASE_URL -c "SELECT jsonb_pretty(enrichment_data) FROM contacts WHERE id = 'f6e4e0f2-0597-47a2-b4f5-869fa94b6a12';" | head -50
echo ""

echo "3. Is it the right format for the Dashboard?"
echo "------------------------------------------------------------"
psql $DATABASE_URL -c "SELECT 
  id,
  name,
  enrichment_data->>'sections' as has_sections,
  enrichment_data->>'metadata' as has_metadata,
  jsonb_typeof(enrichment_data->'sections') as sections_type
FROM contacts 
WHERE id = 'f6e4e0f2-0597-47a2-b4f5-869fa94b6a12';"
echo ""

echo "4. What about Anna O'Brien and Marco Chan?"
echo "------------------------------------------------------------"
psql $DATABASE_URL -c "SELECT id, name, enrichment_status FROM contacts WHERE name ILIKE '%anna%' OR name ILIKE '%obrien%' OR name ILIKE '%marco%' OR name ILIKE '%chan%';"
echo ""

echo "========================================================================"
echo "NEXT: View the actual enrichment output"
echo "========================================================================"
echo "cat /tmp/apex_debug/contact_f6e4e0f2-0597-47a2-b4f5-869fa94b6a12_02_perplexity_openai_20251217_025946.txt"
