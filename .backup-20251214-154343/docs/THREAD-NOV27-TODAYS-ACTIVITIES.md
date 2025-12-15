

# APEX DASHBOARD DEBUGGING GUIDE
## Session: November 28, 2025

---

## CRITICAL ISSUE #1: App.tsx Syntax Errors

### Problem
Vite/Babel reports "Unexpected token" at line 274:5 pointing to a closing `</div>` tag.

### Root Cause
- Unclosed JSX element above line 274
- Missing opening tag or extra closing tag
- Common pattern: duplicate closing braces `)}` causing structure mismatch

### Solution
Check lines 260-280 in `/Users/chrisrabenold/projects/apex/dashboard_v1/src/App.tsx`:
```bash
cd /Users/chrisrabenold/projects/apex
sed -n '260,280p' dashboard_v1/src/App.tsx
```

Look for:
1. Missing opening `<div>` that matches the closing `</div>` on line 274
2. Duplicate `)}` closures
3. Unclosed conditional rendering blocks

---

## CRITICAL ISSUE #2: Duplicate Import Declarations

### Error Message
```
Identifier 'ChevronUp' has already been declared. (9:9)
```

### Root Cause
Two separate `import { ... } from 'lucide-react';` statements in App.tsx

### Solution
Replace ALL lucide-react imports with a SINGLE merged import:

```tsx
import React, { useState, useEffect } from 'react';
import {
  ChevronUp, ChevronDown, Search, Download, Users, Gauge,
  Activity, Sparkles, Database, Target, ChevronLeft, ChevronRight, Zap
} from 'lucide-react';
import ApexIntelligence from './components/ApexIntelligence';
import CadenceDashboard from './components/CadenceDashboard';
import ContactEnrichmentView from './components/ContactEnrichmentView';
import RawDataViewer from './components/RawDataViewer';
import ContactDetailModal from './components/ContactDetailModal';
import WhyMeTab from './components/WhyMeTab';
import TodaysBoard from './components/TodaysBoard';

type MainTabId = 'board' | 'contacts' | 'cadence' | 'enrichment' | 'raw' | 'whyme';
```

---

## CRITICAL ISSUE #3: Missing Database Column

### Error Message
```json
{"error": "no such column: last_contact_date", "success": false}
```

### Root Cause
The `last_contact_date` column doesn't exist in the `contacts` table but is referenced by the Today's Board API endpoint.

### Solution
Run this SQL command to add the missing column:
```bash
cd /Users/chrisrabenold/projects/apex
sqlite3 apex.db "ALTER TABLE contacts ADD COLUMN last_contact_date TEXT;"
```

### Verify
```bash
sqlite3 apex.db "PRAGMA table_info(contacts);" | grep last_contact
```

### Seed Test Data (Optional)
```sql
-- Recent contacts (15 days ago)
UPDATE contacts SET last_contact_date = date('now', '-15 days') WHERE id IN (SELECT id FROM contacts LIMIT 3);

-- 6 months ago contacts
UPDATE contacts SET last_contact_date = date('now', '-180 days') WHERE id IN (SELECT id FROM contacts LIMIT 3 OFFSET 3);

-- Over a year ago (urgent)
UPDATE contacts SET last_contact_date = date('now', '-400 days') WHERE id IN (SELECT id FROM contacts LIMIT 3 OFFSET 6);

-- Leave rest as NULL for "new prospects"
```

---

## PHASE 2: DATABASE SCHEMA UPDATES

Add these tables for activity logging and opportunity signals:

```bash
cd /Users/chrisrabenold/projects/apex
sqlite3 apex.db <<'EOF'
-- Activity Logging Table
CREATE TABLE IF NOT EXISTS contact_activities (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  contact_id INTEGER NOT NULL,
  activity_type TEXT NOT NULL,  -- 'call', 'email', 'linkedin', 'meeting'
  activity_date TEXT NOT NULL,
  direction TEXT,               -- 'inbound' or 'outbound'
  subject TEXT,
  notes TEXT,
  outcome TEXT,                 -- 'connected', 'voicemail', 'email_sent', etc.
  created_at TEXT DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (contact_id) REFERENCES contacts(id)
);

-- Opportunity Signals Table
CREATE TABLE IF NOT EXISTS opportunity_signals (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  contact_id INTEGER NOT NULL,
  signal_type TEXT NOT NULL,    -- 'job_change', 'linkedin_post', 'company_news', 'funding'
  signal_date TEXT NOT NULL,
  signal_data TEXT,             -- JSON blob with details
  urgency_boost INTEGER DEFAULT 0,
  viewed INTEGER DEFAULT 0,
  created_at TEXT DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (contact_id) REFERENCES contacts(id)
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_activities_contact ON contact_activities(contact_id);
CREATE INDEX IF NOT EXISTS idx_activities_date ON contact_activities(activity_date);
CREATE INDEX IF NOT EXISTS idx_signals_contact ON opportunity_signals(contact_id);
CREATE INDEX IF NOT EXISTS idx_signals_viewed ON opportunity_signals(viewed);

-- Add signal tracking columns to contacts
ALTER TABLE contacts ADD COLUMN linkedin_activity_detected INTEGER DEFAULT 0;
ALTER TABLE contacts ADD COLUMN company_news_detected INTEGER DEFAULT 0;
ALTER TABLE contacts ADD COLUMN last_signal_date TEXT;
ALTER TABLE contacts ADD COLUMN signal_count INTEGER DEFAULT 0;
EOF
```

