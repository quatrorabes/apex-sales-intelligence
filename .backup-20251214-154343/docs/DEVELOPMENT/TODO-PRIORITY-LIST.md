# SALES ANGEL - PRIORITY TODO & FEATURE LIST
**Updated:** November 12, 2025, 2:52 AM PST  
**Status:** Production Path

---

## 🔥 IMMEDIATE PRIORITIES (Next Session)

### 1. **Fix Email Generation Quality** ⚠️
**Status:** CRITICAL - Current emails are template-based, not AI-powered  
**What needs to happen:**
- [ ] Integrate existing `email_variant_generator_fixed.py` into `sales_angel_PREMIUM.py`
- [ ] Integrate existing `call_script_generator.py` 
- [ ] Use `unified_generator.py` to orchestrate both
- [ ] Test with real enrichment data
- [ ] Verify OpenAI/Perplexity API calls working
- [ ] Quality validation: emails must reference specific prospect details

**Files involved:**
- `sales_angel_PREMIUM.py` (main system)
- `email_variant_generator_fixed.py` (proven generator)
- `call_script_generator.py` (proven generator)
- `unified_generator.py` (orchestration)

**Expected outcome:** Emails go from generic templates to personalized, research-based content

---

### 2. **Daily Call List Feature** 🆕
**Status:** NEW REQUIREMENT - Add to product  
**What it is:**
- Automated daily digest of 5-10 top-priority contacts to call
- Delivered via email, Slack, or dashboard
- Sorted by urgency, score, and cadence timing

**Requirements:**
- [ ] Create daily call list generator
- [ ] Pull from scheduled touchpoints (phone channel)
- [ ] Limit to 5-10 contacts per day
- [ ] Include: Name, Company, Why Now, Talk Track
- [ ] Delivery options: Email, Slack notification, Dashboard widget
- [ ] Schedule: Runs daily at 8am user's timezone

**Technical approach:**
```python
def generate_daily_call_list(user_id, limit=10):
    """
    Pull today's scheduled phone touchpoints
    Rank by urgency and score
    Generate brief with call prep notes
    Send to user via preferred channel
    """
    pass
```

**File to create:** `daily_call_list_generator.py`

**Integration points:**
- `sales_angel_PREMIUM.py` - touchpoint scheduler
- `premium_dashboard.py` - UI display
- `slack.py` - notification delivery

---

### 3. **Assistant Menu Bar Item** 🆕
**Status:** NEW FEATURE - Monetization opportunity  
**What it is:**
- Menu bar app (Mac/Windows) that sits in system tray
- Quick access to daily call list
- One-click contact lookup
- Quick-dial with call script popup
- Real-time notifications for hot leads

**Packaging decision:**
- **Option A:** Include in basic package (value-add)
- **Option B:** Premium add-on ($25-50/month extra)
- **Recommendation:** Include in Professional+ tier, upsell for Starter

**Features:**
- 🔔 Real-time notifications (new hot lead, follow-up due)
- 📞 Click-to-call with instant script popup
- 📋 Today's call list always visible
- 🔍 Quick search any contact
- ✉️ Draft email from menu bar
- 📊 Quick stats (calls today, emails sent, responses)

**Technical stack:**
- **Mac:** Swift/SwiftUI menu bar app
- **Windows:** Electron or native .NET
- **Backend:** REST API to main platform
- **Auth:** OAuth token from web login

**File structure:**
```
/assistant_app
  /mac
    MenuBarApp.swift
    CallListView.swift
    ContactSearchView.swift
  /windows
    MenuBarApp.cs
    ...
  /shared
    api_client.py
    notifications.py
```

**Development estimate:** 40-60 hours (per platform)

---

## 🧪 TESTING REQUIREMENTS

### 4. **Cold Lead Testing from LinkedIn** 🆕
**Status:** CRITICAL VALIDATION - Need real-world test  
**What we need to do:**

#### Test Setup:
- [ ] Export 25-50 cold leads from LinkedIn Sales Navigator
- [ ] Import into system (no prior relationship)
- [ ] Run full enrichment pipeline
- [ ] Generate intelligence + emails + call scripts
- [ ] Review quality manually
- [ ] Send test batch (5-10 emails)
- [ ] Track response rates

