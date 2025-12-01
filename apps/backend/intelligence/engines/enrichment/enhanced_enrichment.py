#!/usr/bin/env python3

#!/usr/bin/env python3
"""
PROFILE BUILDER - Enhanced Enrichment Engine
3-Stage Process:
1. Perplexity sonar-pro: Comprehensive open-ended research
2. GPT-4: Intelligence interpolation + structured formatting
3. Database persistence + dashboard population

Format matches: Clint Stefan profile from Perplexity Space "Profile Builder"
"""
import os
import requests
import json
from datetime import datetime
from dotenv import load_dotenv
import openai

load_dotenv()

class EnhancedEnrichment:
		"""Three-stage enrichment: Research → Intelligence → Structure"""
	
		def __init__(self):
			"""Initialize enrichment engine with API keys"""
			self.perplexity_key = os.getenv('PERPLEXITY_API_KEY')
			self.openai_key = os.getenv('OPENAI_API_KEY')
			
			if not self.perplexity_key:
				logger.warning("⚠️  PERPLEXITY_API_KEY not set")
			if not self.openai_key:
				logger.warning("⚠️  OPENAI_API_KEY not set")
				
			# NO LONGER SET GLOBAL API KEY - use client instance instead
				
		def enrich_contact(self, contact):
				"""
				Main enrichment flow:
				Stage 1: Perplexity research (open-ended)
				Stage 2: GPT-4 intelligence interpolation
				Stage 3: Return structured profile for database
				"""
				name = contact.get('name', '')
				company = contact.get('company', '')
				contact_id = contact.get('id', 'unknown')
			
				print('=' * 80)
				print(f"PROFILE BUILDER ENRICHMENT: {name} at {company}")
				print('=' * 80)
			
				# STAGE 1: Perplexity Research
				query = self.build_profile_builder_query(contact)
				print("\n🔍 STAGE 1: PERPLEXITY RESEARCH (sonar-pro)")
				print('-' * 40)
				print(query[:500] + "...(truncated for display)")
				print('-' * 40)
			
				raw_profile = self.call_perplexity(query)
				if not raw_profile:
						print("❌ No result from Perplexity")
						return {'status': 'error', 'error': 'Perplexity research failed'}
			
				print(f"✅ STAGE 1 COMPLETE: {len(raw_profile):,} characters")
			
				# STAGE 2: GPT-4 Intelligence Layer
				print("\n✨ STAGE 2: GPT-4 INTELLIGENCE INTERPOLATION...")
				print('-' * 40)
			
				polished_profile = self.add_intelligence_layer(raw_profile, contact)
				if not polished_profile:
						print("⚠️  Stage 2 failed, using raw profile")
						polished_profile = raw_profile
				else:
						print(f"✅ STAGE 2 COMPLETE: {len(polished_profile):,} characters")
					
				# Save files for audit trail
				timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
				base_filename = f"{self.output_dir}/profile_{contact_id}_{name.replace(' ', '_')}_{timestamp}"
			
				# Save raw version
				raw_filename = f"{base_filename}_raw.txt"
				self.save_profile(raw_filename, contact, raw_profile, "sonar-pro (raw)")
			
				# Save polished version
				polished_filename = f"{base_filename}_polished.txt"
				self.save_profile(polished_filename, contact, polished_profile, "sonar-pro + gpt-4 (polished)")
			
				# Save JSON metadata
				json_filename = f"{base_filename}.json"
				with open(json_filename, 'w', encoding='utf-8') as f:
						json.dump({
								'contact': contact,
								'raw_profile': raw_profile,
								'polished_profile': polished_profile,
								'generated_at': datetime.now().isoformat(),
								'raw_length': len(raw_profile),
								'polished_length': len(polished_profile),
								'filenames': {
										'raw': raw_filename,
										'polished': polished_filename
								}
						}, f, indent=2)
					
				print('=' * 80)
				print("🎉 THREE-STAGE ENRICHMENT COMPLETE!")
				print('=' * 80)
				print(f"📄 Raw profile: {raw_filename}")
				print(f"📄 Polished profile: {polished_filename}")
				print(f"📄 JSON data: {json_filename}")
				print(f"📊 Raw size: {len(raw_profile):,} characters")
				print(f"📊 Polished size: {len(polished_profile):,} characters")
			
				# Return for API/database
				return {
						'status': 'success',
						'enrichment_data': polished_profile,
						'overview': polished_profile[:500],
						'character_count': len(polished_profile)
				}
	
		def build_profile_builder_query(self, contact):
				"""
				Build the EXACT query format from Profile Builder Space.
				Open-ended to let Perplexity explore comprehensively.
				"""
				name = contact.get('name', '')
				title = contact.get('title', '')
				company = contact.get('company', '')
				email = contact.get('email', '')
				phone = contact.get('phone', '')
				linkedin_url = contact.get('linkedin_url', '')
			
				context = f"{name}, {title} at {company}"
				if email:
						context += f"\nEmail: {email}"
				if phone:
						context += f"\nPhone: {phone}"
				if linkedin_url:
						context += f"\nLinkedIn: {linkedin_url}"
						context += f"\n\nUse this LinkedIn profile ({linkedin_url}) as PRIMARY source for work history and education."
					
				query = f"""{context}

You are a professional profile-building assistant. Generate a comprehensive, up-to-date profile using sources such as LinkedIn and the Internet.

For the PERSON ({name}), structure the profile as:

1. Overview – Current title and organization
2. Background – Work history, notable achievements
3. Education – Degrees and institutions
4. Recent Mentions – Any news, public appearances, LinkedIn posts, or online presence
5. Social Profiles – Find Instagram, Facebook, and Twitter user profiles
6. Personality Detail – Perform a Myers-Briggs personality assessment based on professional behavior
7. Myers-Briggs Personality Assessment Summary – Compose and interpret the assessment
8. Sales Opportunities – Evaluate potential talking points regarding sales opportunities

For the COMPANY ({company}), structure the profile as:

1. Overview – Description, mission, founding details, and HQ
2. Products & Services – Key offerings and markets served
3. Leadership – Key executives and founders
4. Market & Competitors – Industry, position, key competitors
5. Recent News – Major announcements, deals, or product launches
6. Fun Facts – Find any relevant company news or fun facts

IMPORTANT:
- Be thorough and cite sources where possible
- Find the correct company where {name} works as {title}
- If the company is in commercial real estate or mortgage banking, emphasize their deal flow and client types
- Include specific years, dates, and quantifiable details wherever available
- Search for social media profiles on all major platforms
"""

				return query.strip()
				
		def add_intelligence_layer(self, raw_profile, contact):
				"""
				Stage 2: GPT-4 adds intelligence, interpolation, and structure.
				Matches the EXACT format from Clint Stefan profile output.
				"""
				name = contact.get('name', '')
				title = contact.get('title', '')
				company = contact.get('company', '')
			
				polish_prompt = f"""
You are an expert sales intelligence analyst. Transform the following research into a structured, actionable professional profile.

CONTACT: {name}
TITLE: {title}
COMPANY: {company}

RAW RESEARCH:
{raw_profile}

FORMAT YOUR OUTPUT EXACTLY LIKE THIS:

# {name.upper()} - PROFESSIONAL PROFILE

## 1. Overview
[2-3 sentence executive summary with current title and organization]

## 2. Professional Background
[Career trajectory, work history, notable achievements with specific years and companies]

## 3. Education
[Degrees, institutions, years attended, honors/distinctions. Format as bullet points with years.]

## 4. Recent Mentions
python
#!/usr/bin/env python3
"""
PROFILE BUILDER - Enhanced Enrichment Engine
3-Stage Intelligence Pipeline:
	Stage 1: Perplexity sonar-pro comprehensive research
	Stage 2: GPT-4 intelligence interpolation & structuring
	Stage 3: Database persistence
	
