#!/usr/bin/env python3

#!/usr/bin/env python3
"""
APEX Dashboard - Complete Integration
Enrichment + Scoring + Content Generation
"""
import os
import sqlite3
import json
import asyncio
from datetime import datetime
from flask import Flask, render_template, jsonify, request, send_file
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

# Database path
DB_PATH = os.path.expanduser("~/projects/apex/apex.db")

@app.route('/')
def dashboard():
	"""Main dashboard view"""
	return render_template('dashboard.html')

@app.route('/api/contacts')
def get_contacts():
	"""Get all contacts with enrichment status"""
	conn = sqlite3.connect(DB_PATH)
	conn.row_factory = sqlite3.Row
	cursor = conn.cursor()
	
	cursor.execute("""
		SELECT 
			id, name, email, company, title, phone,
			enrichment_status, priority_score, rss_score, mdcp_score,
			CASE 
				WHEN enrichment_data IS NOT NULL 
				THEN LENGTH(enrichment_data) 
				ELSE 0 
			END as data_size,
			CASE
				WHEN email_1_body IS NOT NULL THEN 'yes'
				ELSE 'no'
			END as has_content
		FROM contacts 
		ORDER BY priority_score DESC NULLS LAST
		LIMIT 100
	""")
	
	contacts = [dict(row) for row in cursor.fetchall()]
	conn.close()
	
	return jsonify(contacts)

@app.route('/api/contacts/<int:contact_id>')
def get_contact_detail(contact_id):
	"""Get single contact with full details"""
	conn = sqlite3.connect(DB_PATH)
	conn.row_factory = sqlite3.Row
	cursor = conn.cursor()
	
	cursor.execute("SELECT * FROM contacts WHERE id = ?", (contact_id,))
	contact = dict(cursor.fetchone())
	
	# Parse enrichment data if exists
	if contact['enrichment_data']:
		try:
			enrichment = json.loads(contact['enrichment_data'])
			contact['enrichment_preview'] = enrichment.get('perplexity_insights', '')[:500]
		except:
			contact['enrichment_preview'] = 'Error parsing enrichment'
			
	conn.close()
	return jsonify(contact)

@app.route('/api/contacts/<int:contact_id>/enrich', methods=['POST'])
def enrich_contact(contact_id):
	"""Run enhanced enrichment"""
	from enhanced_enrichment import EnhancedEnrichment
	
	conn = sqlite3.connect(DB_PATH)
	conn.row_factory = sqlite3.Row
	cursor = conn.cursor()
	
	cursor.execute("SELECT * FROM contacts WHERE id = ?", (contact_id,))
	row = cursor.fetchone()
	
	if not row:
		return jsonify({'error': 'Contact not found'}), 404
	
	contact = dict(row)
	
	# Run enhanced enrichment
	enricher = EnhancedEnrichment()
	result = enricher.enrich_contact(contact)
	
	if result and result['success']:
		# Save to database
		enrichment_data = {
			'full_profile_text': result['profile_text'],
			'perplexity_insights': result['profile_text'],
			'enriched_at': datetime.now().isoformat(),
			'profile_length': result['character_count']
		}
		
		cursor.execute("""
			UPDATE contacts 
			SET enrichment_data = ?,
				enrichment_status = 'complete',
				enriched_at = CURRENT_TIMESTAMP
			WHERE id = ?
		""", (json.dumps(enrichment_data), contact_id))
		
		conn.commit()
		
		# Auto-score
		from apps.backend.intelligence.engines.scoring.unified_scoring_engine import UnifiedScoringEngine
		scorer = UnifiedScoringEngine()
		scores = scorer.calculate_scores(contact_id)
		
		conn.close()
		
		return jsonify({
			'success': True,
			'contact_id': contact_id,
			'data_size': result['character_count'],
			'scores': scores,
			'filename': result['filename']
		})
	
	conn.close()
	return jsonify({'error': 'Enrichment failed'}), 500

