#!/usr/bin/env python3

#!/usr/bin/env python3
"""
Database migration: Add cadence automation tables
"""

import sqlite3
from datetime import datetime

def migrate():
	conn = sqlite3.connect('./apex.db')
	cursor = conn.cursor()
	
	print("🔄 Starting cadence tables migration...")
	
	# 1. Add cadence fields to contacts table
	print("\n📋 Step 1: Adding cadence columns to contacts table...")
	new_columns = [
		("cadence_id", "INTEGER"),
		("cadence_status", "TEXT DEFAULT 'none'"),
		("cadence_started_at", "TEXT"),
		("last_cadence_touch_at", "TEXT")
	]
	
	for col_name, col_type in new_columns:
		try:
			cursor.execute(f"ALTER TABLE contacts ADD COLUMN {col_name} {col_type}")
			print(f"   ✅ Added: {col_name}")
		except sqlite3.OperationalError as e:
			if "duplicate column" in str(e).lower():
				print(f"   ⏭️  Already exists: {col_name}")
			else:
				raise
				
	# 2. Create cadence_sequences table
	print("\n📋 Step 2: Creating cadence_sequences table...")
	cursor.execute("""
		CREATE TABLE IF NOT EXISTS cadence_sequences (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			contact_id INTEGER NOT NULL,
			cadence_type TEXT NOT NULL,
			status TEXT DEFAULT 'active',
			current_step INTEGER DEFAULT 0,
			total_steps INTEGER NOT NULL,
			started_at TEXT NOT NULL,
			last_touch_at TEXT,
			next_touch_at TEXT,
			completed_at TEXT,
			stop_reason TEXT,
			created_at TEXT NOT NULL,
			FOREIGN KEY (contact_id) REFERENCES contacts(id) ON DELETE CASCADE
		)
	""")
	print("   ✅ Created: cadence_sequences")
	
	# 3. Create cadence_touches table
	print("\n📋 Step 3: Creating cadence_touches table...")
	cursor.execute("""
		CREATE TABLE IF NOT EXISTS cadence_touches (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			sequence_id INTEGER NOT NULL,
			contact_id INTEGER NOT NULL,
			step_number INTEGER NOT NULL,
			touch_type TEXT NOT NULL,
			variant_number INTEGER,
			scheduled_for TEXT NOT NULL,
			executed_at TEXT,
			status TEXT DEFAULT 'pending',
			response_received INTEGER DEFAULT 0,
			error_message TEXT,
			created_at TEXT NOT NULL,
			FOREIGN KEY (sequence_id) REFERENCES cadence_sequences(id) ON DELETE CASCADE,
			FOREIGN KEY (contact_id) REFERENCES contacts(id) ON DELETE CASCADE
		)
	""")
	print("   ✅ Created: cadence_touches")
	
	# 4. Create cadence_activities table (for logging)
	print("\n📋 Step 4: Creating cadence_activities table...")
	cursor.execute("""
		CREATE TABLE IF NOT EXISTS cadence_activities (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			contact_id INTEGER NOT NULL,
			sequence_id INTEGER,
			touch_id INTEGER,
			activity_type TEXT NOT NULL,
			activity_data TEXT,
			created_at TEXT NOT NULL,
			FOREIGN KEY (contact_id) REFERENCES contacts(id) ON DELETE CASCADE
		)
	""")
	print("   ✅ Created: cadence_activities")
	
	# 5. Create indexes for performance
	print("\n📋 Step 5: Creating indexes...")
	indexes = [
		("idx_cadence_sequences_contact", "cadence_sequences(contact_id)"),
		("idx_cadence_sequences_status", "cadence_sequences(status)"),
		("idx_cadence_touches_sequence", "cadence_touches(sequence_id)"),
		("idx_cadence_touches_scheduled", "cadence_touches(scheduled_for)"),
		("idx_cadence_touches_status", "cadence_touches(status)"),
		("idx_cadence_activities_contact", "cadence_activities(contact_id)")
	]
	
	for idx_name, idx_def in indexes:
		try:
			cursor.execute(f"CREATE INDEX IF NOT EXISTS {idx_name} ON {idx_def}")
			print(f"   ✅ Created index: {idx_name}")
		except Exception as e:
			print(f"   ⚠️  Index {idx_name}: {e}")
			
	conn.commit()
	conn.close()
	
	print("\n✅ Migration completed successfully!")
	print("\n📊 Summary:")
	print("   • Added 4 columns to contacts table")
	print("   • Created 3 new tables (sequences, touches, activities)")
	print("   • Created 6 indexes for query performance")
	
if __name__ == "__main__":
	migrate()
	