Output Format: Based on "Profile Builder" Perplexity Space instructions
- Overview, Background, Education, Social Profiles
- Myers-Briggs Personality Assessment
- Pain Points, Sales Opportunities, Talking Points
- Fun Facts, Company News, Deal History
"""
import os
import requests
import json
from datetime import datetime
from dotenv import load_dotenv
import openai

load_dotenv()


class EnhancedEnrichment:
		"""Three-stage enrichment: Research → Intelligence → Structure"""
		
		def __init__(self, api_key=None, openai_key=None):
				self.perplexity_key = api_key or os.getenv('PERPLEXITY_API_KEY')
				self.openai_key = openai_key or os.getenv('OPENAI_API_KEY')
				
				if not self.perplexity_key:
						raise ValueError("PERPLEXITY_API_KEY required")
				if not self.openai_key:
						raise ValueError("OPENAI_API_KEY required for intelligence layer")
				
				openai.api_key = self.openai_key
				self.output_dir = 'enrichment_profiles'
				os.makedirs(self.output_dir, exist_ok=True)
				
				print("✅ EnhancedEnrichment initialized (Profile Builder 3-stage)")
		
		def enrich_contact(self, contact):
				"""Main enrichment pipeline"""
				name = contact.get('name', '')
				company = contact.get('company', '')
				contact_id = contact.get('id', 'unknown')
				
				print("=" * 80)
				print(f"PROFILE BUILDER ENRICHMENT: {name} at {company}")
				print("=" * 80)
				
				# STAGE 1: Perplexity Research (Open-ended, comprehensive)
				query = self._build_profile_builder_query(contact)
				print("\n🔍 STAGE 1: PERPLEXITY RESEARCH (sonar-pro)")
				print("-" * 40)
				print(query[:500] + "...(truncated for display)")
				print("-" * 40)
				
				raw_profile = self._call_perplexity(query)
				if not raw_profile:
						print("❌ No result from Perplexity")
						return {'status': 'error', 'error': 'Perplexity returned no data'}
				
				print(f"✅ STAGE 1 COMPLETE: {len(raw_profile)} characters")
				
				# STAGE 2: GPT-4 Intelligence Layer (Interpolation + Structure)
				print("\n✨ STAGE 2: GPT-4 INTELLIGENCE INTERPOLATION...")
				print("-" * 40)
				
				polished_profile = self._gpt4_intelligence_layer(raw_profile, contact)
				if not polished_profile:
						print("⚠️  Stage 2 failed, using raw profile")
						polished_profile = raw_profile
				else:
						print(f"✅ STAGE 2 COMPLETE: {len(polished_profile)} characters")
				
				# Save outputs
				timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
				base_filename = f"{self.output_dir}/profile_{contact_id}_{name.replace(' ', '_')}_{timestamp}"
				
				raw_filename = f"{base_filename}_raw.txt"
				self._save_profile(raw_filename, contact, raw_profile, "sonar-pro (raw)")
				
				polished_filename = f"{base_filename}_polished.txt"
				self._save_profile(polished_filename, contact, polished_profile, "sonar-pro + gpt-4 (polished)")
				
				print("=" * 80)
				print("THREE-STAGE ENRICHMENT COMPLETE!")
				print("=" * 80)
				print(f"📄 Raw profile: {raw_filename}")
				print(f"📄 Polished profile: {polished_filename}")
				print(f"📊 Raw size: {len(raw_profile)} characters")
				print(f"📊 Polished size: {len(polished_profile)} characters")
				
				return {
						'status': 'success',
						'enrichment_data': polished_profile,
						'overview': polished_profile[:500],
						'character_count': len(polished_profile)
				}
		
		def _build_profile_builder_query(self, contact):
				"""Build comprehensive query based on Profile Builder instructions"""
				name = contact.get('name', '')
				title = contact.get('title', '')
				company = contact.get('company', '')
				email = contact.get('email', '')
				phone = contact.get('phone', '')
				linkedin_url = contact.get('linkedin_url', '')
				
				context = f"{name}, {title} at {company}"
				if email:
						context += f"\nEmail: {email}"
				if phone:
						context += f"\nPhone: {phone}"
				if linkedin_url:
						context += f"\nLinkedIn Profile: {linkedin_url}"
						context += f"\n\n🔍 Use this LinkedIn profile ({linkedin_url}) as PRIMARY source for work history and education."
				
				query = f"""{context}
				
