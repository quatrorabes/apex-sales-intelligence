# DASHBOARD FIX - IMMEDIATE ACTION PLAN
**Status:** Ready to Execute  
**Time:** 2-3 hours  
**Priority:** CRITICAL - Foundation for everything else

---

## 🎯 OBJECTIVE

Fix the `premium_dashboard.py` Streamlit dashboard to properly display:
1. **Text colors** - Make content readable and professional
2. **Component positioning** - Proper layout and alignment
3. **Data display** - Show generated intelligence, emails, call scripts
4. **Working UI** - Foundation for plugging in enhancements

---

## 📋 CURRENT STATE (From Last Night's Session)

### What Works:
- ✅ `sales_angel_PREMIUM.py` - Intelligence engine working
- ✅ `sales_angel.db` - SQLite database with data
- ✅ Contact intelligence generation (0.6 seconds)
- ✅ 3 email variants + 3 call scripts generated
- ✅ Cadence assignment and scheduling
- ✅ Database schema complete

### What's Broken in Dashboard:
- ❌ Text colors not visible (white text on white background?)
- ❌ Component positioning off (elements overlapping/misaligned?)
- ❌ Missing data display (only "Talking Points" header shows)
- ❌ No template selection interface
- ❌ No enrichment data visible
- ❌ No confidence scoring display

---

## 🔧 IMMEDIATE FIXES NEEDED

### 1. **Fix Text Color & Styling** (30 minutes)

**Problem:** Text not visible or poorly contrasted

**Solution:**
```python
# Add to premium_dashboard.py

import streamlit as st

# Set page config with dark theme
st.set_page_config(
    page_title="Sales Angel Dashboard",
    page_icon="📞",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better visibility
st.markdown("""
<style>
    /* Main content text */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    
    /* Headers */
    h1, h2, h3 {
        color: #1f2937 !important;
        font-weight: 600 !important;
    }
    
    /* Text content */
    p, div, span {
        color: #374151 !important;
    }
    
    /* Metric values */
    [data-testid="stMetricValue"] {
        color: #059669 !important;
        font-size: 2rem !important;
        font-weight: 700 !important;
    }
    
    /* Metric labels */
    [data-testid="stMetricLabel"] {
        color: #6b7280 !important;
        font-size: 0.875rem !important;
        font-weight: 500 !important;
    }
    
    /* Cards/containers */
    .stCard {
        background-color: #ffffff !important;
        border: 1px solid #e5e7eb !important;
        border-radius: 0.5rem !important;
        padding: 1.5rem !important;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1) !important;
    }
    
    /* Buttons */
    .stButton > button {
        background-color: #2563eb !important;
        color: white !important;
        font-weight: 600 !important;
        border-radius: 0.375rem !important;
        padding: 0.5rem 1rem !important;
        border: none !important;
    }
    
    .stButton > button:hover {
        background-color: #1d4ed8 !important;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #f9fafb !important;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 1rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        color: #6b7280 !important;
        font-weight: 600 !important;
    }
    
    .stTabs [aria-selected="true"] {
        color: #2563eb !important;
        border-bottom-color: #2563eb !important;
    }
</style>
""", unsafe_allow_html=True)
```

---

### 2. **Fix Component Layout & Positioning** (45 minutes)

**Problem:** Components misaligned, overlapping, or poorly organized

**Solution - New Dashboard Structure:**

