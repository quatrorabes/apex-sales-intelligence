import sqlite3

conn = sqlite3.connect('./apex.db')
cursor = conn.cursor()

# First, check what columns actually exist
print("\nChecking database schema...")
cursor.execute("PRAGMA table_info(contacts)")
columns = cursor.fetchall()
column_names = [col[1] for col in columns]

print(f"\nExisting columns in contacts table:")
for col in column_names:
    print(f"  - {col}")

# Check which name-related columns exist
has_firstname = 'firstname' in column_names
has_lastname = 'lastname' in column_names
has_name = 'name' in column_names
has_email = 'email' in column_names
has_company = 'company' in column_names

print(f"\nName columns available:")
print(f"  - name: {'✅' if has_name else '❌'}")
print(f"  - firstname: {'✅' if has_firstname else '❌'}")
print(f"  - lastname: {'✅' if has_lastname else '❌'}")

# Build query based on available columns
select_parts = ['id']
if has_name:
    select_parts.append('name')
if has_firstname:
    select_parts.append('firstname')
if has_lastname:
    select_parts.append('lastname')
if has_company:
    select_parts.append('company')
if has_email:
    select_parts.append('email')

# Build WHERE clause based on available name columns
where_conditions = []
if has_name:
    where_conditions.append("(name IS NULL OR name = '' OR name = ' ')")
if has_firstname:
    where_conditions.append("(firstname IS NULL OR firstname = '')")
if has_lastname:
    where_conditions.append("(lastname IS NULL OR lastname = '')")

if where_conditions and has_company:
    query = f'''
        SELECT {', '.join(select_parts)}
        FROM contacts 
        WHERE ({' AND '.join(where_conditions)})
        AND company IS NOT NULL
        LIMIT 10
    '''

    print(f"\nChecking contacts with missing names...")
    cursor.execute(query)

    rows = cursor.fetchall()
    if rows:
        print(f"\nFound {len(rows)} contacts with missing names:")
        for row in rows:
            contact_id = row[0]
            # Build display based on available data
            display_parts = [f"ID {contact_id}:"]

            # Add available fields to display
            idx = 1
            if has_name and idx < len(row):
                display_parts.append(f"name='{row[idx]}'")
                idx += 1
            if has_firstname and idx < len(row):
                display_parts.append(f"firstname='{row[idx]}'")
                idx += 1
            if has_lastname and idx < len(row):
                display_parts.append(f"lastname='{row[idx]}'")
                idx += 1
            if has_company and idx < len(row):
                display_parts.append(f"company='{row[idx]}'")
                idx += 1
            if has_email and idx < len(row):
                display_parts.append(f"email='{row[idx]}'")

            print(f"  {' | '.join(display_parts)}")

        print(f"\nTo fix missing names, use SQL like:")
        if has_name and has_firstname and has_lastname:
            print(f"  UPDATE contacts SET name='John Smith', firstname='John', lastname='Smith' WHERE id=X;")
        elif has_name:
            print(f"  UPDATE contacts SET name='John Smith' WHERE id=X;")
        else:
            print(f"  You may need to add name columns to your table first.")
    else:
        print("✅ All contacts have names (or no contacts exist with companies)!")
else:
    print("\n⚠️ No name columns found or no company column exists")
    print("\nSample of contacts in database:")
    cursor.execute(f"SELECT {', '.join(select_parts)} FROM contacts LIMIT 5")
    rows = cursor.fetchall()
    for row in rows:
        print(f"  {row}")

conn.close()