@app.route('/api/contacts/<int:contact_id>/generate', methods=['POST'])
def generate_content(contact_id):
	"""Generate content with relationship awareness"""
	data = request.json or {}
	content_type = data.get('type', 'email')
	relationship_level = data.get('relationship', 'cold')
	
	conn = sqlite3.connect(DB_PATH)
	conn.row_factory = sqlite3.Row
	cursor = conn.cursor()
	
	cursor.execute("SELECT * FROM contacts WHERE id = ?", (contact_id,))
	contact = dict(cursor.fetchone())
	
	# Get enrichment
	profile = ""
	if contact['enrichment_data']:
		enrichment = json.loads(contact['enrichment_data'])
		profile = enrichment.get('perplexity_insights', '')[:2000]
		
	# Generate content based on relationship
	from openai import OpenAI
	client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
	
	# Check if peer/broker vs prospect
	is_peer = any(term in contact.get('title', '').lower() 
					for term in ['broker', 'principal', 'ccim', 'banker'])
	
	if is_peer:
		prompt = f"""
Write a {content_type} from Chris Rabenold (Harvest SBA lending) to {contact['name']}.
They are PEERS in CRE industry, not a prospect.
Relationship: {relationship_level}
Focus: Referral partnership potential
Tone: Professional but casual
Length: Under 75 words

Profile: {profile[:500]}
"""
	else:
		prompt = f"""
Write a {content_type} from Chris Rabenold (Harvest SBA lending) to {contact['name']}.
They are a potential CLIENT for SBA loans.
Relationship: {relationship_level}
Focus: Owner-occupied CRE benefits vs leasing
Tone: Professional, value-focused
Length: Under 100 words

Profile: {profile[:500]}
"""

	response = client.chat.completions.create(
		model="gpt-4o-mini",
		messages=[
			{"role": "system", "content": "Write authentic business communication."},
			{"role": "user", "content": prompt}
		],
		temperature=0.7
	)

	content = response.choices[0].message.content
	
	# Save to database
	cursor.execute(f"""
		UPDATE contacts 
		SET email_1_body = ?,
			content_generated_at = CURRENT_TIMESTAMP
		WHERE id = ?
	""", (content, contact_id))

	conn.commit()
	conn.close()
	
	return jsonify({
		'success': True,
		'content': content,
		'is_peer': is_peer
	})

@app.route('/api/dashboard/stats')
def dashboard_stats():
	"""Get dashboard statistics"""
	conn = sqlite3.connect(DB_PATH)
	cursor = conn.cursor()
	
	stats = {}
	
	# Total contacts
	cursor.execute("SELECT COUNT(*) FROM contacts")
	stats['total_contacts'] = cursor.fetchone()[0]
	
	# Enriched contacts
	cursor.execute("SELECT COUNT(*) FROM contacts WHERE enrichment_status = 'complete'")
	stats['enriched_contacts'] = cursor.fetchone()[0]
	
	# Scored contacts
	cursor.execute("SELECT COUNT(*) FROM contacts WHERE priority_score IS NOT NULL")
	stats['scored_contacts'] = cursor.fetchone()[0]
	
	# Content generated
	cursor.execute("SELECT COUNT(*) FROM contacts WHERE email_1_body IS NOT NULL")
	stats['content_generated'] = cursor.fetchone()[0]
	
	# Top prospects
	cursor.execute("""
		SELECT name, company, priority_score 
		FROM contacts 
		WHERE priority_score IS NOT NULL 
		ORDER BY priority_score DESC 
		LIMIT 5
	""")
	stats['top_prospects'] = [
		{'name': row[0], 'company': row[1], 'score': row[2]}
		for row in cursor.fetchall()
	]
	
	conn.close()
	return jsonify(stats)

# Create templates directory if it doesn't exist
os.makedirs('templates', exist_ok=True)

