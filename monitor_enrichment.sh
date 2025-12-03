#!/bin/bash

while true; do
    clear
    echo "🔍 ENRICHMENT PROGRESS"
    echo "=========================================================="
    echo ""
    
    sqlite3 apex.db << 'SQL'
.mode column
.headers on

SELECT 
    enrichment_status as Status,
    COUNT(*) as Count,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM contacts WHERE linkedin_url IS NOT NULL), 1) as '% of LinkedIn'
FROM contacts
WHERE linkedin_url IS NOT NULL
GROUP BY enrichment_status
ORDER BY 
    CASE enrichment_status
        WHEN 'completed' THEN 1
        WHEN 'pending' THEN 2
        WHEN 'in_progress' THEN 3
        ELSE 4
    END;
SQL
    
    echo ""
    echo "Last 5 enriched:"
    sqlite3 apex.db "SELECT name, company FROM contacts WHERE enrichment_status = 'completed' ORDER BY updated_at DESC LIMIT 5;"
    
    echo ""
    echo "Refreshing every 30 seconds... (Ctrl+C to stop)"
    sleep 30
done
