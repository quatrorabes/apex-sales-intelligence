#!/usr/bin/env python3

#!/usr/bin/env python3
"""
Profile Management and Content Generation System
Full context storage and retrieval
"""
import os
import sqlite3
import json
from datetime import datetime
from typing import Dict, Optional
from dataclasses import dataclass, asdict
from flask import Flask, request, jsonify, render_template_string
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Data Models
@dataclass
class UserProfile:
	"""The seller's profile"""
	user_name: str
	user_email: str
	user_phone: str
	user_title: str
	user_company: str
	user_bio: str
	user_style: str
	user_value_props: str
	user_industry_focus: str
	
	@classmethod
	def load_chris(cls):
		"""Load Chris's profile as default"""
		return cls(
			user_name="Chris Rabenold",
			user_email="crabenold@harvestcref.com",
			user_phone="310-363-9346",
			user_title="Senior Vice President, Business Development",
			user_company="Harvest Small Business Finance",
			user_bio="""Over 20 years in SBA and conventional CRE lending. 
						Previously at Greystone, Plaza Bank, Cathay Bank. 
						Specializes in owner-occupied commercial real estate.""",
			user_style="Professional casual, direct, no corporate speak",
			user_value_props="""SBA 504 loans with 10% down for owner-occupied CRE.
								Help businesses build equity instead of paying rent.
								90% financing available for qualified borrowers.""",
			user_industry_focus="Commercial real estate, small business finance"
		)
	
@dataclass  
class RelationshipContext:
	"""Relationship between user and contact"""
	relationship_level: str = 'cold'
	years_known: int = 0
	last_interaction: str = ''
	common_ground: list = None
	referral_potential: str = ''
	personal_notes: str = ''
	professional_notes: str = ''
	
	def to_json(self):
		return json.dumps(asdict(self))
	
class ProfileManager:
	"""Manage all profile data"""
	
	def __init__(self, db_path="~/projects/apex/apex.db"):
		self.db_path = os.path.expanduser(db_path)
		self.ensure_tables()
		
	def ensure_tables(self):
		"""Create tables if they don't exist"""
		conn = sqlite3.connect(self.db_path)
		cursor = conn.cursor()
		
		# Check if tables exist, create if not
		cursor.execute("""
			CREATE TABLE IF NOT EXISTS user_profiles (
				id INTEGER PRIMARY KEY AUTOINCREMENT,
				user_name TEXT NOT NULL,
				user_email TEXT,
				user_phone TEXT,
				user_title TEXT,
				user_company TEXT,
				user_bio TEXT,
				user_style TEXT,
				user_value_props TEXT,
				user_industry_focus TEXT,
				created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
			)
		""")
		
		cursor.execute("""
			CREATE TABLE IF NOT EXISTS relationship_mapping (
				id INTEGER PRIMARY KEY AUTOINCREMENT,
				contact_id INTEGER,
				relationship_level TEXT DEFAULT 'cold',
				years_known INTEGER DEFAULT 0,
				last_interaction TEXT,
				common_ground TEXT,
				referral_potential TEXT,
				personal_notes TEXT,
				professional_notes TEXT,
				updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
			)
		""")
		
		conn.commit()
		conn.close()
		
	def save_user_profile(self, profile: UserProfile) -> int:
		"""Save or update user profile"""
		conn = sqlite3.connect(self.db_path)
		cursor = conn.cursor()
		
		cursor.execute("""
			INSERT OR REPLACE INTO user_profiles 
			(user_name, user_email, user_phone, user_title, user_company,
			user_bio, user_style, user_value_props, user_industry_focus)
			VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
		""", (
			profile.user_name, profile.user_email, profile.user_phone,
			profile.user_title, profile.user_company, profile.user_bio,
			profile.user_style, profile.user_value_props, profile.user_industry_focus
		))
		
		user_id = cursor.lastrowid
		conn.commit()
		conn.close()
		return user_id
	
	def get_or_create_relationship(self, contact_id: int) -> RelationshipContext:
		"""Get existing relationship or create new"""
		conn = sqlite3.connect(self.db_path)
		conn.row_factory = sqlite3.Row
		cursor = conn.cursor()
		
		cursor.execute("""
			SELECT * FROM relationship_mapping 
			WHERE contact_id = ?
		""", (contact_id,))
		
		row = cursor.fetchone()
		
		if row:
			context = RelationshipContext(
				relationship_level=row['relationship_level'],
				years_known=row['years_known'],
				last_interaction=row['last_interaction'] or '',
				common_ground=json.loads(row['common_ground']) if row['common_ground'] else [],
				referral_potential=row['referral_potential'] or '',
				personal_notes=row['personal_notes'] or '',
				professional_notes=row['professional_notes'] or ''
			)
		else:
			# Check if it's Andy or someone specific
			cursor.execute("SELECT name FROM contacts WHERE id = ?", (contact_id,))
			contact = cursor.fetchone()
			
			if contact and "Andy Bratt" in contact['name']:
				context = RelationshipContext(
					relationship_level='connected',
					years_known=10,
					last_interaction='NAIOP event 2 months ago',
					common_ground=['NAIOP', 'CRE finance', 'Newport Beach'],
					referral_potential='High - complementary services',
					professional_notes='Gantry does big loans, we do SBA'
				)
				# Save this
				self.save_relationship(contact_id, context)
			else:
				context = RelationshipContext()
				
		conn.close()
		return context
	
	def save_relationship(self, contact_id: int, context: RelationshipContext):
		"""Save relationship context"""
		conn = sqlite3.connect(self.db_path)
		cursor = conn.cursor()
		
		cursor.execute("""
			INSERT OR REPLACE INTO relationship_mapping
			(contact_id, relationship_level, years_known, last_interaction,
			common_ground, referral_potential, personal_notes, professional_notes)
			VALUES (?, ?, ?, ?, ?, ?, ?, ?)
		""", (
			contact_id, context.relationship_level, context.years_known,
			context.last_interaction, json.dumps(context.common_ground),
			context.referral_potential, context.personal_notes, 
			context.professional_notes
		))
		
		conn.commit()
		conn.close()
		
