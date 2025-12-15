# Sales Angel - Pipeline, Cadence & Activity Tracking System

## 🎯 Overview

This upgrade adds complete **sales funnel management**, **automated cadence sequences**, and **enhanced activity tracking** to Sales Angel. Transform your enriched contacts into a full-featured CRM with pipeline forecasting, automated touchpoint scheduling, and engagement analytics.

---

## 📦 What's New

### ✅ Phase 1 Complete: Data Foundation

**4 New Database Tables:**
- `pipeline_stages` - Track contacts through sales funnel
- `cadences` - Define reusable outreach sequences  
- `cadence_steps` - Individual touchpoints in each sequence
- `contact_cadence_assignments` - Link contacts to active cadences

**Enhanced Existing Table:**
- `outreach_activities` - Added 7 new columns for cadence tracking, engagement scoring, and next action recommendations

**5 New Python Modules:**
1. `upgrade_db_pipeline.py` - Database migration script
2. `pipeline_manager.py` - Sales funnel management
3. `cadence_engine.py` - Automated sequence orchestration
4. `activity_tracker_v2.py` - Enhanced activity logging
5. `test_complete_system.py` - Comprehensive testing suite

---

## 🚀 Quick Start

### Step 1: Backup Your Database

```bash
# Automatic backup is included in upgrade script
# But you can manually backup first for safety
cp sales_angel.db sales_angel_manual_backup.db
```

### Step 2: Run Database Upgrade

```bash
python upgrade_db_pipeline.py
```

**Expected Output:**
```
✅ Backup created: sales_angel_backup_20251111_120000.db
🔧 Starting database upgrade...
📊 Creating pipeline_stages table...
✅ pipeline_stages table created
📅 Creating cadences table...
✅ cadences table created
🎯 Creating default cadences...
✅ Default cadences created
🔄 Auto-assigning pipeline stages to existing contacts...
✅ Assigned 387 contacts to pipeline stages

DATABASE UPGRADE COMPLETE!
```

### Step 3: Test the System

```bash
python test_complete_system.py
```

This runs comprehensive tests on all new functionality and shows you:
- Current pipeline distribution
- Available cadences and scheduled activities
- Response rates and engagement metrics
- 30-day forecast
- Integration workflow demonstration

### Step 4: Start Using It!

```python
# Example: Move contact through pipeline
from pipeline_manager import move_to_stage
move_to_stage(contact_id=123, new_stage="qualified", expected_value=50000)

# Example: Auto-assign cadence based on MDCP score
from cadence_engine import auto_assign_cadence_by_mdcp
auto_assign_cadence_by_mdcp(contact_id=123)

# Example: Log an activity
from activity_tracker_v2 import log_activity
log_activity(
    contact_id=123,
    activity_type="email",
    content_used="Email Template 1 - Introduction",
    engagement_score=75,
    response_type="positive"
)
```

---

## 📊 Pipeline Management

### Stage Definitions

| Stage | Probability | Description |
|-------|------------|-------------|
| **New** | 10% | Fresh lead, not yet contacted |
| **Contacted** | 25% | Initial outreach completed |
| **Qualified** | 50% | Qualified as good fit, engaged |
| **Proposal** | 70% | Proposal or demo delivered |
| **Negotiation** | 85% | Actively negotiating terms |
| **Closed Won** | 100% | Deal closed successfully |
| **Closed Lost** | 0% | Deal lost |
| **Nurture** | 5% | Long-term nurture campaign |

### Key Functions

```python
from pipeline_manager import *

# Get complete pipeline summary
summary = get_pipeline_summary()
# Returns: stage counts, values, conversion rates, win/loss metrics

# Move contact to new stage
move_to_stage(
    contact_id=123,
    new_stage="proposal",
    expected_value=75000,
    notes="Sent proposal after successful demo"
)

# Get contact's current stage
current = get_current_stage(contact_id=123)

# Get all contacts in a specific stage
contacts = get_contacts_by_stage("qualified")

# Forecast pipeline for next 30 days
forecast = forecast_pipeline(days_ahead=30)
# Returns: expected revenue, weighted revenue, top deals

# Get stage history for contact
history = get_contact_stage_history(contact_id=123)
```

---

## 📅 Cadence System

### Default Cadences

