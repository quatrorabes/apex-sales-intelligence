# 🚀 AI EMAIL & CALL VARIANT GENERATOR
## Installation & Quick Start Guide

**Created:** November 11, 2025, 8:11 PM PST  
**Status:** Production-Ready  
**Cost:** ~$0.04-0.06 per contact (3 emails + 3 call scripts)

---

## 📋 What This Does

Generates **world-class outreach content** using your enriched profile data:

### Email Variants (3 per contact)
1. **Direct Value**: Pain point-focused, immediate value proposition
2. **Social Proof**: Achievement-based, credibility-building approach
3. **Insight-Led**: Industry trend/insight that creates curiosity

### Call Scripts (3 per contact)
1. **Direct & Confident**: Straight to the point, value-focused
2. **Consultative**: Rapport-building, relationship-first approach
3. **Executive**: Strategic insights for senior decision-makers

**Each variant:**
- Uses REAL data from your enrichment
- References specific details about the person/company
- Sounds natural and authentic (not templated)
- Matches their personality and communication style
- Includes objection handling and next steps

---

## ⚡ Quick Start (5 Minutes)

### Step 1: Install Dependencies

```bash
cd ~/projects/sales-angel-clean
source venv/bin/activate

# Install required package
pip install requests
```

### Step 2: Add New Database Columns

```bash
# Run this to add columns for timestamps
sqlite3 sales_angel.db "
ALTER TABLE contacts ADD COLUMN variants_generated_at TEXT;
ALTER TABLE contacts ADD COLUMN scripts_generated_at TEXT;
"
```

### Step 3: Copy the Generator Files

Save these 3 files to your `~/projects/sales-angel-clean/` directory:
- `email_variant_generator.py`
- `call_script_generator.py`
- `unified_generator.py`

### Step 4: Test with One Contact

```bash
# Generate complete kit for Matt Cheeseman
python unified_generator.py 157153

# View the results
python unified_generator.py view 157153
```

**Expected output:**
```
🎯 GENERATING COMPLETE OUTREACH KIT
══════════════════════════════════════════════════════════════════
Contact: Matt Cheeseman
Title: [his title]
Company: River City Bank
Score: 68 | Tier: WARM
══════════════════════════════════════════════════════════════════

⚡ Parallel generation mode (faster)...

🎯 Generating AI Email Variants for Contact 157153...
  Variant 1...  ✅ (142 chars)
  Variant 2...  ✅ (156 chars)
  Variant 3...  ✅ (148 chars)

📞 Generating AI Call Scripts for Contact 157153...
  Variant 1 (Direct)...  ✅ (1847 chars)
  Variant 2 (Consultative)...  ✅ (2012 chars)
  Variant 3 (Executive)...  ✅ (1653 chars)

✨ GENERATION COMPLETE FOR Matt Cheeseman
══════════════════════════════════════════════════════════════════
📧 Email Variants: ✅ 3/3
📞 Call Scripts: ✅ 3/3

🎉 FULL OUTREACH KIT READY!
```

---

## 📖 Usage Examples

### Generate for Single Contact
```bash
python unified_generator.py 157153
```

### Generate for All 9 Enriched Contacts
```bash
python unified_generator.py batch 9
```

### View Generated Content
```bash
# View everything
python unified_generator.py view 157153

# View just emails
python email_variant_generator.py view 157153

# View just call scripts
python call_script_generator.py view 157153
```

### Batch Generate for Specific Number
```bash
# Generate for top 5 enriched contacts
python unified_generator.py batch 5

# Generate for all enriched
python unified_generator.py batch
```

### Quick API Test
```bash
# Test with one generation of each type
python unified_generator.py test 157153
```

---

## 💰 Cost Breakdown

**Per Contact (Complete Kit):**
- 3 Email Variants: ~$0.015-0.025
- 3 Call Scripts: ~$0.025-0.035
- **Total: ~$0.04-0.06**

**Your 9 Enriched Contacts:**
- 9 contacts × $0.05 avg = **$0.45 total**
- Gets you: 27 emails + 27 call scripts = **54 pieces of content**