```python
import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

def main():
    st.title("📞 Sales Angel Intelligence Dashboard")
    
    # ===== SIDEBAR =====
    with st.sidebar:
        st.header("🎯 Quick Actions")
        
        # Contact selector
        contacts = get_all_contacts()
        selected_contact = st.selectbox(
            "Select Contact",
            options=contacts['id'].tolist(),
            format_func=lambda x: get_contact_name(x)
        )
        
        st.divider()
        
        # Action buttons
        if st.button("🔄 Generate Intelligence", use_container_width=True):
            generate_intelligence(selected_contact)
            st.success("Intelligence generated!")
            st.rerun()
        
        if st.button("📧 View Emails", use_container_width=True):
            st.session_state.view = "emails"
        
        if st.button("☎️ View Call Scripts", use_container_width=True):
            st.session_state.view = "calls"
        
        st.divider()
        
        # Stats
        st.metric("Total Contacts", len(contacts))
        st.metric("Enriched Today", get_today_enrichment_count())
        st.metric("Pending Touchpoints", get_pending_touchpoints_count())
    
    # ===== MAIN CONTENT =====
    
    # Top metrics row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Hot Leads (85+)",
            value=get_hot_leads_count(),
            delta="+3 this week"
        )
    
    with col2:
        st.metric(
            label="Avg Score",
            value=f"{get_avg_score():.1f}",
            delta="+2.3"
        )
    
    with col3:
        st.metric(
            label="Today's Calls",
            value=get_todays_calls_count(),
            delta="5 remaining"
        )
    
    with col4:
        st.metric(
            label="This Week",
            value=f"{get_week_touchpoints()}",
            delta="+12%"
        )
    
    st.divider()
    
    # Contact Intelligence Display
    if selected_contact:
        display_contact_intelligence(selected_contact)

def display_contact_intelligence(contact_id):
    """Display full intelligence for selected contact"""
    
    # Get intelligence from database
    intel = get_intelligence(contact_id)
    contact = get_contact_details(contact_id)
    
    if not intel:
        st.warning("⚠️ No intelligence generated yet. Click 'Generate Intelligence' to create.")
        return
    
    # Contact header
    st.header(f"{contact['name']} - {contact['company']}")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.write(f"**Title:** {contact['title']}")
    with col2:
        st.write(f"**Score:** {contact['score']}")
    with col3:
        st.write(f"**Cadence:** {intel['cadence_type']}")
    
    st.divider()
    
    # Tabbed interface
    tab1, tab2, tab3, tab4 = st.tabs([
        "📧 Email Variants", 
        "☎️ Call Scripts", 
        "📋 Intelligence Kernel",
        "📅 Cadence Schedule"
    ])
    
    with tab1:
        display_email_variants(intel)
    
    with tab2:
        display_call_scripts(intel)
    
    with tab3:
        display_intelligence_kernel(intel)
    
    with tab4:
        display_cadence_schedule(contact_id)

def display_email_variants(intel):
    """Display 3 email variants with copy button"""
    
    for i in range(1, 4):
        variant_num = i
        subject = intel.get(f'email_{i}_subject', 'N/A')
        body = intel.get(f'email_{i}_body', 'N/A')
        style = intel.get(f'email_{i}_style', 'N/A')
        
        with st.expander(f"✉️ Email Variant {i}: {style}", expanded=(i==1)):
            st.write(f"**Subject:** {subject}")
            st.text_area(
                "Body",
                value=body,
                height=200,
                key=f"email_{i}",
                label_visibility="collapsed"
            )
            
            col1, col2 = st.columns([1, 4])
            with col1:
                if st.button(f"📋 Copy", key=f"copy_email_{i}"):
                    st.code(f"Subject: {subject}\n\n{body}", language="text")
                    st.success("Ready to copy!")

def display_call_scripts(intel):
    """Display 3 call scripts"""
    
    for i in range(1, 4):
        approach = intel.get(f'call_{i}_approach', 'N/A')
        script = intel.get(f'call_{i}_script', 'N/A')
        
        with st.expander(f"☎️ Call Script {i}: {approach}", expanded=(i==1)):
            st.markdown(script)
            
            if st.button(f"📋 Copy Script", key=f"copy_call_{i}"):
                st.code(script, language="text")
                st.success("Ready to copy!")

def display_intelligence_kernel(intel):
    """Display WHO/WHEN/WHAT framework"""
    
    st.subheader("🎯 Intelligence Kernel")
    
    # WHO
    st.markdown("### WHO")
    st.write(intel.get('who_summary', 'N/A'))
    
    # WHEN
    st.markdown("### WHEN")
    st.write(intel.get('when_timing', 'N/A'))
    
    # WHAT
    st.markdown("### WHAT")
    st.write(intel.get('what_offer', 'N/A'))
    
    # Metadata
    st.divider()
    col1, col2, col3 = st.columns(3)
    with col1:
        st.write(f"**Urgency:** {intel.get('urgency_level', 'N/A')}")
    with col2:
        st.write(f"**Persona:** {intel.get('persona_type', 'N/A')}")
    with col3:
        st.write(f"**Generated:** {intel.get('created_at', 'N/A')}")

def display_cadence_schedule(contact_id):
    """Show scheduled touchpoints"""
    
    touchpoints = get_touchpoints(contact_id)
    
    if touchpoints.empty:
        st.warning("No touchpoints scheduled")
        return
    
    st.subheader(f"📅 {len(touchpoints)} Touchpoints Scheduled")
    
    for idx, tp in touchpoints.iterrows():
        col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
        
        with col1:
            st.write(f"**{tp['scheduled_date']}**")
        with col2:
            st.write(f"📱 {tp['channel']}")
        with col3:
            st.write(f"Priority: {tp['priority']}")
        with col4:
            status_color = "🟢" if tp['status'] == 'scheduled' else "✅"
            st.write(f"{status_color} {tp['status']}")

# ===== DATABASE HELPER FUNCTIONS =====

def get_all_contacts():
    """Fetch all contacts from HubSpot database"""
    conn = sqlite3.connect('sales_angel.db')
    query = "SELECT id, firstname, lastname, company FROM contacts LIMIT 100"
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

def get_contact_name(contact_id):
    """Get formatted contact name"""
    conn = sqlite3.connect('sales_angel.db')
    query = f"SELECT firstname, lastname, company FROM contacts WHERE id={contact_id}"
    df = pd.read_sql_query(query, conn)
    conn.close()
    if len(df) > 0:
        return f"{df.iloc[0]['firstname']} {df.iloc[0]['lastname']} ({df.iloc[0]['company']})"
    return "Unknown"

def get_intelligence(contact_id):
    """Fetch intelligence for contact"""
    conn = sqlite3.connect('sales_angel.db')
    query = f"SELECT * FROM contact_intelligence WHERE contact_id={contact_id}"
    df = pd.read_sql_query(query, conn)
    conn.close()
    if len(df) > 0:
        return df.iloc[0].to_dict()
    return None

def get_touchpoints(contact_id):
    """Fetch scheduled touchpoints"""
    conn = sqlite3.connect('sales_angel.db')
    query = f"""
        SELECT scheduled_date, channel, priority, status 
        FROM touchpoint_schedule 
        WHERE contact_id={contact_id}
        ORDER BY scheduled_date
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

# ===== STATS FUNCTIONS =====

def get_hot_leads_count():
    """Count contacts with score >= 85"""
    # Implement based on your scoring logic
    return 12  # Placeholder

def get_avg_score():
    """Get average contact score"""
    return 73.5  # Placeholder

def get_todays_calls_count():
    """Count calls scheduled for today"""
    return 8  # Placeholder

def get_week_touchpoints():
    """Count this week's touchpoints"""
    return 34  # Placeholder

def get_today_enrichment_count():
    """Count enrichments today"""
    return 5  # Placeholder

def get_pending_touchpoints_count():
    """Count pending touchpoints"""
    return 23  # Placeholder

if __name__ == "__main__":
    main()
```