#### 🔥 Hot Lead - 7 Day Blitz (MDCP 80-100)
Aggressive 7-touch sequence for highest-value leads:
- **Day 0**: Email 1 - Introduction with intelligence
- **Day 1**: LinkedIn - Connection request
- **Day 3**: Email 2 - Value-add with industry insights
- **Day 4**: Call - Discovery call (Script 1)
- **Day 5**: Email 3 - Resource share and case study
- **Day 6**: LinkedIn - Follow-up message
- **Day 7**: Call - Breakup call (Script 2)

#### 🟠 Warm Lead - 14 Day Nurture (MDCP 60-79)
Balanced 5-touch sequence:
- **Day 0**: Email 1 - Introduction
- **Day 3**: LinkedIn - Connection
- **Day 7**: Email 2 - Value proposition
- **Day 10**: Call - Exploratory call
- **Day 14**: Email 3 - Follow-up with resources

#### 🟡 Qualified Lead - 30 Day Long Game (MDCP 40-59)
Patient 4-touch sequence:
- **Day 0**: Email 1 - Soft introduction
- **Day 7**: LinkedIn - Connection
- **Day 14**: Email 2 - Educational content
- **Day 30**: Call - Check-in call

#### ⚪ Cold Lead - 60 Day Slow Burn (MDCP <40)
Minimal 3-touch sequence:
- **Day 0**: Email 1 - Generic introduction
- **Day 30**: Email 2 - Value proposition
- **Day 60**: LinkedIn - Connection attempt

### Key Functions

```python
from cadence_engine import *

# List all available cadences
cadences = get_all_cadences()

# Auto-assign cadence based on MDCP score
auto_assign_cadence_by_mdcp(contact_id=123)
# Automatically selects: hot/warm/qualified/cold based on score

# Manually assign specific cadence
assign_cadence(
    contact_id=123,
    cadence_id=1,  # Hot Lead - 7 Day Blitz
    start_date="2025-11-12"  # Optional, defaults to today
)

# Get today's scheduled activities
activities = get_scheduled_activities()  # Defaults to today
activities = get_scheduled_activities("2025-11-15")  # Specific date

# Complete an activity
complete_activity(
    activity_id=456,
    engagement_score=80,
    response_type="positive"
)

# Check cadence status for contact
status = get_contact_cadence_status(contact_id=123)
# Returns: cadence name, progress, completion rate

# Pause/resume cadences
pause_cadence(contact_id=123)
resume_cadence(contact_id=123)

# Get detailed steps for a cadence
steps = get_cadence_steps(cadence_id=1)
```

---

## 📈 Activity Tracking

### Enhanced Features

- **Engagement Scoring**: Rate each activity 0-100 based on prospect engagement
- **Response Types**: Classify responses as positive, neutral, negative, or no_response
- **Next Action Recommendations**: System automatically suggests next steps
- **Cadence Integration**: Activities linked to cadence steps for progress tracking
- **Timeline View**: Complete activity history per contact
- **Analytics**: Response rates, engagement trends, effectiveness metrics

### Key Functions

```python
from activity_tracker_v2 import *

# Log a new activity
activity_id = log_activity(
    contact_id=123,
    activity_type="email",  # email, call, linkedin, meeting
    content_used="Email Template 1 - Introduction",
    engagement_score=75,
    response_type="positive",
    notes="Prospect very interested, asked for demo"
)

# Get activity timeline for contact
timeline = get_activity_timeline(contact_id=123, limit=50)

# Get overall response rates
rates = get_response_rates()
# Returns: overall response rate, positive rate, breakdown by activity type

# Get upcoming next actions
upcoming = get_next_actions_due(days_ahead=7)
# Returns: all contacts with actions due in next 7 days

# Get activity stats for contact
stats = get_contact_activity_stats(contact_id=123)
# Returns: total activities, response rate, avg engagement, breakdown by type

# Bulk log activities (useful for imports)
activities = [
    {"contact_id": 123, "activity_type": "email", "engagement_score": 70},
    {"contact_id": 124, "activity_type": "call", "response_type": "positive"}
]
count = bulk_log_activities(activities)
```

---

## 🔗 Integration with Existing System

### Workflow Integration

Your existing Sales Angel system (enrichment + content generation) now flows seamlessly into the new pipeline:

```
1. HubSpot Contact → 2. Perplexity Enrichment → 3. OpenAI Content → 4. PIPELINE ENTRY (NEW)
                                                                           ↓
5. Auto-assign Cadence (based on MDCP) → 6. Schedule Activities → 7. Track Engagement
                                                                           ↓
8. Move through Pipeline Stages ← 9. Next Action Recommendations ← 10. Log Activities
```

### Example: Complete Flow

