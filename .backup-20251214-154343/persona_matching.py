#!/usr/bin/env python3

import pandas as pd
import json

# Define the 8 personas
personas = [
	'loan_broker',
	'sales_broker',
	'banker',
	'sba_banker',
	'referral_network_other',
	'internal',
	'borrower',
	'past_borrower'
]

# Create comprehensive job title mappings for each persona
# Based on the keyword examples provided and industry standards

persona_mappings = {
	'banker': {
		'description': 'Traditional banking professionals in commercial lending roles',
		'job_titles': [
			'commercial lender',
			'cre lender',
			'business development officer',
			'bdo',
			'loan officer',
			'vp commercial',
			'svp commercial',
			'vp lending',
			'svp lending',
			'regional manager',
			'market president',
			'relationship manager',
			'commercial finance',
			'commercial loan',
			'lending specialist',
			'credit officer',
			'underwriter',
			'senior credit officer',
			'commercial credit analyst',
			'chief lending officer',
			'clo',
			'loan portfolio manager',
			'risk manager'
		],
		'company_keywords': [
			'bank',
			'banking',
			'credit union',
			'community bank',
			'financial services',
			'trust company'
		],
		'matching_keywords': [
			'commercial lending',
			'loans',
			'commercial mortgages',
			'finance',
			'financial services'
		]
	},
	
	'sba_banker': {
		'description': 'Banking professionals specializing in SBA lending programs',
		'job_titles': [
			'sba specialist',
			'sba 504',
			'sba 7a',
			'sba program manager',
			'sba lender',
			'sba loan officer',
			'government guaranteed',
			'small business lending specialist',
			'sba lending officer',
			'sba credit analyst',
			'sba program coordinator',
			'sba relationship manager'
		],
		'company_keywords': [
			'bank',
			'credit union',
			'sba',
			'small business administration',
			'community bank',
			'financial services'
		],
		'matching_keywords': [
			'sba lending',
			'government guaranteed lending',
			'small business loans',
			'small business lending',
			'sba programs'
		]
	},
	
	'loan_broker': {
		'description': 'Loan brokers and intermediaries connecting borrowers to lenders',
		'job_titles': [
			'loan broker',
			'mortgage broker',
			'commercial mortgage broker',
			'business loan broker',
			'lending broker',
			'capital advisor',
			'loan correspondent',
			'loan originator',
			'loan processor',
			'broker',
			'mortgage professional',
			'loan facilitator',
			'commercial finance consultant',
			'financing advisor',
			'capital broker'
		],
		'company_keywords': [
			'mortgage broker',
			'loan broker',
			'brokerage',
			'broker network',
			'lending',
			'financial services',
			'commercial capital'
		],
		'matching_keywords': [
			'commercial lending',
			'loans',
			'finance',
			'business lending',
			'commercial mortgages'
		]
	},
	
	'sales_broker': {
		'description': 'Sales-focused brokers in real estate and business brokerage',
		'job_titles': [
			'cre broker',
			'commercial real estate broker',
			'cre agent',
			'commercial broker',
			'commercial agent',
			'ccim',
			'cbb',
			'real estate advisor',
			'real estate broker',
			'principal broker',
			'business broker',
			'm&a advisor',
			'mergers and acquisitions',
			'm&a intermediary',
			'middle market broker',
			'business sales broker',
			'broker associate',
			'senior broker',
			'commercial agent'
		],
		'company_keywords': [
			'cbre',
			'cushman',
			'colliers',
			'jll',
			'marcus & millichap',
			'cre',
			'commercial real estate',
			'brokerage',
			'realty',
			'm&a',
			'business brokerage'
		],
		'matching_keywords': [
			'commercial real estate',
			'mergers & acquisitions',
			'loans',
			'finance',
			'commercial lending'
		]
	},
	
	'referral_network_other': {
		'description': 'Community leaders, influencers, and connectors in business ecosystem',
		'job_titles': [
			'economic development officer',
			'edo',
			'city planner',
			'urban development',
			'chamber of commerce executive',
			'executive director chamber',
			'cdc director',
			'sbdc director',
			'community development director',
			'business development director',
			'government relations officer',
			'vistage chair',
			'executive coach',
			'ceo coach',
			'business coach',
			'peer advisory facilitator',
			'group facilitator',
			'ceo roundtable leader',
			'leadership coach',
			'nonprofit director',
			'eo board member',
			'ypo member'
		],
		'company_keywords': [
			'chamber',
			'economic development',
			'city of',
			'county of',
			'sbdc',
			'cdc',
			'government',
			'municipality',
			'nonprofit',
			'vistage',
			'eo',
			'ypo',
			'coaching',
			'advisory'
		],
		'matching_keywords': [
			'finance',
			'commercial lending',
			'economic development',
			'government',
			'business development',
			'leadership'
		]
	},
	
	'internal': {
		'description': 'Internal staff and employees of lending organizations',
		'job_titles': [
			'loan officer',
			'business development officer',
			'relationship manager',
			'credit analyst',
			'underwriter',
			'loan processor',
			'loan specialist',
			'commercial lender',
			'account manager',
			'senior analyst',
			'credit officer',
			'risk manager',
			'manager',
			'supervisor',
			'team lead',
			'operations manager',
			'compliance officer',
			'quality assurance specialist',
			'loan coordinator'
		],
		'company_keywords': [
			'bank',
			'credit union',
			'financial services',
			'lender',
			'lending company',
			'fintech',
			'lending platform'
		],
		'matching_keywords': [
			'commercial lending',
			'loans',
			'finance',
			'financial services',
			'credit analysis'
		]
	},
	
	'borrower': {
		'description': 'Active small business owners and decision makers seeking financing',
		'job_titles': [
			'owner',
			'business owner',
			'co-owner',
			'president',
			'ceo',
			'chief executive',
			'cfo',
			'chief financial officer',
			'partner',
			'managing partner',
			'founder',
			'founder & ceo',
			'founder & president',
			'managing member',
			'principal',
			'proprietor',
			'attorney',
			'esquire',
			'partner attorney',
			'managing partner attorney',
			'cpa',
			'financial advisor',
			'wealth manager',
			'cfp',
			'practice owner',
			'practice manager',
			'clinic owner',
			'managing director',
			'executive director',
			'operations director'
		],
		'company_keywords': [
			'llc',
			'inc',
			'corporation',
			'company',
			'group',
			'services',
			'solutions',
			'consulting',
			'medical',
			'dental',
			'veterinary',
			'law firm',
			'legal',
			'practice',
			'clinic',
			'financial advisory',
			'wealth management'
		],
		'matching_keywords': [
			'business owner',
			'entrepreneur',
			'executive',
			'decision maker',
			'management',
			'leadership'
		]
	},
	
	'past_borrower': {
		'description': 'Previous clients and borrowers who have obtained financing',
		'job_titles': [
			'owner',
			'business owner',
			'co-owner',
			'president',
			'ceo',
			'chief executive',
			'cfo',
			'partner',
			'managing partner',
			'founder',
			'managing member',
			'principal',
			'proprietor',
			'retired owner',
			'former owner',
			'former ceo',
			'consultant',
			'advisor',
			'former executive'
		],
		'company_keywords': [
			'llc',
			'inc',
			'corporation',
			'company',
			'group',
			'former',
			'retired',
			'consulting'
		],
		'matching_keywords': [
			'business experience',
			'management',
			'leadership',
			'previous business owner'
		]
	}
}