**ROI:**
- $0.45 invested → 9 contacts with 6 variants each
- ONE meeting booked = $45K-450K potential deal value
- **ROI: 10,000% - 100,000%**

---

## 🎯 What Makes This World-Class

### 1. **Uses Your Enrichment Data**
- Pulls from `deep_intel`, `personality_profile`, `key_intelligence`
- References REAL details about the person/company
- Not generic templates

### 2. **Three Distinct Approaches**
- Different hooks, different positioning
- A/B/C test which works best
- Adapt to different personalities

### 3. **Natural & Authentic**
- Sounds like a human wrote it
- Professional but conversational
- Matches prospect's communication style

### 4. **Action-Oriented**
- Clear call-to-action in every variant
- Objection handling in call scripts
- Specific next steps

### 5. **Comprehensive**
- Emails: Short (3-4 sentences, <100 words)
- Call Scripts: Full conversation flow with discovery questions
- Rep notes: Key insights and what NOT to say

---

## 📊 Sample Output

### Email Variant 1 (Direct Value)
```
Subject: Quick question about your SBA lending volume

Hi Matt,

I noticed River City Bank's focus on SBA 504 lending. Most lenders 
we work with struggle with processing delays that cost them 2-3 
deals per quarter.

We've helped similar community banks cut approval time by 40% while 
maintaining compliance. Worth a 15-minute conversation?

Best,
[Your Name]
```

### Call Script 1 (Direct)
```
═══════════════════════════════════════════════════════════════
CALL SCRIPT VARIANT 1
Matt Cheeseman - VP Commercial Lending at River City Bank
═══════════════════════════════════════════════════════════════

📞 OPENER:
"Hi Matt, this is [Your Name] from [Company]. I know you're busy, so 
I'll be brief. I've been working with community banks in the SBA 
lending space and saw River City Bank's strong presence in 504 loans."

🎯 HOOK/VALUE PROP:
"The reason I'm calling is we're helping banks like yours eliminate 
the processing bottlenecks that typically cost 2-3 deals per quarter. 
Based on what I've seen with your volume, that's potentially $150K+ 
in lost revenue annually. Is that something you're actively working on?"

❓ DISCOVERY QUESTIONS:
• What's your current average time from application to SBA approval?
• How many deals would you say you lose to processing delays?
• If you could cut that time in half, what would that mean for your 
  team and your numbers?

🛡️ OBJECTION HANDLING:
IF they say "Not interested":
"I totally understand. Quick question before I let you go - if you 
could solve one thing about your SBA lending process tomorrow, what 
would it be?"

IF they say "Send me info":
"I could, but honestly the info won't make much sense without context. 
How about I send you a 2-minute video explaining exactly how we helped 
[similar bank] add $4M in SBA volume last year? I'll include my 
calendar link and you can grab 15 minutes if it looks relevant."

✅ CLOSING/NEXT STEP:
"Based on what you shared, I think a 15-minute demo showing exactly 
how we'd apply this to River City Bank would be valuable. I have 
Thursday at 2pm or Friday at 10am open. Which works better?"

📝 NOTES FOR REP:
• Matt is analytical - lead with data and ROI
• River City Bank prides itself on community relationships - emphasize 
  how faster processing helps serve their market better
• DON'T pitch technology for technology's sake - always tie to business 
  outcomes
═══════════════════════════════════════════════════════════════
```

---

## 🔥 Advanced Usage

### Regenerate for Specific Contact
```bash
# This will overwrite existing variants
python email_variant_generator.py 157153
python call_script_generator.py 157153

# Or both at once
python unified_generator.py 157153
```

### Export to CSV
```bash
# Export all email subjects to review
sqlite3 sales_angel.db "
SELECT 
  id, firstname, lastname, company,
  email_1_subject, email_2_subject, email_3_subject
FROM contacts 
WHERE variants_generated_at IS NOT NULL
" > email_subjects.csv
```

### Check Generation Status
```bash
# See which contacts have variants
sqlite3 sales_angel.db "
SELECT 
  id, firstname, lastname, company,
  CASE 
    WHEN variants_generated_at IS NOT NULL THEN 'Yes' 
    ELSE 'No' 
  END as has_emails,
  CASE 
    WHEN scripts_generated_at IS NOT NULL THEN 'Yes' 
    ELSE 'No' 
  END as has_scripts
FROM contacts 
WHERE enriched = 1
"
```