```python
# After enriching a contact with Sales Angel...

# 1. Contact automatically enters "new" pipeline stage during enrichment
# (This happens in upgrade_db_pipeline.py)

# 2. Auto-assign cadence based on MDCP score
from cadence_engine import auto_assign_cadence_by_mdcp
auto_assign_cadence_by_mdcp(contact_id=contact_id)

# 3. Cadence engine schedules all activities automatically

# 4. Get today's scheduled activities
from cadence_engine import get_scheduled_activities
today_activities = get_scheduled_activities()

# 5. When you complete an activity, log it
from activity_tracker_v2 import log_activity
log_activity(
    contact_id=contact_id,
    activity_type="email",
    content_used="Used Email Template 1",
    engagement_score=80,
    response_type="positive"
)

# 6. Based on engagement, move to next pipeline stage
from pipeline_manager import move_to_stage
if response_type == "positive":
    move_to_stage(contact_id, "qualified", expected_value=50000)

# 7. System automatically recommends next action!
```

---

## 📊 Database Schema Reference

### pipeline_stages

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER PK | Unique stage record ID |
| contact_id | INTEGER FK | Link to contacts table |
| stage | TEXT | Current stage (new, contacted, qualified, etc.) |
| entered_at | TEXT | When contact entered this stage |
| exited_at | TEXT | When contact left this stage (NULL if current) |
| duration_days | INTEGER | Days spent in this stage |
| probability | INTEGER | Close probability 0-100% |
| expected_value | REAL | Expected deal value |
| notes | TEXT | Stage transition notes |

### cadences

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER PK | Unique cadence ID |
| name | TEXT | Cadence name |
| description | TEXT | Cadence description |
| mdcp_tier | TEXT | Target tier (hot, warm, qualified, cold) |
| total_touches | INTEGER | Total number of touchpoints |
| duration_days | INTEGER | Total duration in days |
| active | INTEGER | 1 = active, 0 = inactive |

### cadence_steps

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER PK | Unique step ID |
| cadence_id | INTEGER FK | Link to cadences table |
| step_number | INTEGER | Step sequence number |
| day_offset | INTEGER | Days from cadence start |
| activity_type | TEXT | email, call, linkedin, meeting |
| template_type | TEXT | Template identifier |
| priority | TEXT | high, medium, low |
| description | TEXT | Step description |

### contact_cadence_assignments

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER PK | Unique assignment ID |
| contact_id | INTEGER FK | Link to contacts table |
| cadence_id | INTEGER FK | Link to cadences table |
| assigned_date | TEXT | When cadence was assigned |
| start_date | TEXT | When cadence starts |
| current_step | INTEGER | Current step number |
| status | TEXT | active, paused, completed, stopped |
| completion_rate | REAL | Progress 0.0-1.0 |
| last_activity_date | TEXT | Last completed activity |

### outreach_activities (Enhanced)

**New columns added:**

| Column | Type | Description |
|--------|------|-------------|
| cadence_step_id | INTEGER FK | Link to cadence_steps (if part of cadence) |
| scheduled_date | TEXT | When activity is scheduled |
| completed | INTEGER | 1 = done, 0 = pending |
| engagement_score | INTEGER | 0-100 engagement rating |
| response_type | TEXT | positive, neutral, negative, no_response |
| next_action | TEXT | Recommended next action |
| next_action_date | TEXT | When to take next action |

---

## 🎨 Dashboard Integration (Next Phase)

These modules are designed to power a dashboard with:

### Top Metrics Cards
- Total Pipeline Value
- Weighted Pipeline (risk-adjusted)
- Active Cadences
- Win Rate %
- Avg Sales Cycle

### Visualizations
- **Pipeline Funnel**: Stage-by-stage visualization with conversion rates
- **Cadence Progress**: Visual progress bars per contact
- **Activity Feed**: Real-time stream of recent activities
- **Response Rate Charts**: Effectiveness by activity type
- **Forecast Dashboard**: 30/60/90 day revenue projections

### Interactive Features
- Click contact → View full intelligence + activity timeline
- Drag-and-drop contacts between pipeline stages
- One-click cadence assignment
- Quick activity logging
- Today's action list (scheduled activities)

---

## 🔍 Troubleshooting

### Issue: Database upgrade fails

**Solution:**
```bash
# Check if sales_angel.db exists in current directory
ls -la sales_angel.db

# If missing, check your working directory
pwd

# Make sure you're in the same directory as sales_angel.db
cd /path/to/sales-angel-clean/
python upgrade_db_pipeline.py
```