# Create a summary table
summary_data = []
for persona, details in persona_mappings.items():
	summary_data.append({
		'Persona': persona,
		'Description': details['description'],
		'Sample Job Titles': ', '.join(details['job_titles'][:5]) + '...',
		'Job Title Count': len(details['job_titles']),
		'Key Company Keywords': ', '.join(details['company_keywords'][:4])
	})
	
summary_df = pd.DataFrame(summary_data)
print("=" * 120)
print("PERSONA JOB TITLE MAPPING SUMMARY")
print("=" * 120)
print(summary_df.to_string(index=False))
print("\n")

# Now create detailed breakdown
print("=" * 120)
print("DETAILED JOB TITLE MAPPING BY PERSONA")
print("=" * 120)

for persona, details in persona_mappings.items():
	print(f"\n{'─' * 120}")
	print(f"PERSONA: {persona.upper()}")
	print(f"Description: {details['description']}")
	print(f"{'─' * 120}")
	print(f"\nJob Titles ({len(details['job_titles'])} total):")
	for i, title in enumerate(details['job_titles'], 1):
		print(f"  {i:2d}. {title}")
		
	print(f"\nCompany Keywords:")
	for keyword in details['company_keywords']:
		print(f"  • {keyword}")
		
	print(f"\nMatching Skills/Experience Keywords:")
	for keyword in details['matching_keywords']:
		print(f"  • {keyword}")
		
print("\n" + "=" * 120)
print("CROSS-PERSONA TITLE OVERLAPS")
print("=" * 120)

# Find overlapping titles between personas
all_titles = {}
for persona, details in persona_mappings.items():
	for title in details['job_titles']:
		if title not in all_titles:
			all_titles[title] = []
		all_titles[title].append(persona)
		
# Show titles that appear in multiple personas
overlaps = {title: personas_list for title, personas_list in all_titles.items() if len(personas_list) > 1}
print(f"\nTitles appearing across multiple personas: {len(overlaps)}")
for title, persona_list in sorted(overlaps.items()):
	print(f"  '{title}' → {', '.join(persona_list)}")