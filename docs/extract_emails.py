#!/usr/bin/env python3
"""
SIMPLE EMAIL EXTRACTOR FOR SALES ANGEL
Run this to get your 9 enriched contacts' email content ready to send
"""

import sqlite3
import os
from pathlib import Path

# Database location
db_path = Path.home() / "projects/sales-angel-clean/sales_angel.db"

print("🔍 Connecting to Sales Angel database...")
print(f"📂 Location: {db_path}\n")

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get enriched contacts
    query = """
    SELECT 
        id, firstname, lastname, email, company, jobtitle, score, tier,
        email_1_subject, email_1_body,
        email_2_subject, email_2_body,
        email_3_subject, email_3_body
    FROM contacts 
    WHERE enriched = 1
    ORDER BY score DESC;
    """
    
    cursor.execute(query)
    contacts = cursor.fetchall()
    
    print(f"✅ Found {len(contacts)} enriched contacts\n")
    print("="*80)
    
    # Create individual email files for each contact
    output_dir = Path.home() / "projects/sales-angel-clean/emails_ready_to_send"
    output_dir.mkdir(exist_ok=True)
    
    for contact in contacts:
        contact_id = contact[0]
        firstname = contact[1]
        lastname = contact[2]
        email = contact[3]
        company = contact[4]
        jobtitle = contact[5]
        score = contact[6]
        tier = contact[7]
        
        print(f"\n📧 {firstname} {lastname} ({email})")
        print(f"   {company} | Score: {score} ({tier})")
        
        # Create file for each email sequence
        for i in range(1, 4):
            subject_idx = 8 + (i-1)*2
            body_idx = 9 + (i-1)*2
            
            subject = contact[subject_idx]
            body = contact[body_idx]
            
            if subject and body:
                filename = f"{contact_id}_{firstname}_{lastname}_email_{i}.txt"
                filepath = output_dir / filename
                
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(f"TO: {email}\n")
                    f.write(f"FROM: Your Name <your.email@company.com>\n")
                    f.write(f"SUBJECT: {subject}\n")
                    f.write(f"\n{'='*60}\n\n")
                    f.write(body)
                    f.write(f"\n\n{'='*60}\n")
                    f.write(f"\nCONTACT INFO:\n")
                    f.write(f"Name: {firstname} {lastname}\n")
                    f.write(f"Company: {company}\n")
                    f.write(f"Title: {jobtitle}\n")
                    f.write(f"Email: {email}\n")
                    f.write(f"Score: {score} ({tier})\n")
                
                print(f"   ✅ Email {i} saved: {filename}")
    
    conn.close()
    
    print("\n" + "="*80)
    print(f"\n🎉 SUCCESS! All emails extracted to:\n   {output_dir}")
    print(f"\n📊 Total files created: {len(contacts) * 3}")
    print("\n🚀 NEXT STEPS:")
    print("   1. Open the 'emails_ready_to_send' folder")
    print("   2. Open each .txt file")
    print("   3. Copy the content")
    print("   4. Paste into Gmail/Outlook")
    print("   5. Send!")
    print("\n💡 TIP: Start with Email 1 for all contacts, then send Email 2 a week later.")
    
except FileNotFoundError:
    print("❌ ERROR: Database not found!")
    print(f"   Expected location: {db_path}")
    print("\n   Make sure you're running this from the correct directory.")
except Exception as e:
    print(f"❌ ERROR: {e}")
    print("\n   Contact support or check your database file.")