class ContentGenerator:
	"""Generate authentic content with full context"""
	
	def __init__(self, profile_manager: ProfileManager):
		self.pm = profile_manager
		self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
		
	def generate(self, contact_id: int, channel: str = "email") -> str:
		"""Generate content with full context"""
		
		# Get all context
		user = UserProfile.load_chris()  # Or load from DB
		relationship = self.pm.get_or_create_relationship(contact_id)
		
		# Get contact data
		conn = sqlite3.connect(self.pm.db_path)
		conn.row_factory = sqlite3.Row
		cursor = conn.cursor()
		
		cursor.execute("SELECT * FROM contacts WHERE id = ?", (contact_id,))
		contact = dict(cursor.fetchone())
		
		# Get enrichment
		intel = ""
		if contact.get('enrichment_data'):
			data = json.loads(contact['enrichment_data'])
			intel = data.get('perplexity_insights', '')[:1000]
			
		conn.close()
		
		# Build comprehensive prompt
		prompt = self.build_prompt(user, contact, relationship, intel, channel)
		
		# Generate
		response = self.client.chat.completions.create(
			model="gpt-4o",
			messages=[
				{"role": "system", "content": self.get_system_prompt(relationship.relationship_level)},
				{"role": "user", "content": prompt}
			],
			temperature=0.7
		)
		
		content = response.choices[0].message.content
		
		# Save generated content
		self.save_content(contact_id, channel, content, relationship.to_json())
		
		return content
	
	def build_prompt(self, user, contact, relationship, intel, channel):
		"""Build comprehensive context prompt"""
		
		prompt = f"""
SENDER PROFILE:
- Name: {user.user_name}
- Company: {user.user_company}
- Role: {user.user_title}
- Value Props: {user.user_value_props}
- Style: {user.user_style}

RECIPIENT PROFILE:
- Name: {contact['name']}
- Company: {contact['company']}
- Title: {contact['title']}
- Email: {contact['email']}

RELATIONSHIP CONTEXT:
- Level: {relationship.relationship_level}
- Years Known: {relationship.years_known}
- Last Interaction: {relationship.last_interaction}
- Common Ground: {', '.join(relationship.common_ground) if relationship.common_ground else 'None'}
- Notes: {relationship.professional_notes}

INTELLIGENCE:
{intel[:500] if intel else 'No additional intelligence available'}

TASK: Write a {channel} message that:
1. Matches the relationship depth (don't be too familiar if cold)
2. References something specific if relationship exists
3. Has a clear business purpose
4. Sounds like {user.user_name} actually wrote it

Keep it under {"50 words" if channel == "text" else "75 words"}.
"""
		return prompt
		
	def get_system_prompt(self, relationship_level):
		"""System prompt based on relationship"""
		if relationship_level in ['connected', 'close']:
			return "Write like messaging a business friend. Natural, no corporate speak."
		elif relationship_level == 'warm':
			return "Write friendly but professional. You've met but aren't close."
		else:
			return "Write a professional introduction with specific value. Don't be too familiar."
		
	def save_content(self, contact_id, channel, content, context):
		"""Save generated content"""
		conn = sqlite3.connect(self.pm.db_path)
		cursor = conn.cursor()
		
		cursor.execute("""
			INSERT INTO generated_content
			(contact_id, channel, generated_content, relationship_context, ai_model)
			VALUES (?, ?, ?, ?, ?)
		""", (contact_id, channel, content, context, "gpt-4o"))
		
		conn.commit()
		conn.close()
		