You are a professional profile-building assistant. Generate a comprehensive, up-to-date profile using public web sources, LinkedIn, and any available data.

Build a professional profile for {name} structured with these sections:
	
**FOR THE PERSON ({name}):**

1. Overview – Current title, organization, and 2-3 sentence role summary
2. Background – Career trajectory, work history, notable achievements (include specific years and companies)
3. Education – Degrees, institutions, years attended, honors/distinctions (e.g., Dean's List, scholarships)
4. Recent Mentions – News articles, public appearances, LinkedIn posts, online presence (with dates)
5. Social Media Profiles – Find Instagram, Facebook, Twitter/X profiles (provide handles or "Not publicly available")
6. Personality Detail – Perform a Myers-Briggs personality assessment based on professional behavior, leadership style, communication patterns
7. Myers-Briggs Summary – Interpret the personality type and how it relates to their work style and strengths
	
**FOR THE COMPANY ({company}):**
	
8. Company Overview – Description, mission, founding details, HQ location
8.1. Products & Services – Key offerings and markets served
8.2. Leadership – Key executives and founders
8.3. Market & Competitors – Industry position, key competitors
8.4. Recent News – Major announcements, deals, product launches
8.5. Company Fun Facts – Unique background, volunteer work, culture notes
	
**STRATEGIC INTELLIGENCE SECTION:**
	
9. Pain Points – Identify 5 specific pain points that someone in {name}'s role ({title}) would face in their day-to-day work. Consider industry challenges, role-specific frustrations, and market conditions.
	
10. Business Needs & Opportunities – Identify 5 specific ways this person or their business could benefit from sales intelligence, CRM tools, or financing solutions (if applicable to their industry).
	
11. Key Insights – Provide 3 critical, non-obvious insights about {name}, their profession, or {company} that would be valuable in a business conversation or sales pitch.
	
12. Final Note – One-paragraph strategic summary synthesizing {name}'s position, needs, and best engagement approach for outreach.
	
**IMPORTANT:**
- Be thorough and cite sources where possible
- Include specific dates, years, and context
- Find the correct company where {name} works as {title}
- If {company} is in commercial real estate, mortgage banking, or finance, emphasize their deal flow and client types
"""
				return query.strip()
		
		def _gpt4_intelligence_layer(self, raw_profile, contact):
				"""
				Stage 2: GPT-4 adds intelligence, interpolates data, structures output
				Output format matches Clint Stefan example from Profile Builder Space
				"""
				name = contact.get('name', '')
				title = contact.get('title', '')
				company = contact.get('company', '')
				
				prompt = f"""
You are an expert sales intelligence analyst with deep expertise in professional profiling and business psychology.
	
Your task: Transform the following research into a structured, actionable professional profile with added intelligence and insights.
	
**CONTACT:** {name}, {title} at {company}
	
**RAW RESEARCH DATA:**
{raw_profile}
	
**OUTPUT FORMAT (USE EXACTLY THIS STRUCTURE):**
	
## 1. Overview
[2-3 sentence executive summary of current role, organization, and key background]
	
## 2. Professional Background
[Detailed career trajectory with specific companies, roles, years, and notable achievements. Include progression and key transitions.]
	
## 3. Education & Credentials
[All degrees, institutions, years attended, honors/distinctions (e.g., UC Berkeley BA Economics 1976-1980, Dean's List)]
	
## 4. Recent Mentions
[News articles, public appearances, LinkedIn activity, speaking engagements - include dates and context]
	
## 5. Social Media Profiles
- **LinkedIn:** [URL or "Not found"]
- **Twitter/X:** [Handle or "Not publicly available"]
- **Facebook:** [Profile or "Not publicly available"]
- **Instagram:** [Handle or "Not publicly available"]
	
## 6. Personality Detail
[Based on the research, perform a Myers-Briggs personality assessment. Infer type from:
- Leadership style (strategic vs tactical, collaborative vs directive)
- Communication patterns (formal vs informal, data-driven vs relationship-driven)
- Career choices (entrepreneurial vs corporate, specialist vs generalist)
- Public presence (visible thought leader vs behind-the-scenes operator)]
	
Example: "Based on {name}'s professional trajectory and leadership style, they exhibit traits commonly associated with an **ENTJ** (Extraverted, Intuitive, Thinking, Judging) personality type."
	
## 7. Myers-Briggs Personality Assessment Summary
[Interpret how this personality type manifests in their work:
- Strategic thinking and decision-making style
- Leadership and team dynamics
- Communication preferences
- How they approach problems and opportunities
- Best ways to engage with them]
	
## 8. Company Overview – {company}
[Mission, founding details, HQ, size, stage (startup/growth/established)]
	
### 8.1. Products & Services
[Key offerings, markets served, unique value proposition]
	
### 8.2. Leadership
[Key executives, founders, notable team members]
	
### 8.3. Market & Competitors
[Industry position, key competitors, differentiation]
	
### 8.4. Recent News
[Major announcements, deals, funding, product launches - with dates]
	
### 8.5. Company Fun Facts
[Unique culture, volunteer work, awards, quirky details that humanize the company]
	
## 9. Pain Points & Challenges
[Identify 5 specific pain points for someone in {name}'s role as {title}:]
- [Pain point 1 with context]
- [Pain point 2 with context]
- [Pain point 3 with context]
- [Pain point 4 with context]
- [Pain point 5 with context]
	
## 10. Sales Opportunities & Talking Points
[5 actionable talking points for sales conversations based on their background, pain points, and industry:]
- [Talking point 1]
- [Talking point 2]
- [Talking point 3]
- [Talking point 4]
- [Talking point 5]
	
## 11. Key Insights (Deep Intelligence)
[3 critical, non-obvious insights valuable for business conversations:]
- [Insight 1: Something about their career path, expertise, or company that reveals opportunity]
- [Insight 2: A strategic angle based on industry trends or their role]
- [Insight 3: Personal or professional motivator that drives decision-making]
	
## 12. Final Note – Strategic Summary
[One compelling paragraph that synthesizes:
- Who they are (role, background, expertise)
- What they care about (motivations, goals)
- How to engage them (best channels, messaging angles, timing)
- Why now (urgency, opportunity, market conditions)]
	
**INSTRUCTIONS:**
- Use the EXACT section structure above
- Add your own intelligence and interpolation beyond the raw data
- Cite specific evidence from the research
- Make it actionable for sales teams
- Include dates, numbers, and specific details wherever possible
- If data is missing (e.g., social profiles), say "Not publicly available" rather than omitting
- Be professional but direct - this is for business use
"""
				
				try:
						response = openai.ChatCompletion.create(
								model='gpt-4',
								messages=[
										{
												'role': 'system',
												'content': 'You are a professional business intelligence analyst specializing in sales enablement. You excel at transforming raw research into actionable, structured profiles with deep insights.'
										},
										{
												'role': 'user',
												'content': prompt
										}
								],
								temperature=0.4,  # Balanced creativity and consistency
								max_tokens=4000
						)
						return response.choices.message.content
				
				except Exception as e:
						print(f"❌ GPT-4 intelligence layer error: {e}")
						return None
		
		def _call_perplexity(self, query):
			"""Call Perplexity API with sonar-pro model"""
			url = 'https://api.perplexity.ai/chat/completions'
			headers = {
				'Authorization': f'Bearer {self.perplexity_key}',
				'Content-Type': 'application/json'
			}
			payload = {
				'model': 'sonar-pro',
				'messages': [{'role': 'user', 'content': query}],
				'temperature': 0.2,
				'max_tokens': 4000
			}
			
			try:
				print("🌐 Calling Perplexity API (sonar-pro model)...")
				response = requests.post(url, json=payload, headers=headers, timeout=60)
				
				if response.status_code == 200:
					data = response.json()
					print("✅ API call successful!")
					return data['choices'][0]['message']['content']  # FIXED: Added [0]
				else:
					print(f"❌ API Error: {response.status_code}")
					print(f"Response: {response.text}")
					return None
			
			except Exception as e:
				print(f"❌ Request error: {e}")
				return None
		
		def _save_profile(self, filename, contact, profile_text, model_info):
			"""Save profile to file with metadata header"""
			with open(filename, 'w', encoding='utf-8') as f:
				f.write("=" * 80 + "\n")
				f.write("PROFILE BUILDER - APEX SALES INTELLIGENCE\n")
				f.write(f"Generated: {datetime.now().isoformat()}\n")
				f.write(f"Model: {model_info}\n")
				f.write("=" * 80 + "\n")
				f.write("CONTACT DETAILS\n")
				f.write(f"Name: {contact.get('name')}\n")
				f.write(f"Title: {contact.get('title')}\n")
				f.write(f"Company: {contact.get('company')}\n")
				f.write(f"Email: {contact.get('email')}\n")
				f.write(f"Phone: {contact.get('phone')}\n")
				f.write("=" * 80 + "\n")
				f.write("PROFILE\n")
				f.write("-" * 80 + "\n")
				f.write(profile_text)
				f.write("\n" + "=" * 80 + "\n")
	
	
	# Test stub
	if __name__ == '__main__':
		test_contact = {
			'id': 1,
			'name': 'John Doe',
			'title': 'Vice President',
			'company': 'Sample Company',
			'email': 'john@example.com',
			'phone': '555-1234',
			'linkedin_url': 'https://linkedin.com/in/johndoe'
		}
		
		enricher = EnhancedEnrichment()
		result = enricher.enrich_contact(test_contact)
		
		if result.get('status') == 'success':
			print("✅ Test completed successfully!")