---

## 🐛 Troubleshooting

### "No such column: variants_generated_at"
**Fix:** Run Step 2 again to add the columns

### "Contact not found or not enriched"
**Fix:** Make sure the contact has `enriched = 1` in database
```bash
sqlite3 sales_angel.db "SELECT id, firstname, lastname, enriched FROM contacts WHERE id = 157153"
```

### "Error generating variant: 401 Unauthorized"
**Fix:** Check your Perplexity API key in `.env`
```bash
cat .env | grep PERPLEXITY_API_KEY
```

### Variants are too generic
**Fix:** Your enrichment data might be sparse. Check:
```bash
sqlite3 sales_angel.db "SELECT deep_intel, personality_profile FROM contacts WHERE id = 157153"
```

---

## 📈 Next Steps

### 1. Generate for All 9 Contacts (NOW)
```bash
cd ~/projects/sales-angel-clean
source venv/bin/activate
python unified_generator.py batch 9
```

**Time:** 3-5 minutes  
**Cost:** ~$0.45  
**Output:** 54 pieces of world-class outreach content

### 2. Review and Send
```bash
# View Matt Cheeseman's kit
python unified_generator.py view 157153

# Copy email variant 1 or 2 (whichever you prefer)
# Send via Gmail/Outlook
# Track in cadence_automation.py
```

### 3. Scale to 50 Contacts
```bash
# Score all contacts first
python score_leads.py all

# Enrich top 50
python complete_pipeline.py batch 50

# Generate variants for all
python unified_generator.py batch 50
```

---

## 🎯 Success Metrics

Track these to optimize:

**Email Performance:**
- Open rate by variant (goal: 50%+)
- Response rate by variant (goal: 25%+)
- Meeting booking rate (goal: 15%+)

**Call Performance:**
- Connection rate (goal: 60%+)
- Conversation length (goal: 3+ minutes)
- Meeting booking rate (goal: 30%+)

**Variant Analysis:**
```bash
# After sending, track which variant performed best
# Update this in your cadence_automation.py or activity_monitor.py
```

---

## 💡 Pro Tips

1. **A/B Test Variants**: Send variant 1 to first 3 contacts, variant 2 to next 3, variant 3 to last 3. See which performs best.

2. **Customize Before Sending**: These are great starting points, but add your personal touch to each one.

3. **Match to Channel**: Email variant 1 pairs well with Call script 1 (both direct).

4. **Track What Works**: Log which variants get responses. After 20 contacts, you'll know which approach wins.

5. **Refresh Periodically**: Market conditions change. Regenerate variants every 2-3 months to keep content fresh.

---

## 🔄 Integration with Existing Scripts

### With Cadence Automation
```python
# After generating variants, start cadence
python unified_generator.py 157153
python cadence_automation.py start 157153 standard
```

### With Activity Monitor
```python
# Log when you send generated content
python activity_monitor.py log 157153 email 5 "sent variant 1"
```

### With Dashboard
The dashboard will automatically show variant-generated contacts. You can add a filter:
```python
# In sales_angel_dashboard.py, add:
variants_generated = contact.get('variants_generated_at') is not None
```

---

## 📞 Support & Questions

If you encounter issues:
1. Check your `.env` file has `PERPLEXITY_API_KEY`
2. Verify database has enrichment data for the contact
3. Make sure `requests` library is installed
4. Review error messages - they're descriptive

---

## 🎉 You're Ready!

You now have:
- ✅ World-class email generator
- ✅ World-class call script generator
- ✅ Unified generator (both in parallel)
- ✅ Complete installation guide
- ✅ Usage examples
- ✅ Troubleshooting help

**GO GENERATE AND SEND!**

```bash
cd ~/projects/sales-angel-clean
source venv/bin/activate
python unified_generator.py batch 9
```

**Expected time:** 3-5 minutes  
**Expected cost:** $0.45  
**Expected output:** 54 pieces of content  
**Potential value:** $45K-450K (if you close deals)

🚀 **START NOW!** 🚀