# Flask Routes for Web Interface
@app.route('/')
def home():
	"""Main interface"""
	return render_template_string('''
	<!DOCTYPE html>
	<html>
	<head>
		<title>APEX Content Generator</title>
		<style>
			body { font-family: Arial; padding: 20px; max-width: 1200px; margin: auto; }
			.container { display: flex; gap: 20px; }
			.panel { flex: 1; border: 1px solid #ddd; padding: 15px; border-radius: 5px; }
			textarea { width: 100%; height: 100px; }
			button { background: #007bff; color: white; padding: 10px 20px; border: none; cursor: pointer; }
			.generated { background: #f0f8ff; padding: 10px; margin-top: 10px; border-radius: 5px; }
		</style>
	</head>
	<body>
		<h1>🎯 APEX Authentic Content Generator</h1>
		
		<div class="container">
			<div class="panel">
				<h3>Contact Selection</h3>
				<select id="contact_id" style="width: 100%; padding: 5px;">
					<option value="">Loading contacts...</option>
				</select>
				
				<h4>Relationship Context</h4>
				<label>Relationship Level:</label>
				<select id="relationship_level">
					<option value="cold">Cold - Never met</option>
					<option value="warm">Warm - Met once/twice</option>
					<option value="familiar">Familiar - See at events</option>
					<option value="connected">Connected - Regular contact</option>
					<option value="close">Close - Actual friends</option>
				</select>
				
				<label>Years Known:</label>
				<input type="number" id="years_known" value="0" style="width: 50px;">
				
				<label>Last Interaction:</label>
				<input type="text" id="last_interaction" placeholder="e.g., NAIOP event last month">
				
				<label>Notes:</label>
				<textarea id="notes" placeholder="Any relevant context..."></textarea>
			</div>
			
			<div class="panel">
				<h3>Generate Content</h3>
				<label>Channel:</label>
				<select id="channel">
					<option value="email">Email</option>
					<option value="text">Text/SMS</option>
					<option value="linkedin">LinkedIn</option>
					<option value="call">Call Script</option>
				</select>
				
				<br><br>
				<button onclick="generateContent()">Generate Content</button>
				
				<div id="output" class="generated" style="display:none;">
					<h4>Generated Content:</h4>
					<div id="content"></div>
				</div>
			</div>
		</div>
		
		<script>
			// Load contacts
			fetch('/api/contacts')
				.then(r => r.json())
				.then(contacts => {
					const select = document.getElementById('contact_id');
					select.innerHTML = contacts.map(c => 
						`<option value="${c.id}">${c.name} - ${c.company}</option>`
					).join('');
				});
			
			function generateContent() {
				const data = {
					contact_id: document.getElementById('contact_id').value,
					channel: document.getElementById('channel').value,
					relationship: {
						level: document.getElementById('relationship_level').value,
						years_known: document.getElementById('years_known').value,
						last_interaction: document.getElementById('last_interaction').value,
						notes: document.getElementById('notes').value
					}
				};
				
				fetch('/api/generate', {
					method: 'POST',
					headers: {'Content-Type': 'application/json'},
					body: JSON.stringify(data)
				})
				.then(r => r.json())
				.then(result => {
					document.getElementById('content').innerText = result.content;
					document.getElementById('output').style.display = 'block';
				});
			}
		</script>
	</body>
	</html>
	''')
	
@app.route('/api/contacts')
def api_contacts():
	"""Get contacts list"""
	conn = sqlite3.connect(os.path.expanduser("~/projects/apex/apex.db"))
	conn.row_factory = sqlite3.Row
	cursor = conn.cursor()
	
	cursor.execute("""
		SELECT id, name, company, title 
		FROM contacts 
		WHERE enrichment_status = 'complete'
		ORDER BY name
	""")
	
	contacts = [dict(row) for row in cursor.fetchall()]
	conn.close()
	
	return jsonify(contacts)

@app.route('/api/generate', methods=['POST'])
def api_generate():
	"""Generate content endpoint"""
	data = request.json
	
	pm = ProfileManager()
	gen = ContentGenerator(pm)
	
	# Update relationship if provided
	if data.get('relationship'):
		rel = RelationshipContext(
			relationship_level=data['relationship']['level'],
			years_known=int(data['relationship']['years_known']),
			last_interaction=data['relationship']['last_interaction'],
			professional_notes=data['relationship']['notes']
		)
		pm.save_relationship(data['contact_id'], rel)
		
	# Generate content
	content = gen.generate(data['contact_id'], data['channel'])
	
	return jsonify({
		'success': True,
		'content': content
	})
	
if __name__ == '__main__':
	# Initialize Chris's profile
	pm = ProfileManager()
	chris = UserProfile.load_chris()
	pm.save_user_profile(chris)
	
	print("✅ System initialized!")
	print("🌐 Starting web interface on http://localhost:5001")
	
	app.run(debug=True, port=5001)
	