---

### 3. **Connect to Existing Database** (15 minutes)

**Fix database connection to use actual `sales_angel.db`:**

```python
# Update all database connections to point to correct file
import sqlite3
import os

DB_PATH = "sales_angel.db"  # Same directory as premium_dashboard.py

def get_db_connection():
    """Get SQLite connection with error handling"""
    try:
        conn = sqlite3.connect(DB_PATH)
        return conn
    except Exception as e:
        st.error(f"Database connection error: {e}")
        return None
```

---

### 4. **Test Dashboard** (30 minutes)

**Run and verify:**

```bash
# Activate environment
source venv/bin/activate

# Run dashboard
streamlit run premium_dashboard.py

# Should open at http://localhost:8501
```

**Test checklist:**
- [ ] Text is readable (proper colors)
- [ ] Components are aligned
- [ ] Can select a contact
- [ ] Intelligence displays (emails, scripts, kernel)
- [ ] Buttons work
- [ ] No errors in console

---

## 🎯 SUCCESS CRITERIA

### After this fix, you should have:

1. ✅ **Readable dashboard** - All text properly colored and visible
2. ✅ **Proper layout** - Components positioned correctly, no overlap
3. ✅ **Working data display** - Intelligence, emails, scripts visible
4. ✅ **Interactive UI** - Buttons, tabs, selectors functional
5. ✅ **Foundation ready** - Can now plug in enhancements from dev plan

---

## 🚀 NEXT STEPS (After Dashboard is Fixed)

Once dashboard is working, immediately proceed to:

1. **Task #1 from Dev Plan:** Bi-directional CRM Integration (16 hours)
2. **Task #2:** End-to-End Data Encryption (12 hours)
3. **Task #5:** Predictive Lead Scoring with ML (32 hours)

---

## 📁 FILES TO MODIFY

1. `premium_dashboard.py` - Main dashboard file (complete rewrite)
2. Test connection to `sales_angel.db`
3. Verify `sales_angel_PREMIUM.py` is generating data correctly

---

## ⏱️ TIME ESTIMATE

- **Text/styling fixes:** 30 min
- **Layout restructure:** 45 min
- **Database connection:** 15 min
- **Testing & debugging:** 30 min
- **Total:** 2 hours

---

## 🔥 LET'S GO!

Ready to execute? Start with the CSS styling first, then rebuild the layout structure, then connect to database, then test.

**Start time:** Now  
**Expected completion:** 2 hours  
**Status:** Ready to code 💪
