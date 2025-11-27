# SALES ANGEL - COMPLETE INTEGRATED SYSTEM

**AI-Powered Sales Intelligence with ML Learning**

This is the complete, integrated system that generates personalized emails and call scripts, saves everything to a database, and uses machine learning to adapt based on your feedback.

---

## 🎯 Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│  SALES ANGEL SYSTEM                                             │
└─────────────────────────────────────────────────────────────────┘
         │
         ├── 📥 INPUT: Enriched Contacts (CSV)
         │     └─ Name, Company, Title, MBTI, DISC, News, etc.
         │
         ├── 🔄 GENERATION LAYER
         │     ├─ loan_email_generator.py (3 variants each)
         │     └─ loan_call_generator.py (3 variants + objections)
         │
         ├── 💾 DATABASE LAYER (sales_angel.db)
         │     ├─ Contacts table
         │     ├─ Generated content table
         │     ├─ ML feedback table
         │     └─ Metrics table
         │
         ├── 🧠 ML LEARNING LAYER
         │     ├─ Content quality prediction
         │     ├─ User preference analysis
         │     └─ Adaptive prompt optimization
         │
         ├── 🎨 DASHBOARD LAYER
         │     ├─ Content review interface
         │     ├─ Accept/reject with feedback
         │     ├─ ML insights display
         │     └─ Settings panel
         │
         └── 📊 OUTPUT: Database + Dashboard
               └─ Accepted content ready for use
```

---

## 📦 Files Included

| File | Purpose |
|------|---------|
| `loan_email_generator.py` | Generates 3 personalized email variants |
| `loan_call_generator.py` | Generates 3 personalized call scripts |
| `sales_angel_db.py` | Database schema + content management |
| `sales_angel_ml.py` | ML learning + preference analysis |
| `sales_angel_dashboard.py` | Streamlit dashboard for review |
| `sales_angel_pipeline.py` | Master orchestrator (main entry point) |
| `sales_angel.db` | SQLite database (auto-created) |

---

## 🚀 Quick Start

### 1. Prerequisites

```bash
pip install openai python-dotenv streamlit
```

### 2. Set Up Environment

Create `.env` file:
```
OPENAI_API_KEY=sk-...
PERPLEXITY_API_KEY=...
HUBSPOT_API_KEY=...
```

### 3. Prepare Contact CSV

Your enriched contacts CSV should have these columns:
- `name` - Full name
- `company` - Company name
- `title` - Job title
- `email` - Email address
- `phone` - Phone number
- `mbti` - MBTI personality type (e.g., ESTJ)
- `disc` - DISC profile (e.g., C-Type)
- `news` - Recent company news/triggers
- `value_props` - Your value propositions
- `score` - Lead score

### 4. Run Pipeline

```bash
# Generate content for first 10 contacts (testing)
python sales_angel_pipeline.py --csv contacts.csv --batch 10

# Generate for ALL contacts
python sales_angel_pipeline.py --csv contacts.csv

# Skip generation, just review existing content
python sales_angel_pipeline.py --skip-generation

# Custom database path
python sales_angel_pipeline.py --db my_sales_angel.db
```

### 5. Review & Provide Feedback

Dashboard automatically launches at `http://localhost:8501`

Or launch manually:
```bash
streamlit run sales_angel_dashboard.py
```

---

## 💡 How It Works

### Generation Flow

1. **Load Contacts** → Pipeline reads CSV with enriched contact data
2. **Generate Emails** → `loan_email_generator.py` creates 3 variants per contact
3. **Generate Calls** → `loan_call_generator.py` creates 3 variants + objection handling
4. **Save to DB** → All content stored in `sales_angel.db`
5. **ML Tracking** → Each item gets quality score prediction

### Feedback Flow

1. **Review Content** → Dashboard displays each variant with quality score
2. **Provide Feedback** → You accept/reject with reasoning
3. **ML Learning** → System learns your preferences
4. **Adapt Prompts** → Next generation uses learned preferences
5. **Continuous Improvement** → System gets smarter over time

---

## 🎛️ Dashboard Features

### Review Tab
- **Content Display** → Email or call script with full context
- **Quality Metrics** → AI prediction + acceptance rate by style
- **Why Accept?** → Reasons this content is good
- **Why Reject?** → Reasons to improve
- **Feedback Buttons**
  - ✅ Accept (approve for use)
  - ❌ Reject (request regeneration)
  - ⭐ Mark as Best (favorite style)

### ML Insights Tab
- **Acceptance Rate** → Overall quality metric
- **By Style Performance** → Which approaches you prefer
- **By Variant Performance** → Which variant # works best
- **Your Preferences** → System's learned understanding
- **Suggested Adjustments** → Optimizations for next generation

### Settings Tab
- **API Configuration** → Verify keys are set
- **Database Stats** → Record counts
- **Reset Data** → Clear everything (if needed)

---

## 🧠 Machine Learning System

### How Learning Works

