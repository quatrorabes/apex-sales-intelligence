# SALES ANGEL - QUICK START GUIDE

## 1. Initial Setup

```bash
# Copy environment template
cp .env.template .env

# Edit .env and add your API keys
nano .env
# Required: OPENAI_API_KEY
# Optional: HUBSPOT_API_KEY
```

## 2. Run Everything (One Command!)

```bash
python orchestrate.py
```

This will:
1. Ask to sync from HubSpot (pulls 500+ contacts)
2. Ask to generate emails/calls
3. Launch the dashboard at http://localhost:8501

## 3. Manual Steps

**Just sync from HubSpot:**
```bash
python hubspot_sync.py
```

**Generate content for enriched contacts:**
```bash
python sales_angel_complete.py --batch 50    # First 50
python sales_angel_complete.py --full        # All contacts
```

**View data without UI:**
```bash
python data_tool.py --stats                  # Show stats
python data_tool.py --export-csv             # Export to CSV
python data_tool.py --export-enhancement     # Full JSON export
```

**Launch dashboard:**
```bash
streamlit run app.py
```

## 4. Dashboard Features

- **Dashboard**: Overview metrics & charts
- **Contacts**: Import, view, enrich contact data
- **Generation**: Preview emails & calls
- **Cadence**: Schedule outreach, track next actions
- **Pipeline**: Track deals, view expected value

## 5. Data Flow

```
HubSpot Contacts
    ↓
Local Database (sales_angel.db)
    ↓
Enrichment (MBTI, DISC, Industry)
    ↓
AI Content Generation
    - 3 email variants
    - 3 call variants
    ↓
Dashboard Review & Tracking
    - Accept/reject variants
    - Set outreach cadence
    - Track deals & pipeline
    ↓
Write Back to HubSpot
```

## 6. Files Overview

| File | Purpose |
|------|---------|
| `orchestrate.py` | Master workflow (start here!) |
| `hubspot_sync.py` | Sync contacts from HubSpot |
| `sales_angel_complete.py` | Generate emails & calls |
| `data_tool.py` | View raw data (CLI) |
| `app.py` | Interactive dashboard (Streamlit) |
| `sales_angel.db` | SQLite database (all data) |

## 7. Troubleshooting

**HubSpot sync failing?**
- Check HUBSPOT_API_KEY in .env
- Get key: https://app.hubspot.com/l/api-keys/

**No content generating?**
- Check OPENAI_API_KEY in .env
- Ensure you have OpenAI credits

**Dashboard not showing data?**
- Run: `python sales_angel_complete.py --batch 5`
- Refresh dashboard browser page

## 8. API Key Setup

### OpenAI (Required)
1. Go to: https://platform.openai.com/api-keys
2. Create new key
3. Add to .env: `OPENAI_API_KEY=sk-...`

### HubSpot (Optional)
1. Go to: https://app.hubspot.com/l/api-keys/
2. Copy existing or create new key
3. Add to .env: `HUBSPOT_API_KEY=pat-na2-...`

## Support

**Run individual tools:**
```bash
python hubspot_sync.py          # Just sync
python sales_angel_complete.py  # Just generate
streamlit run app.py             # Just dashboard
```

**Check your data:**
```bash
sqlite3 sales_angel.db "SELECT COUNT(*) FROM contacts;"
```

**Start fresh:**
```bash
rm sales_angel.db
python orchestrate.py
```

---
**Version 1.0** | Harvest Small Business Finance
