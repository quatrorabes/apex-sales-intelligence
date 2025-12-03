cd ~/projects/apex/dashboard_v1/src/components/

# Fix TodaysBoard buttons
cat > /tmp/fix_todays_buttons.py << 'FIX'
with open('TodaysBoard.tsx', 'r') as f:
    content = f.read()

# Find the Email button and make it actually work
old_email = '''<a
          href={`mailto:${contact.email}`}
          className="text-xs px-3 py-1 bg-indigo-100 text-indigo-700 rounded hover:bg-indigo-200"
        >
          Email
        </a>'''

new_email = '''<a
          href={`mailto:${contact.email}`}
          onClick={(e) => e.stopPropagation()}
          className="text-xs px-3 py-1 bg-indigo-100 text-indigo-700 rounded hover:bg-indigo-200"
        >
          Email
        </a>'''

content = content.replace(old_email, new_email)

# Make View Profile button actually do something
old_view = '''<button className="text-xs px-3 py-1 bg-gray-100 text-gray-700 rounded hover:bg-gray-200">
          View Profile
        </button>'''

new_view = '''<button 
          onClick={(e) => {
            e.stopPropagation();
            window.location.href = `/contacts/${contact.id}`;
          }}
          className="text-xs px-3 py-1 bg-gray-100 text-gray-700 rounded hover:bg-gray-200"
        >
          View Profile
        </button>'''

content = content.replace(old_view, new_view)

with open('TodaysBoard.tsx', 'w') as f:
    f.write(content)

print('✅ Fixed TodaysBoard buttons!')
FIX

python3 /tmp/fix_todays_buttons.py
