#!/bin/bash
# Diagnose enrichment display issues

echo "========================================================================"
echo "APEX ENRICHMENT DIAGNOSTIC"
echo "========================================================================"
echo ""

echo "Step 1: Check what was actually enriched"
echo "----------------------------------------"
echo "Run this query to see the last enriched contact:"
echo ""
echo 'psql $DATABASE_URL -c "SELECT id, name, enrichment_status, enriched_at FROM contacts WHERE enrichment_status = '"'"'completed'"'"' ORDER BY enriched_at DESC LIMIT 1;"'
echo ""

echo "Step 2: Check the enrichment_data format"
echo "----------------------------------------"
echo "Run this to see the actual data structure:"
echo ""
echo 'psql $DATABASE_URL -c "SELECT id, name, jsonb_pretty(enrichment_data) FROM contacts WHERE enrichment_status = '"'"'completed'"'"' ORDER BY enriched_at DESC LIMIT 1;"'
echo ""

echo "Step 3: Check debug files for the UUID you THOUGHT you selected"
echo "----------------------------------------------------------------"
echo "In Render Shell, run:"
echo "  ls -lh /tmp/apex_debug/ | tail -10"
echo "  # Look for files with the contact UUID you clicked"
echo ""

echo "========================================================================"
echo "TELL ME:"
echo "1. Which contact did you CLICK on? (name and UUID from Dashboard)"
echo "2. Which contact got enriched? (from Step 1 query)"
echo "3. What does the enrichment_data look like? (from Step 2 query)"
echo "========================================================================"