# Dashboard HTML template
dashboard_html = '''
<!DOCTYPE html>
<html>
<head>
	<title>APEX Dashboard</title>
	<style>
		* { margin: 0; padding: 0; box-sizing: border-box; }
		body { 
			font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
			background: #f5f7fa;
		}
		.header {
			background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
			color: white;
			padding: 20px;
			box-shadow: 0 2px 4px rgba(0,0,0,0.1);
		}
		.header h1 { font-size: 24px; }
		.stats-bar {
			display: flex;
			gap: 20px;
			padding: 20px;
			background: white;
			border-bottom: 1px solid #e1e8ed;
		}
		.stat-card {
			flex: 1;
			text-align: center;
		}
		.stat-number {
			font-size: 32px;
			font-weight: bold;
			color: #667eea;
		}
		.stat-label {
			color: #657786;
			font-size: 14px;
			margin-top: 5px;
		}
		.container {
			display: flex;
			height: calc(100vh - 140px);
		}
		.contacts-panel {
			width: 400px;
			background: white;
			border-right: 1px solid #e1e8ed;
			overflow-y: auto;
		}
		.contact-item {
			padding: 15px;
			border-bottom: 1px solid #f0f3f7;
			cursor: pointer;
			transition: background 0.2s;
		}
		.contact-item:hover { background: #f8f9fa; }
		.contact-item.selected { background: #f0f3ff; }
		.contact-name { 
			font-weight: 600; 
			color: #14171a;
			margin-bottom: 5px;
		}
		.contact-company { 
			color: #657786; 
			font-size: 14px;
		}
		.contact-badges {
			display: flex;
			gap: 8px;
			margin-top: 8px;
		}
		.badge {
			padding: 2px 8px;
			border-radius: 12px;
			font-size: 12px;
			font-weight: 500;
		}
		.badge.enriched { 
			background: #d4f4dd; 
			color: #1e7e34;
		}
		.badge.scored { 
			background: #fff3cd; 
			color: #856404;
		}
		.badge.content { 
			background: #cce5ff; 
			color: #004085;
		}
		.badge.peer { 
			background: #f8d7da; 
			color: #721c24;
		}
		.detail-panel {
			flex: 1;
			padding: 20px;
			overflow-y: auto;
		}
		.detail-card {
			background: white;
			border-radius: 8px;
			padding: 20px;
			margin-bottom: 20px;
			box-shadow: 0 1px 3px rgba(0,0,0,0.1);
		}
		.detail-card h3 {
			color: #14171a;
			margin-bottom: 15px;
			font-size: 18px;
		}
		.info-grid {
			display: grid;
			grid-template-columns: 1fr 1fr;
			gap: 15px;
		}
		.info-item label {
			color: #657786;
			font-size: 12px;
			text-transform: uppercase;
			display: block;
			margin-bottom: 5px;
		}
		.info-item value {
			color: #14171a;
			font-size: 14px;
		}
		.action-buttons {
			display: flex;
			gap: 10px;
			margin-top: 20px;
		}
		.btn {
			padding: 10px 20px;
			border: none;
			border-radius: 6px;
			font-size: 14px;
			font-weight: 600;
			cursor: pointer;
			transition: all 0.2s;
		}
		.btn-primary {
			background: #667eea;
			color: white;
		}
		.btn-primary:hover {
			background: #5a67d8;
		}
		.btn-secondary {
			background: white;
			color: #667eea;
			border: 2px solid #667eea;
		}
		.score-display {
			display: flex;
			gap: 20px;
			margin-top: 15px;
		}
		.score-item {
			text-align: center;
		}
		.score-value {
			font-size: 24px;
			font-weight: bold;
			color: #667eea;
		}
		.score-label {
			font-size: 12px;
			color: #657786;
			margin-top: 5px;
		}
		.content-preview {
			background: #f8f9fa;
			padding: 15px;
			border-radius: 6px;
			font-family: monospace;
			font-size: 13px;
			line-height: 1.6;
			max-height: 300px;
			overflow-y: auto;
			white-space: pre-wrap;
		}
		.loading {
			display: inline-block;
			width: 20px;
			height: 20px;
			border: 3px solid #f3f3f3;
			border-top: 3px solid #667eea;
			border-radius: 50%;
			animation: spin 1s linear infinite;
			margin-left: 10px;
		}
		@keyframes spin {
			0% { transform: rotate(0deg); }
			100% { transform: rotate(360deg); }
		}
		.empty-state {
			text-align: center;
			padding: 40px;
			color: #657786;
		}
	</style>
</head>
<body>
	<div class="header">
		<h1>🎯 APEX Sales Intelligence Dashboard</h1>
	</div>
	
	<div class="stats-bar">
		<div class="stat-card">
			<div class="stat-number" id="stat-total">0</div>
			<div class="stat-label">Total Contacts</div>
		</div>
		<div class="stat-card">
			<div class="stat-number" id="stat-enriched">0</div>
			<div class="stat-label">Enriched</div>
		</div>
		<div class="stat-card">
			<div class="stat-number" id="stat-scored">0</div>
			<div class="stat-label">Scored</div>
		</div>
		<div class="stat-card">
			<div class="stat-number" id="stat-content">0</div>
			<div class="stat-label">Content Generated</div>
		</div>
	</div>
	
	<div class="container">
		<div class="contacts-panel" id="contacts-panel">
			<div class="empty-state">Loading contacts...</div>
		</div>
		
		<div class="detail-panel" id="detail-panel">
			<div class="empty-state">
				<h3>Select a contact to view details</h3>
				<p>Choose from the list on the left to see enrichment, scoring, and content generation options.</p>
			</div>
		</div>
	</div>
	
	<script>
		let currentContact = null;
		let contacts = [];
		
		// Load dashboard stats
		async function loadStats() {
			const response = await fetch('/api/dashboard/stats');
			const stats = await response.json();
			
			document.getElementById('stat-total').textContent = stats.total_contacts;
			document.getElementById('stat-enriched').textContent = stats.enriched_contacts;
			document.getElementById('stat-scored').textContent = stats.scored_contacts;
			document.getElementById('stat-content').textContent = stats.content_generated;
		}
		
		// Load contacts list
		async function loadContacts() {
			const response = await fetch('/api/contacts');
			contacts = await response.json();
			
			const panel = document.getElementById('contacts-panel');
			
			if (contacts.length === 0) {
				panel.innerHTML = '<div class="empty-state">No contacts found</div>';
				return;
			}
			
			panel.innerHTML = contacts.map(contact => {
				const isPeer = ['broker', 'principal', 'ccim', 'banker'].some(
					term => (contact.title || '').toLowerCase().includes(term)
				);
				
				return `
					<div class="contact-item" onclick="selectContact(${contact.id})">
						<div class="contact-name">${contact.name}</div>
						<div class="contact-company">${contact.title || 'No title'} at ${contact.company || 'No company'}</div>
						<div class="contact-badges">
							${contact.enrichment_status === 'complete' ? '<span class="badge enriched">Enriched</span>' : ''}
							${contact.priority_score ? '<span class="badge scored">Score: ' + Math.round(contact.priority_score) + '</span>' : ''}
							${contact.has_content === 'yes' ? '<span class="badge content">Content</span>' : ''}
							${isPeer ? '<span class="badge peer">Peer</span>' : ''}
						</div>
					</div>
				`;
			}).join('');
		}
		
		// Select and show contact details
		async function selectContact(contactId) {
			// Update selection UI
			document.querySelectorAll('.contact-item').forEach(item => {
				item.classList.remove('selected');
			});
			event.currentTarget.classList.add('selected');
			
			// Load contact details
			const response = await fetch(`/api/contacts/${contactId}`);
			currentContact = await response.json();
			
			const isPeer = ['broker', 'principal', 'ccim', 'banker'].some(
				term => (currentContact.title || '').toLowerCase().includes(term)
			);
			
			const detailPanel = document.getElementById('detail-panel');
			detailPanel.innerHTML = `
				<div class="detail-card">
					<h3>${currentContact.name}</h3>
					<div class="info-grid">
						<div class="info-item">
							<label>Title</label>
							<value>${currentContact.title || 'Not specified'}</value>
						</div>
						<div class="info-item">
							<label>Company</label>
							<value>${currentContact.company || 'Not specified'}</value>
						</div>
						<div class="info-item">
							<label>Email</label>
							<value>${currentContact.email || 'Not specified'}</value>
						</div>
						<div class="info-item">
							<label>Phone</label>
							<value>${currentContact.phone || 'Not specified'}</value>
						</div>
						<div class="info-item">
							<label>Type</label>
							<value>${isPeer ? '🤝 Industry Peer (Referral Partner)' : '🎯 Prospect (Potential Client)'}</value>
						</div>
						<div class="info-item">
							<label>Enrichment Status</label>
							<value>${currentContact.enrichment_status || 'Not enriched'}</value>
						</div>
					</div>
					
					${currentContact.priority_score ? `
						<div class="score-display">
							<div class="score-item">
								<div class="score-value">${Math.round(currentContact.priority_score)}</div>
								<div class="score-label">Priority Score</div>
							</div>
							<div class="score-item">
								<div class="score-value">${Math.round(currentContact.rss_score || 0)}</div>
								<div class="score-label">Role Score</div>
							</div>
							<div class="score-item">
								<div class="score-value">${Math.round(currentContact.mdcp_score || 0)}</div>
								<div class="score-label">Data Score</div>
							</div>
						</div>
					` : ''}
					
					<div class="action-buttons">
						<button class="btn btn-primary" onclick="enrichContact(${contactId})" 
							${currentContact.enrichment_status === 'complete' ? 'disabled' : ''}>
							${currentContact.enrichment_status === 'complete' ? '✓ Enriched' : '🔍 Enrich Contact'}
						</button>
						<button class="btn btn-secondary" onclick="generateContent(${contactId})">
							✉️ Generate Content
						</button>
					</div>
				</div>
				
				${currentContact.enrichment_preview ? `
					<div class="detail-card">
						<h3>Enrichment Preview</h3>
						<div class="content-preview">${currentContact.enrichment_preview}</div>
					</div>
				` : ''}
				
				${currentContact.email_1_body ? `
					<div class="detail-card">
						<h3>Generated Email</h3>
						<div class="content-preview">${currentContact.email_1_body}</div>
					</div>
				` : ''}
			`;
		}
		
		// Enrich contact
		async function enrichContact(contactId) {
			const btn = event.target;
			btn.innerHTML = 'Enriching... <span class="loading"></span>';
			btn.disabled = true;
			
			try {
				const response = await fetch(`/api/contacts/${contactId}/enrich`, {
					method: 'POST'
				});
				const result = await response.json();
				
				if (result.success) {
					alert(`✅ Enrichment complete! Profile size: ${result.data_size} characters\\nScores: Priority=${Math.round(result.scores.priority_score)}`);
					loadContacts();
					loadStats();
					selectContact(contactId);
				} else {
					alert('❌ Enrichment failed: ' + result.error);
				}
			} catch (error) {
				alert('Error: ' + error.message);
			}
		}
		
		// Generate content
		async function generateContent(contactId) {
			const btn = event.target;
			btn.innerHTML = 'Generating... <span class="loading"></span>';
			btn.disabled = true;
			
			try {
				const response = await fetch(`/api/contacts/${contactId}/generate`, {
					method: 'POST',
					headers: {'Content-Type': 'application/json'},
					body: JSON.stringify({
						type: 'email',
						relationship: 'cold'
					})
				});
				const result = await response.json();
				
				if (result.success) {
					alert(`✅ Content generated!\\nType: ${result.is_peer ? 'Peer/Referral' : 'Prospect/Client'}`);
					selectContact(contactId);
				} else {
					alert('❌ Generation failed');
				}
			} catch (error) {
				alert('Error: ' + error.message);
			} finally {
				btn.innerHTML = '✉️ Generate Content';
				btn.disabled = false;
			}
		}
		
		// Initialize dashboard
		loadStats();
		loadContacts();
	</script>
</body>
</html>
'''

# Save the template
with open('templates/dashboard.html', 'w') as f:
	f.write(dashboard_html)
	
if __name__ == '__main__':
	print("\n" + "="*60)
	print("🚀 APEX DASHBOARD STARTING")
	print("="*60)
	print("\n✅ Features:")
	print("   • View all contacts with enrichment status")
	print("   • Run enhanced enrichment with strategic intel")
	print("   • Auto-scoring after enrichment")
	print("   • Generate relationship-aware content")
	print("   • Identify peers vs prospects automatically")
	print("\n🌐 Open http://localhost:5000 in your browser")
	print("="*60 + "\n")
	
	app.run(debug=True, port=5000)
	