```
User Accepts Content with Style X
         ↓
ML System records: Accept + Style X
         ↓
Next generation prioritizes Style X
         ↓
Quality improves → More accepts
```

### Tracked Metrics

| Metric | Tracked | Used For |
|--------|---------|----------|
| Acceptance by Style | Yes | Predict quality for each style |
| Acceptance by Variant# | Yes | Learn which variant position works best |
| Word Count | Yes | Optimize length preferences |
| Specific References | Yes | Encourage personalization |
| CTA Clarity | Yes | Improve call-to-action quality |
| User Feedback Text | Yes | Understand why decisions made |

### Adaptive Prompts

System automatically adjusts generation prompts based on:
- Your most-accepted styles
- Your least-accepted styles
- Your preferred variant numbers
- Your overall acceptance rate
- Specific feedback you've given

---

## 📊 Database Schema

### contacts table
```
id, firstname, lastname, email, phone, company, jobtitle, mbti, disc, score, created_at
```

### generated_content table
```
id, contact_id, content_type, variant_num, style, subject, body, lines, cta, objections,
generated_at, status, feedback_score, user_rating, user_notes, accepted_at, rejected_at
```

### ml_feedback table
```
id, content_id, contact_id, user_action, reasoning, variant_num, style, key_factors, feedback_timestamp
```

### ml_metrics table
```
id, metric_date, total_generated, total_accepted, total_rejected, acceptance_rate, avg_feedback_score, model_accuracy
```

---

## 🎯 Quality Guardrails

### Anti-Hallucination

The system prevents AI from suggesting:
- ❌ Fintech products
- ❌ Software/platforms
- ❌ Apps or digital tools
- ❌ AI solutions
- ❌ Automation systems

Only suggests:
- ✅ Lending products (SBA 504, 7(a), Conventional)
- ✅ Credit solutions
- ✅ Deal structure strategies
- ✅ Timing and regulatory compliance

### Content Validation

Each generated variant checks for:
- ✅ Specific company/role reference
- ✅ Clear problem statement
- ✅ No generic openers
- ✅ Clear CTA or question
- ✅ Reasonable word count (60-100 words)
- ✅ No banned terms

---

## 🔄 Batch Processing

For large lists:

```bash
# Process 100 contacts
python sales_angel_pipeline.py --csv contacts.csv --batch 100

# Process ALL contacts
python sales_angel_pipeline.py --csv contacts.csv
```

Each contact generates:
- 3 email variants
- 3 call scripts (with objection handling)
- Total: 6 pieces of content per contact

For 100 contacts = 600 pieces of content to review

---

## 📈 Monitoring ML Progress

Watch metrics in real-time:

```bash
# In dashboard → ML Insights tab

Overall Acceptance Rate: 65%
Problem-Agitate-Solve: 78% (improving)
Social Proof: 62%
Value-First Consultative: 54% (needs work)
```

System learns and optimizes automatically.

---

## 🛠️ Configuration

### Customize Company Profile

Edit in `loan_email_generator.py` and `loan_call_generator.py`:

```python
COMPANY_PROFILE = """
BUSINESS DOMAIN:
- We do NOT provide fintech, software, platforms...
- We DO provide: SBA 504, 7(a), Conventional loans

UNIQUE VALUE PROPOSITIONS:
- Flexible credit solutions
- Nationwide lender
- Quick closings
- Story lending capability
- [ADD YOUR OWN]
"""
```

### Adjust ML Model Weights

Edit in `sales_angel_ml.py`:

```python
self.feature_weights = {
    'style': {},          # Adjusted from feedback
    'variant_num': {},    # Adjusted from feedback
    'word_count': 0.1,    # Tune importance
    'has_specific_reference': 0.2
}
```

---

## 🐛 Troubleshooting

### "No pending content"
→ Run pipeline to generate content first
```bash
python sales_angel_pipeline.py --csv contacts.csv --batch 5
```

### "API Error: 401"
→ Check OPENAI_API_KEY in .env file

### "FileNotFoundError: contacts.csv"
→ Create CSV with enriched contacts in same directory

### "Database locked"
→ Close dashboard, wait 5 seconds, try again

---

## 📞 Support

For issues:
1. Check database: `sqlite3 sales_angel.db ".tables"`
2. Check logs in dashboard Settings tab
3. Verify .env file has all required keys
4. Try with `--batch 1` to debug single contact

---

## 🚀 Next Steps

1. ✅ Run pipeline on 10 contacts
2. ✅ Review in dashboard (accept/reject 3-4 each)
3. ✅ Check ML Insights to see learning
4. ✅ Run again on full list
5. ✅ Export accepted content for use

---

## 📝 License & Credits

Sales Angel | AI-Powered Sales Intelligence
Built with OpenAI GPT-4 | Streamlit | SQLite

---

**Questions?** See files for detailed docstrings and comments.

**Ready?** Start with:
```bash
python sales_angel_pipeline.py --help
```