### Issue: Import errors in test script

**Solution:**
```bash
# Make sure all .py files are in same directory
ls -la *.py

# Should see:
# - upgrade_db_pipeline.py
# - pipeline_manager.py
# - cadence_engine.py
# - activity_tracker_v2.py
# - test_complete_system.py
```

### Issue: No activities scheduled

**Solution:**
```python
# Manually assign a cadence to a contact
from cadence_engine import auto_assign_cadence_by_mdcp

# Get a contact ID from your database
import sqlite3
conn = sqlite3.connect("sales_angel.db")
cursor = conn.cursor()
cursor.execute("SELECT id FROM contacts LIMIT 1")
contact_id = cursor.fetchone()[0]
conn.close()

# Assign cadence
auto_assign_cadence_by_mdcp(contact_id)

# Now check scheduled activities
from cadence_engine import get_scheduled_activities
activities = get_scheduled_activities()
print(f"Found {len(activities)} scheduled activities")
```

---

## 📚 Best Practices

### 1. Pipeline Stage Movement
- Always provide `expected_value` when moving to proposal or later stages
- Add notes explaining why contact moved to new stage
- Review contacts stuck in stages >30 days

### 2. Cadence Management
- Let auto-assignment handle most cases (based on MDCP)
- Manually assign custom cadences only for special situations
- Pause cadences if contact goes cold, don't delete
- Mark as "completed" only when all steps done or deal closed

### 3. Activity Logging
- **Always** log activities with engagement scores
- Use response_type consistently:
  - `positive`: Interested, wants to learn more, asked questions
  - `neutral`: Acknowledged but non-committal
  - `negative`: Not interested, asked to remove
  - `no_response`: No reply/response received
- Add notes for context on important interactions

### 4. Data Quality
- Review pipeline summary weekly
- Check for contacts in wrong stages
- Validate cadence completion rates
- Monitor response rate trends

---

## 🚀 Next Steps

### Immediate (This Session)
1. ✅ Database schema complete
2. ✅ Core modules built
3. ✅ Testing suite ready
4. ⏳ **Next: Build dashboard UI**

### Short-term (Next Session)
5. ⏳ API endpoints for dashboard
6. ⏳ Real-time activity feed
7. ⏳ Interactive pipeline visualization
8. ⏳ Notion integration

### Future Enhancements
- Email integration (Gmail/Outlook sync)
- Call recording integration
- AI-powered next action recommendations
- Predictive scoring for close probability
- Team collaboration features
- Mobile app

---

## 📄 File Summary

| File | Purpose | Lines | Status |
|------|---------|-------|--------|
| `upgrade_db_pipeline.py` | Database migration | ~400 | ✅ Complete |
| `pipeline_manager.py` | Sales funnel logic | ~350 | ✅ Complete |
| `cadence_engine.py` | Sequence automation | ~450 | ✅ Complete |
| `activity_tracker_v2.py` | Activity management | ~400 | ✅ Complete |
| `test_complete_system.py` | Testing suite | ~350 | ✅ Complete |
| **Total** | **Data Foundation** | **~1,950** | **✅ Ready** |

---

## 💡 Pro Tips

1. **Run tests regularly** - `python test_complete_system.py` gives you instant health check

2. **Start with auto-assignment** - Let the system assign cadences based on MDCP, then adjust manually only if needed

3. **Use engagement scores consistently** - Develop your own scale (e.g., 80+ = very interested, 50-79 = moderate, <50 = low interest)

4. **Review forecast weekly** - `forecast_pipeline()` helps you stay on top of expected revenue

5. **Monitor response rates** - If response rates drop, adjust cadence timing or content

---

## 🎉 Success Criteria

You'll know the system is working when:

- ✅ All 387 contacts have pipeline stages assigned
- ✅ Default cadences created (4 cadences with 19 total steps)
- ✅ Activities scheduled for contacts with active cadences
- ✅ Pipeline summary shows accurate stage distribution
- ✅ Response rate tracking shows historical data
- ✅ Forecast generates weighted revenue projections

---

## 📞 Support

**Questions? Issues?**

1. Run `python test_complete_system.py` and review output
2. Check database with: `sqlite3 sales_angel.db "SELECT COUNT(*) FROM [table_name]"`
3. Review backup files in case rollback needed

**All tests passing? You're ready to build the dashboard! 🚀**

---

*Sales Angel - Data Foundation v1.0*  
*Built: November 11, 2025*  
*Ready for Dashboard Integration*
