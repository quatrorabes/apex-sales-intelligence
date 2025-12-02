#!/usr/bin/env python3

#!/usr/bin/env python3
"""
Authentic Relationship-Based Content Generator
Testing with real Chris-Andy dynamic
"""
import os
from openai import OpenAI
from dotenv import load_dotenv
import random

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# The REAL context
RELATIONSHIP_CONTEXT = """
Chris Rabenold (Harvest Small Business Finance) reaching out to Andy Bratt (Gantry).

RELATIONSHIP:
- Known each other 10 years through CRE industry
- See each other at NAIOP/ULI events, always say hi
- Good conversations but don't talk regularly
- Border between acquaintances and friends
- Mutual professional respect

BUSINESS DYNAMIC:
- Andy: Does $1M-$200M conventional CRE loans at Gantry (huge deals)
- Chris: Does SBA 504/7a loans for small businesses (owner-occupied CRE)
- Natural referral partners - not competitors
- Andy's too-small deals could go to Chris
- Chris's too-big deals could go to Andy

COMMUNICATION STYLE:
- Professional but casual
- No need for introductions
- Can reference shared experiences/events
- Industry shorthand is fine (LTV, DCR, basis points, etc.)
"""

# Different angles to test
ANGLES = [
	"Referral opportunity - has a deal that might fit Andy's shop",
	"Market observation - noticed something Andy might find interesting",
	"Event follow-up - planning to see him at upcoming NAIOP event",
	"Deal congrats - saw one of his recent wins, natural reconnect",
	"Market shift - rates/regulations changing, worth comparing notes"
]

def generate_authentic_outreach(channel="email", angle=None):
	"""Generate real-sounding outreach"""
	
	if not angle:
		angle = random.choice(ANGLES)
		
	prompt = f"""
{RELATIONSHIP_CONTEXT}

Write a {channel} from Chris to Andy with this angle: {angle}

CRITICAL RULES:
- Write like Chris is typing quickly between meetings
- No corporate phrases ("I hope this finds you well", "reaching out", etc.)
- No fake enthusiasm or overselling
- Natural reason to connect, not forced
- Could be sent at 7pm on a Monday after a long day
- Should feel like continuing an ongoing professional relationship

Length: {"Under 50 words" if channel == "text" else "Under 75 words"}

The message should feel authentic enough that Andy wouldn't think 
twice about it being generated.
"""

	response = client.chat.completions.create(
		model="gpt-4o",
		messages=[
			{"role": "system", "content": "You write authentic business communication between long-time industry contacts. No corporate speak."},
			{"role": "user", "content": prompt}
		],
		temperature=0.8  # Bit more variety
	)

	return response.choices[0].message.content
	
# Test multiple versions
print("="*60)
print("TESTING AUTHENTIC OUTREACH GENERATION")
print("="*60)

# Generate different versions
for i in range(3):
	print(f"\n📧 EMAIL VERSION {i+1}:")
	print("-" * 40)
	email = generate_authentic_outreach("email")
	print(email)
	
print("\n📱 TEXT VERSION:")
print("-" * 40)
text = generate_authentic_outreach("text", "Event follow-up - planning to see him at upcoming NAIOP event")
print(text)

print("\n💬 LINKEDIN VERSION:")
print("-" * 40)
linkedin = generate_authentic_outreach("linkedin message", "Deal congrats - saw one of his recent wins, natural reconnect")
print(linkedin)

print("\n📞 VOICEMAIL SCRIPT:")
print("-" * 40)
vm_prompt = f"""
{RELATIONSHIP_CONTEXT}

Write what Chris would actually say in a 15-second voicemail to Andy.
Not a script - what he'd actually say naturally.
Reason: Has a borrower who needs $15M construction loan (too big for Chris, perfect for Andy)
"""

vm_response = client.chat.completions.create(
	model="gpt-4o",
	messages=[
		{"role": "system", "content": "Write natural speech, not scripts"},
		{"role": "user", "content": vm_prompt}
	],
	temperature=0.8
)
print(vm_response.choices[0].message.content)

print("\n" + "="*60)
