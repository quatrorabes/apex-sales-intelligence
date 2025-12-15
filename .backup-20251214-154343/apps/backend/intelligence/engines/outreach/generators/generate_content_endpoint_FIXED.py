@app.route('/api/contacts/<int:contact_id>/generate-content', methods=['POST'])
def generate_content(contact_id):
    """Generate 3 emails, 3 call scripts, and 2 LinkedIn messages for a contact"""
    try:
        data = request.json or {}
        content_type = data.get('type', 'all')
        
        logger.info(f"🎯 Generating content type: '{content_type}' for contact {contact_id}")
        
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM contacts WHERE id = ?", (contact_id,))
        row = cursor.fetchone()
        
        if not row:
            conn.close()
            return jsonify({"error": "Contact not found"}), 404
        
        contact = dict(row)
        
        if not contact.get('profile_content'):
            conn.close()
            return jsonify({"error": "Contact needs to be enriched first"}), 400
        
        if not OPENAI_API_KEY:
            conn.close()
            return jsonify({"error": "OpenAI API key not configured"}), 500
        
        client = OpenAI(api_key=OPENAI_API_KEY)
        
        results = {}
        enrichment_text = contact.get('profile_content', '')[:2000]
        contact_name = f"{contact.get('firstname', '')} {contact.get('lastname', '')}".strip()
        
        logger.info(f"📝 Contact: {contact_name} | Enrichment: {len(enrichment_text)} chars")
        
        # Generate 3 EMAILS
        if content_type in ['all', 'email']:
            logger.info(f"✉️ Generating 3-email sequence...")
            
            email_prompt = f"""Generate a 3-email outreach sequence for:

Name: {contact_name}
Title: {contact.get('title', '')}
Company: {contact.get('company', '')}

INTELLIGENCE:
{enrichment_text}

Create exactly 3 emails:

EMAIL 1 - INTRODUCTION (Day 1)
- Hook with specific detail from their profile
- Establish credibility quickly
- One clear value proposition
- Soft ask for 15-min call

EMAIL 2 - VALUE ADD (Day 4 - if no response)
- Share relevant insight or resource
- Reference industry challenge they face
- Reinforce value
- Another CTA

EMAIL 3 - BREAKUP (Day 7 - if no response)
- Acknowledge they're busy
- Final value statement
- Leave door open
- Different CTA (resource, connection, etc.)

Format each as:
---EMAIL 1---
Subject: [subject line]

[body]

---EMAIL 2---
Subject: [subject line]

[body]

---EMAIL 3---
Subject: [subject line]

[body]"""

            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are an expert B2B sales copywriter who writes hyper-personalized, conversion-optimized emails."},
                    {"role": "user", "content": email_prompt}
                ],
                temperature=0.7,
                max_tokens=1500
            )
            
            email_content = response.choices[0].message.content
            
            # Parse the 3 emails
            emails = []
            email_parts = email_content.split('---EMAIL')
            
            for i, part in enumerate(email_parts[1:], 1):  # Skip first empty part
                if '---' in part:
                    email_text = part.split('---')[0].strip()
                    
                    subject = ""
                    body = email_text
                    
                    if "Subject:" in email_text:
                        lines = email_text.split('\n', 1)
                        subject = lines[0].replace('Subject:', '').strip()
                        body = lines[1].strip() if len(lines) > 1 else email_text
                    
                    emails.append({
                        'subject': subject,
                        'body': body,
                        'generatedat': datetime.now().isoformat()
                    })
            
            results['emails'] = emails
            logger.info(f"✅ Generated {len(emails)} emails")
        
        # Generate 3 CALL SCRIPTS
        if content_type in ['all', 'call']:
            logger.info(f"📞 Generating 3 call scripts...")
            
            call_prompt = f"""Generate 3 phone call scripts for:

Name: {contact_name}
Title: {contact.get('title', '')}
Company: {contact.get('company', '')}

INTELLIGENCE:
{enrichment_text}

Create exactly 3 scripts:

SCRIPT 1 - COLD CALL
- Permission-based opening
- Reason for call (reference specific detail)
- Value hypothesis
- Ask for meeting
- Handle objections

SCRIPT 2 - FOLLOW-UP CALL
- Reference previous touchpoint
- New insight or value
- Discovery questions
- Next steps

SCRIPT 3 - EXECUTIVE BRIEFING
- Executive summary opener
- 3 key discovery questions based on their role
- Value alignment
- Clear next steps

Format each with:
- Opening
- Body/Value Prop
- Discovery Questions (3-5)
- Objection Handling
- Close/Next Steps

Make them conversational, not robotic!

Format as:
---SCRIPT 1: COLD CALL---
[script content]

---SCRIPT 2: FOLLOW-UP---
[script content]

---SCRIPT 3: EXECUTIVE BRIEFING---
[script content]"""

            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are an expert sales trainer who creates effective, natural call scripts."},
                    {"role": "user", "content": call_prompt}
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            script_content = response.choices[0].message.content
            
            # Parse the 3 scripts
            scripts = []
            script_parts = script_content.split('---SCRIPT')
            
            for i, part in enumerate(script_parts[1:], 1):  # Skip first empty part
                if '---' in part:
                    script_text = part.split('---')[0].strip()
                    # Remove the header line (e.g., "1: COLD CALL")
                    if '\n' in script_text:
                        script_text = '\n'.join(script_text.split('\n')[1:]).strip()
                    
                    scripts.append({
                        'script': script_text,
                        'generatedat': datetime.now().isoformat()
                    })
            
            results['call_scripts'] = scripts
            logger.info(f"✅ Generated {len(scripts)} call scripts")
        
        # Generate 2 LINKEDIN MESSAGES
        if content_type in ['all', 'linkedin']:
            logger.info(f"💼 Generating 2 LinkedIn messages...")
            
            linkedin_prompt = f"""Generate 2 LinkedIn messages for:

Name: {contact_name}
Company: {contact.get('company', '')}

INTELLIGENCE:
{enrichment_text[:500]}

Create exactly 2 messages:

MESSAGE 1 - CONNECTION REQUEST
- Under 300 characters (LinkedIn limit)
- Warm and professional
- Reference something specific from their background
- No sales pitch in connection request!

MESSAGE 2 - FOLLOW-UP MESSAGE (if they accept)
- Professional but conversational
- Value-oriented
- Clear reason to connect
- Soft ask for conversation

Format as:
---MESSAGE 1: CONNECTION REQUEST---
[message under 300 chars]

---MESSAGE 2: FOLLOW-UP---
[message]"""

            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You write engaging LinkedIn connection requests that get accepted."},
                    {"role": "user", "content": linkedin_prompt}
                ],
                temperature=0.7,
                max_tokens=400
            )
            
            linkedin_content = response.choices[0].message.content
            
            # Parse the 2 messages
            messages = []
            message_parts = linkedin_content.split('---MESSAGE')
            
            for i, part in enumerate(message_parts[1:], 1):  # Skip first empty part
                if '---' in part:
                    message_text = part.split('---')[0].strip()
                    # Remove the header line
                    if '\n' in message_text:
                        message_text = '\n'.join(message_text.split('\n')[1:]).strip()
                    
                    messages.append({
                        'message': message_text,
                        'generatedat': datetime.now().isoformat()
                    })
            
            results['linkedin_messages'] = messages
            logger.info(f"✅ Generated {len(messages)} LinkedIn messages")
        
        conn.close()
        
        total_count = len(results.get('emails', [])) + len(results.get('call_scripts', [])) + len(results.get('linkedin_messages', []))
        logger.info(f"🎉 COMPLETE - Generated {total_count} total pieces of content")
        logger.info(f"   📧 {len(results.get('emails', []))} emails")
        logger.info(f"   📞 {len(results.get('call_scripts', []))} call scripts")
        logger.info(f"   💼 {len(results.get('linkedin_messages', []))} LinkedIn messages")
        
        return jsonify({
            "success": True,
            "contact_id": contact_id,
            "results": results
        })
        
    except Exception as e:
        logger.error(f"❌ Content generation error: {e}")
        traceback.print_exc()
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500
