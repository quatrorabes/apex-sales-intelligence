import sqlite3

conn = sqlite3.connect('./apex.db')
cursor = conn.cursor()

print("\nChecking contacts with missing names:")
cursor.execute('''
    SELECT id, name, firstname, lastname, company, email 
    FROM contacts 
    WHERE (name IS NULL OR name = '' OR name = ' ')
    AND company IS NOT NULL
    LIMIT 10
''')

rows = cursor.fetchall()
if rows:
    print("\nContacts missing names:")
    for row in rows:
        print(f"  ID {row[0]}: {row[4]} @ {row[3]} (email: {row[5]})")
    print(f"\nTo fix, update names in database:")
    print(f"  UPDATE contacts SET name='John Smith', firstname='John', lastname='Smith' WHERE id=X;")
else:
    print("✅ All contacts have names!")

conn.close()