#### Success Criteria:
- Enrichment completes for 90%+ of leads
- Emails reference specific details (not generic)
- Call scripts include research-based talking points
- Response rate target: 8-12% (vs. 2-5% industry standard)

#### Test Protocol:
1. **Source leads:** LinkedIn Sales Navigator (banking/insurance)
2. **Import method:** CSV upload or API
3. **Enrichment run:** Full Perplexity + LinkedIn scrape
4. **Quality review:** Manual check of 10 samples
5. **Test send:** 5 emails (approval required)
6. **Track metrics:** Open rate, reply rate, meeting booked rate
7. **Iterate:** Refine prompts based on results

**File to create:** `linkedin_import_tester.py`

---

## 📦 PACKAGING & PRICING STRATEGY

### Product Tiers (Updated)

#### **Starter - $150/month**
- 100 contacts/month
- Basic enrichment
- Standard email variants (3)
- Standard call scripts (3)
- 2 cadences (14-day, 30-day)
- Dashboard access
- Email support

#### **Professional - $250/month** ⭐ MOST POPULAR
- 500 contacts/month
- Advanced enrichment (Perplexity)
- Premium email variants (3)
- Premium call scripts (3)
- All 4 cadences
- Daily call list ✅ NEW
- Assistant menu bar app ✅ NEW
- Dashboard + API access
- Priority support

#### **Enterprise - $450/month**
- Unlimited contacts
- Custom enrichment sources
- Unlimited variants
- Custom cadences
- White-label option
- Multi-user support
- Dedicated success manager
- SLA guarantee

### Add-Ons:
- **Assistant App (if not included):** $35/month
- **API access (Starter tier):** $50/month
- **Extra enrichment credits:** $0.10/contact
- **Custom integrations:** Quote based

---

## 🛠️ TECHNICAL IMPLEMENTATION ROADMAP

### Phase 1: Core Fixes (This Week)
**Goal:** Get system production-ready with quality content

- [x] Database schema (contact_intelligence, touchpoint_schedule)
- [x] Cadence engine (4 cadences)
- [x] Touchpoint scheduling
- [ ] **Integrate proven email/call generators** 🔥
- [ ] **Fix enrichment → email data flow** 🔥
- [ ] **Test with real enriched contacts** 🔥
- [ ] Quality validation workflow

**Estimated time:** 8-12 hours

---

### Phase 2: Daily Call List (Next Week)
**Goal:** Automated daily prioritization

- [ ] Call list generator logic
- [ ] Scoring algorithm (urgency + timing)
- [ ] Email delivery template
- [ ] Slack webhook integration
- [ ] Dashboard widget
- [ ] User preferences (time, quantity, format)
- [ ] Testing with real calendar

**Estimated time:** 12-16 hours

---

### Phase 3: LinkedIn Import & Testing (Concurrent with Phase 2)
**Goal:** Validate with cold leads

- [ ] LinkedIn export workflow documentation
- [ ] CSV import tool
- [ ] Enrichment pipeline test
- [ ] Quality scoring system
- [ ] A/B test framework
- [ ] Metrics dashboard
- [ ] Iteration protocol

**Estimated time:** 8-10 hours

---

### Phase 4: Assistant Menu Bar App (2-3 Weeks)
**Goal:** Native desktop presence

#### Mac App:
- [ ] Swift project setup
- [ ] Menu bar UI
- [ ] API client integration
- [ ] Notification system
- [ ] Call list view
- [ ] Contact search
- [ ] Click-to-call integration
- [ ] App Store prep

#### Windows App (optional for MVP):
- [ ] Electron or .NET setup
- [ ] Similar feature set

**Estimated time:** 40-60 hours (Mac only)

---

## 🔍 QUALITY CHECKLIST

Before sending ANY emails to prospects:

### Email Quality Validation:
- [ ] References specific detail about prospect (company, role, recent activity)
- [ ] No generic phrases ("I hope this email finds you well")
- [ ] Natural tone (not obviously AI-generated)
- [ ] Clear value proposition
- [ ] Relevant to their industry/role
- [ ] Reasonable ask (not pushy)
- [ ] Proper grammar and formatting
- [ ] CTA makes sense for context

