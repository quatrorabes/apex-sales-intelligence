import sqlite3

print("Adding firstname and lastname columns if missing...")

conn = sqlite3.connect('./apex.db')
cursor = conn.cursor()

# Check existing columns
cursor.execute("PRAGMA table_info(contacts)")
existing_columns = [column[1] for column in cursor.fetchall()]

# Add firstname if missing
if 'firstname' not in existing_columns:
    try:
        cursor.execute("ALTER TABLE contacts ADD COLUMN firstname VARCHAR(100)")
        conn.commit()
        print("✅ Added firstname column")
    except sqlite3.OperationalError as e:
        print(f"⚠️ Could not add firstname: {e}")
else:
    print("⏭️  firstname column already exists")

# Add lastname if missing  
if 'lastname' not in existing_columns:
    try:
        cursor.execute("ALTER TABLE contacts ADD COLUMN lastname VARCHAR(100)")
        conn.commit()
        print("✅ Added lastname column")
    except sqlite3.OperationalError as e:
        print(f"⚠️ Could not add lastname: {e}")
else:
    print("⏭️  lastname column already exists")

# Now try to populate firstname/lastname from name field
if 'name' in existing_columns:
    cursor.execute('''
        SELECT id, name 
        FROM contacts 
        WHERE name IS NOT NULL 
        AND name != ''
        AND (firstname IS NULL OR firstname = '')
    ''')

    contacts_to_update = cursor.fetchall()

    if contacts_to_update:
        print(f"\nFound {len(contacts_to_update)} contacts to split names...")
        for contact_id, full_name in contacts_to_update:
            if full_name and ' ' in full_name:
                parts = full_name.split(' ', 1)
                firstname = parts[0]
                lastname = parts[1] if len(parts) > 1 else ''

                cursor.execute(
                    "UPDATE contacts SET firstname = ?, lastname = ? WHERE id = ?",
                    (firstname, lastname, contact_id)
                )
                print(f"  Updated ID {contact_id}: {firstname} {lastname}")

        conn.commit()
        print("✅ Name splitting complete")
    else:
        print("✅ All contacts already have firstname/lastname or no names to split")

conn.close()
print("\n✅ Migration complete!")