---

## API ROUTES TO ADD (api.py)

### Activity Logging Endpoints

```python
# ============= ACTIVITY LOGGING ENDPOINTS =============

@app.route('/api/activities/log', methods=['POST'])
def log_activity():
    """Log a contact activity (call, email, meeting)"""
    try:
        data = request.json
        contact_id = data.get('contact_id')
        activity_type = data.get('activity_type')  # call, email, linkedin, meeting
        activity_date = data.get('activity_date', datetime.now().isoformat())
        direction = data.get('direction', 'outbound')
        subject = data.get('subject', '')
        notes = data.get('notes', '')
        outcome = data.get('outcome', '')

        if not contact_id or not activity_type:
            return jsonify({'success': False, 'error': 'contact_id and activity_type required'}), 400

        conn = get_db()
        cursor = conn.cursor()

        # Insert activity
        cursor.execute("""
            INSERT INTO contact_activities 
            (contact_id, activity_type, activity_date, direction, subject, notes, outcome)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (contact_id, activity_type, activity_date, direction, subject, notes, outcome))

        # Update last_contact_date on contact
        cursor.execute("""
            UPDATE contacts SET last_contact_date = ? WHERE id = ?
        """, (activity_date.split('T')[0], contact_id))

        conn.commit()

        return jsonify({
            'success': True,
            'activity_id': cursor.lastrowid,
            'message': f'{activity_type.title()} logged successfully'
        })
    except Exception as e:
        logger.error(f"Activity logging error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/activities/<int:contact_id>', methods=['GET'])
def get_contact_activities(contact_id):
    """Get activity timeline for a contact"""
    try:
        conn = get_db()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, activity_type, activity_date, direction, subject, notes, outcome, created_at
            FROM contact_activities
            WHERE contact_id = ?
            ORDER BY activity_date DESC
            LIMIT 50
        """, (contact_id,))

        activities = [dict(row) for row in cursor.fetchall()]

        return jsonify({
            'success': True,
            'contact_id': contact_id,
            'activities': activities,
            'total': len(activities)
        })
    except Exception as e:
        logger.error(f"Get activities error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500
```

### Opportunity Signals Endpoints

```python
# ============= OPPORTUNITY SIGNALS ENDPOINTS =============

@app.route('/api/signals/unread', methods=['GET'])
def get_unread_signals():
    """Get all unread opportunity signals"""
    try:
        conn = get_db()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT 
                s.id, s.contact_id, s.signal_type, s.signal_date,
                s.signal_data, s.urgency_boost,
                c.name, c.company, c.title, c.priority_score
            FROM opportunity_signals s
            JOIN contacts c ON s.contact_id = c.id
            WHERE s.viewed = 0
            ORDER BY s.signal_date DESC, s.urgency_boost DESC
            LIMIT 20
        """)

        signals = [dict(row) for row in cursor.fetchall()]

        return jsonify({
            'success': True,
            'signals': signals,
            'total': len(signals)
        })
    except Exception as e:
        logger.error(f"Get signals error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/signals/mark-read/<int:signal_id>', methods=['POST'])
def mark_signal_read(signal_id):
    """Mark a signal as viewed"""
    try:
        conn = get_db()
        cursor = conn.cursor()

        cursor.execute("UPDATE opportunity_signals SET viewed = 1 WHERE id = ?", (signal_id,))
        conn.commit()

        return jsonify({'success': True, 'message': 'Signal marked as read'})
    except Exception as e:
        logger.error(f"Mark signal read error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500
```

---

## QUICK REFERENCE COMMANDS

### Start Backend
```bash
cd /Users/chrisrabenold/projects/apex
python api.py
```

### Start Frontend
```bash
cd /Users/chrisrabenold/projects/apex/dashboard_v1
npm run dev
```

### Access Dashboard
```
http://localhost:5173
```

### Git Operations
```bash
# Restore App.tsx from last commit
git checkout dashboard_v1/src/App.tsx

# Use backup
cp App.tsx.backup App.tsx
```

---

## TODAY'S BOARD URGENCY TIERS

| Tier | Days Since Contact | Urgency Score |
|------|-------------------|---------------|
| ðŸ”¥ Urgent | 365+ days | 95-100 |
| â° Warm | 180-365 days | 80-94 |
| ðŸ’Ž Nurture | 90-180 days | 60-79 |
| ðŸ“Š Stable | <90 days | 0-59 |
| ðŸŽ¯ New Prospect | Never contacted | Based on ICP match |

---

## FILE LOCATIONS

- **App.tsx**: `/Users/chrisrabenold/projects/apex/dashboard_v1/src/App.tsx`
- **api.py**: `/Users/chrisrabenold/projects/apex/api.py`
- **Database**: `/Users/chrisrabenold/projects/apex/apex.db`
- **TodaysBoard**: `/Users/chrisrabenold/projects/apex/dashboard_v1/src/components/TodaysBoard.tsx`
- **ContactDetailModal**: `/Users/chrisrabenold/projects/apex/dashboard_v1/src/components/ContactDetailModal.tsx`

---

## WORKING COMPONENTS (DO NOT TOUCH)
- ContactDetailModal.tsx âœ…
- Enrichment flow âœ…
- Content generation (email/call/LinkedIn) âœ…
- Intelligence/Dossier/Outreach tabs âœ…

---

Generated: November 28, 2025