### Call Script Quality:
- [ ] Opening references research
- [ ] Questions are relevant to their business
- [ ] Objection handling specific to industry
- [ ] Closing appropriate for relationship stage
- [ ] Natural conversation flow

### System Quality:
- [ ] Enrichment data is accurate
- [ ] Scoring makes sense (high scores = truly promising)
- [ ] Cadences executing on schedule
- [ ] No duplicate touchpoints
- [ ] Analytics tracking properly

---

## 🎯 SUCCESS METRICS

### Short-term (30 days):
- 50 contacts fully enriched
- 20 test emails sent
- 3+ responses received (15% response rate target)
- 1 meeting booked
- Daily call list running smoothly
- Zero system errors

### Medium-term (90 days):
- 250 active users
- $30K MRR
- 10-15% average response rate
- 2-3% meeting booking rate
- Assistant app launched (Mac)
- 2 case studies published

### Long-term (1 year):
- 500+ users
- $100K+ MRR
- Proven ROI metrics
- Multi-vertical success (insurance, mortgage, equipment)
- Series A ready

---

## 🚨 KNOWN ISSUES TO ADDRESS

1. **Email Quality** - Using templates instead of AI ⚠️
   - Fix: Integrate existing proven generators

2. **OpenAI API Not Loading** - Environment variable issue
   - Fix: Create .env file or export key

3. **No Enrichment Data** - Empty fields in database
   - Fix: Run enrichment pipeline on existing contacts

4. **No Quality Filter** - System accepts any output
   - Fix: Build validation layer with rejection criteria

5. **No Edit Workflow** - Can't review before sending
   - Fix: Add approval step in dashboard

---

## 📋 NEXT IMMEDIATE ACTIONS (Monday Morning)

### Priority Order:

1. **Fix Email Generation** (2-3 hours)
   - Integrate proven generators
   - Test with 5 contacts
   - Verify quality improvement

2. **Run Enrichment on Test Batch** (1 hour)
   - Select 10 contacts
   - Run full enrichment
   - Verify data populates correctly

3. **Generate Daily Call List** (2-3 hours)
   - Build basic version
   - Test output
   - Email delivery

4. **LinkedIn Import Test** (2 hours)
   - Export 25 cold leads
   - Import to system
   - Run enrichment
   - Review results

5. **Plan Assistant App** (1 hour)
   - Finalize features
   - Choose tech stack
   - Estimate timeline
   - Decide on pricing tier

**Total time Monday:** 8-10 hours

---

## 💡 FUTURE ENHANCEMENTS (Backlog)

### Features to Consider:
- Video message generation (Loom-style)
- Voice note generation (AI voice)
- LinkedIn message automation
- SMS integration
- Calendar booking links
- Meeting prep briefs
- Post-meeting follow-up automation
- Team collaboration features
- CRM activity logging
- Conversation intelligence (call recording analysis)

### Integrations:
- Calendly/Calendar.ly
- Zoom/Google Meet
- Gong/Chorus (conversation intel)
- ZoomInfo/Apollo (data enrichment)
- Clay.com (enrichment competitor)

### AI Enhancements:
- Custom voice cloning
- Image generation (personalized visuals)
- Dynamic landing pages per prospect
- Real-time objection handling suggestions
- Sentiment analysis on replies

---

## 📞 ASSISTANT MENU BAR APP - DETAILED SPEC

### Core Features:

#### 1. **Today's Call List**
- Shows 5-10 prioritized calls for the day
- One-click to view full contact details
- Click-to-dial (if phone system integrated)
- Mark as "called", "left voicemail", "no answer", etc.
- Quick notes entry

#### 2. **Quick Search**
- Search any contact by name/company
- Instant results dropdown
- Shows: name, company, last touchpoint, score
- Click to open full profile

#### 3. **Notifications**
- New hot lead alert
- Follow-up due reminder
- Response received notification
- Meeting scheduled confirmation

#### 4. **Quick Actions**
- Draft email (opens mini composer)
- Log activity (call, meeting, note)
- Schedule follow-up
- View contact card

#### 5. **Stats Dashboard**
- Calls today: 7/10
- Emails sent: 15
- Responses: 3
- Meetings booked: 1

