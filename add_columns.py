#!/usr/bin/env python3

import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

DB_URL = os.getenv('DATABASE_URL')

if not DB_URL:
	print("❌ No DATABASE_URL found in .env")
	exit(1)
	
conn = psycopg2.connect(DB_URL)
conn.autocommit = True
cursor = conn.cursor()

columns = [
	"overview TEXT",
	"background TEXT",
	"education TEXT",
	"recent_mentions TEXT",
	"social_profiles TEXT",
	"personality_detail TEXT",
	"mb_summary TEXT",
	"company_overview TEXT",
	"company_products_services TEXT",
	"company_leadership TEXT",
	"company_market_competitors TEXT",
	"company_recent_news TEXT",
	"company_fun_facts TEXT",
	"sales_talking_points TEXT",
	"deals_history TEXT",
	"fun_facts TEXT"
]

print(f"🔌 Connected to database...")

for col in columns:
	col_name = col.split()[0]
	try:
		cursor.execute(f"ALTER TABLE contacts ADD COLUMN {col};")
		print(f"✅ Added column: {col_name}")
	except psycopg2.errors.DuplicateColumn:
		print(f"⚠️ Column already exists: {col_name}")
	except Exception as e:
		print(f"❌ Error adding {col_name}: {e}")
		
conn.close()
print("🎉 Migration complete!")
