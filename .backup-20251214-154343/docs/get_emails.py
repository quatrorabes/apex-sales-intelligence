#!/usr/bin/env python3
"""
SALES ANGEL - EMAIL CONTENT EXTRACTOR
Quick script to get ready-to-send emails from database
"""

import sqlite3
import sys

DB_PATH = "sales_angel.db"

def get_all_enriched():
    """List all enriched contacts"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    contacts = cursor.execute("""
        SELECT id, firstname, lastname, email, company, mdcp_score, tier
        FROM contacts 
        WHERE enriched = 1
        ORDER BY mdcp_score DESC
    """).fetchall()
    
    print("\n" + "="*80)
    print("🎯 ENRICHED CONTACTS READY FOR OUTREACH")
    print("="*80 + "\n")
    
    for id, fname, lname, email, company, score, tier in contacts:
        print(f"ID: {id}")
        print(f"Name: {fname} {lname}")
        print(f"Email: {email}")
        print(f"Company: {company}")
        print(f"Score: {score} ({tier})")
        print("-" * 80)
    
    conn.close()
    return contacts

def get_email_content(contact_id, email_num=1):
    """Get specific email for a contact"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Get contact info and email
    result = cursor.execute(f"""
        SELECT 
            firstname, lastname, email, company,
            email_{email_num}_subject, email_{email_num}_body
        FROM contacts 
        WHERE id = ?
    """, (contact_id,)).fetchone()
    
    if not result:
        print(f"❌ Contact {contact_id} not found or not enriched")
        conn.close()
        return None
    
    fname, lname, email, company, subject, body = result
    
    print("\n" + "="*80)
    print(f"📧 EMAIL {email_num} FOR {fname} {lname}")
    print("="*80)
    print(f"\n👤 TO: {fname} {lname} <{email}>")
    print(f"🏢 COMPANY: {company}")
    print(f"📬 SUBJECT: {subject}")
    print("\n" + "-"*80)
    print("📝 BODY:")
    print("-"*80 + "\n")
    print(body)
    print("\n" + "="*80)
    print("✅ READY TO COPY/PASTE INTO GMAIL")
    print("="*80 + "\n")
    
    conn.close()
    return {
        'to': email,
        'to_name': f"{fname} {lname}",
        'company': company,
        'subject': subject,
        'body': body
    }

def get_all_emails_for_contact(contact_id):
    """Get all 3 emails for a contact"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    result = cursor.execute("""
        SELECT 
            firstname, lastname, email, company,
            email_1_subject, email_1_body,
            email_2_subject, email_2_body,
            email_3_subject, email_3_body,
            call_script_1, linkedin_note
        FROM contacts 
        WHERE id = ?
    """, (contact_id,)).fetchone()
    
    if not result:
        print(f"❌ Contact {contact_id} not found")
        conn.close()
        return
    
    fname, lname, email, company = result[:4]
    
    print("\n" + "="*80)
    print(f"📧 ALL OUTREACH CONTENT FOR {fname} {lname}")
    print("="*80)
    print(f"\n👤 CONTACT: {fname} {lname}")
    print(f"📧 EMAIL: {email}")
    print(f"🏢 COMPANY: {company}")
    print("\n" + "="*80)
    
    # Email 1
    print("\n📧 EMAIL #1 (Initial Outreach)")
    print("-"*80)
    print(f"SUBJECT: {result[4]}")
    print(f"\n{result[5]}\n")
    
    # Email 2
    print("\n📧 EMAIL #2 (Follow-up)")
    print("-"*80)
    print(f"SUBJECT: {result[6]}")
    print(f"\n{result[7]}\n")
    
    # Email 3
    print("\n📧 EMAIL #3 (Final Touch)")
    print("-"*80)
    print(f"SUBJECT: {result[8]}")
    print(f"\n{result[9]}\n")
    
    # Call Script
    print("\n📞 CALL SCRIPT")
    print("-"*80)
    print(result[10])
    
    # LinkedIn
    print("\n\n🔗 LINKEDIN CONNECTION MESSAGE")
    print("-"*80)
    print(result[11])
    
    print("\n" + "="*80)
    print("✅ ALL CONTENT READY!")
    print("="*80 + "\n")
    
    conn.close()

def export_to_csv():
    """Export all enriched contacts to CSV"""
    import csv
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    contacts = cursor.execute("""
        SELECT 
            id, firstname, lastname, email, company,
            email_1_subject, email_1_body,
            email_2_subject, email_2_body,
            email_3_subject, email_3_body
        FROM contacts 
        WHERE enriched = 1
        ORDER BY mdcp_score DESC
    """).fetchall()
    
    filename = f"enriched_contacts_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([
            'ID', 'First Name', 'Last Name', 'Email', 'Company',
            'Email 1 Subject', 'Email 1 Body',
            'Email 2 Subject', 'Email 2 Body',
            'Email 3 Subject', 'Email 3 Body'
        ])
        writer.writerows(contacts)
    
    print(f"\n✅ Exported {len(contacts)} contacts to {filename}")
    conn.close()

def main():
    """Main function with menu"""
    
    if len(sys.argv) > 1:
        # Command line usage
        command = sys.argv[1]
        
        if command == "list":
            get_all_enriched()
        
        elif command == "view" and len(sys.argv) > 2:
            contact_id = int(sys.argv[2])
            get_all_emails_for_contact(contact_id)
        
        elif command == "email" and len(sys.argv) > 2:
            contact_id = int(sys.argv[2])
            email_num = int(sys.argv[3]) if len(sys.argv) > 3 else 1
            get_email_content(contact_id, email_num)
        
        elif command == "export":
            export_to_csv()
        
        else:
            print("Usage:")
            print("  python get_emails.py list           - List all enriched contacts")
            print("  python get_emails.py view <id>      - View all content for contact")
            print("  python get_emails.py email <id> <#> - Get specific email (1-3)")
            print("  python get_emails.py export         - Export to CSV")
    
    else:
        # Interactive menu
        print("\n" + "="*80)
        print("🚀 SALES ANGEL - EMAIL CONTENT EXTRACTOR")
        print("="*80)
        print("\n1. List all enriched contacts")
        print("2. View all content for a contact")
        print("3. Get specific email to send")
        print("4. Export to CSV")
        print("5. Exit")
        
        choice = input("\nSelect option (1-5): ")
        
        if choice == "1":
            get_all_enriched()
        
        elif choice == "2":
            contact_id = int(input("Enter contact ID: "))
            get_all_emails_for_contact(contact_id)
        
        elif choice == "3":
            contact_id = int(input("Enter contact ID: "))
            email_num = int(input("Enter email number (1-3): "))
            content = get_email_content(contact_id, email_num)
            
            if content:
                print("\n📋 TO SEND THIS EMAIL:")
                print("1. Open Gmail/Outlook")
                print(f"2. To: {content['to']}")
                print(f"3. Subject: {content['subject']}")
                print("4. Copy the body text above")
                print("5. Send!")
        
        elif choice == "4":
            from datetime import datetime
            export_to_csv()
        
        elif choice == "5":
            print("\n👋 Goodbye!")
            return
        
        # Ask if they want to continue
        if input("\nView another? (y/n): ").lower() == 'y':
            main()

if __name__ == "__main__":
    main()