#### 6. **Settings**
- Notification preferences
- Working hours
- Daily call list quantity
- Integrations (phone, calendar)

### Technical Requirements:

#### Mac App:
```swift
// MenuBarApp.swift
import SwiftUI
import Combine

@main
struct SalesAngelApp: App {
    @NSApplicationDelegateAdaptor(AppDelegate.self) var appDelegate
    
    var body: some Scene {
        MenuBarExtra("Sales Angel", systemImage: "phone.circle") {
            ContentView()
        }
    }
}

// Views
- CallListView: Shows today's calls
- ContactSearchView: Quick search
- NotificationsView: Alerts
- QuickActionsView: Common tasks
- SettingsView: Preferences
```

#### API Integration:
```python
# api_client.py
class SalesAngelAPI:
    def get_daily_call_list(self):
        """Fetch today's prioritized calls"""
        pass
    
    def search_contacts(self, query):
        """Search contacts"""
        pass
    
    def log_activity(self, contact_id, activity_type, notes):
        """Log call/meeting/note"""
        pass
    
    def draft_email(self, contact_id):
        """Get email draft for contact"""
        pass
```

#### Notification Service:
```python
# notifications.py
class NotificationService:
    def subscribe_to_events(self):
        """WebSocket or polling for real-time updates"""
        pass
    
    def show_notification(self, title, body, action_url):
        """Display system notification"""
        pass
```

---

## 🎨 UI/UX NOTES

### Dashboard Improvements Needed:
- Today's call list prominent on homepage
- One-click to view contact full profile
- Inline editing of emails before sending
- Approval workflow for first-time sends
- Analytics charts (response rates, meeting rates)
- A/B test results visualization

### Mobile Considerations:
- Responsive web design first
- Native iOS/Android apps later
- Focus on call list + quick actions
- Push notifications critical

---

## 📊 ANALYTICS & REPORTING

### Metrics to Track:

#### User Metrics:
- Daily active users
- Contacts enriched per user
- Emails sent per user
- Calls logged per user
- Average session length

#### Performance Metrics:
- Email open rate
- Email response rate
- Meeting booking rate
- Call connection rate
- Time to first response

#### System Metrics:
- API latency
- Enrichment success rate
- AI generation quality score
- System uptime
- Error rate

#### Revenue Metrics:
- MRR growth
- Churn rate
- CAC
- LTV
- Revenue per user

---

## ✅ COMPLETION CRITERIA

### When is the product "ready"?

**MVP Ready:**
- [ ] Email quality consistently good (90%+ pass manual review)
- [ ] Enrichment working for 85%+ of contacts
- [ ] Daily call list generating correctly
- [ ] Zero critical bugs
- [ ] 10 successful test cases with real prospects

**Launch Ready:**
- [ ] All MVP criteria met
- [ ] 3 pilot customers successfully onboarded
- [ ] Case studies written
- [ ] Pricing validated
- [ ] Support documentation complete
- [ ] Assistant app in beta (Mac)

**Scale Ready:**
- [ ] 50+ paying customers
- [ ] <5% churn rate
- [ ] Response rate consistently 10%+
- [ ] Meeting booking rate 2%+
- [ ] Multi-vertical proven (2+ industries)
- [ ] Series A metrics hit

---

## 🔐 SECURITY & COMPLIANCE

### Before Launch:
- [ ] Security audit
- [ ] Privacy policy
- [ ] Terms of service
- [ ] GDPR compliance review (if targeting EU)
- [ ] SOC 2 preparation (for enterprise)
- [ ] Data encryption at rest and in transit
- [ ] API authentication/authorization
- [ ] Rate limiting
- [ ] Monitoring/alerting

---

## 💬 USER FEEDBACK LOOP

### How we'll iterate:
1. **Weekly user interviews** (5-10 users)
2. **In-app feedback widget**
3. **Support ticket analysis**
4. **Usage analytics review**
5. **Monthly feature voting**
6. **Beta testing program** for new features

---

**Last Updated:** Nov 12, 2025, 2:52 AM  
**Next Review:** After email generator integration complete

---

*This is a living document. Update after each major milestone or feature add.*
