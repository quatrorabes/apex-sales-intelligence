#!/usr/bin/env python3

#!/usr/bin/env python3
"""
APEX Content Generation Module
Orchestrates all content generation scripts
"""

import subprocess
import sys
import os
from typing import Dict
from config import DB_PATH

# Ensure we're in the right directory
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

def run_email_generator(contact_id: int) -> Dict:
	"""Generate 3 email variants using OpenAI"""
	try:
		result = subprocess.run(
			[sys.executable, 'email_generator.py', str(contact_id)],
			capture_output=True,
			text=True,
			timeout=60,
			cwd=SCRIPT_DIR
		)
		
		if result.returncode == 0:
			return {
				'success': True,
				'message': '3 email variants generated',
				'output': result.stdout
			}
		else:
			return {
				'success': False,
				'error': result.stderr or 'Email generation failed'
			}
	except subprocess.TimeoutExpired:
		return {'success': False, 'error': 'Email generation timed out'}
	except Exception as e:
		return {'success': False, 'error': str(e)}
	
	
def run_call_script_generator(contact_id: int) -> Dict:
	"""Generate 3 call scripts with DISC personality optimization"""
	try:
		result = subprocess.run(
			[sys.executable, 'call_script_generator.py', str(contact_id)],
			capture_output=True,
			text=True,
			timeout=60,
			cwd=SCRIPT_DIR
		)
		
		if result.returncode == 0:
			return {
				'success': True,
				'message': '3 call scripts generated',
				'output': result.stdout
			}
		else:
			return {
				'success': False,
				'error': result.stderr or 'Call script generation failed'
			}
	except subprocess.TimeoutExpired:
		return {'success': False, 'error': 'Call script generation timed out'}
	except Exception as e:
		return {'success': False, 'error': str(e)}
	
	
def run_linkedin_generator(contact_id: int) -> Dict:
	"""Generate LinkedIn connection request + follow-up message"""
	try:
		result = subprocess.run(
			[sys.executable, 'linkedin_automation.py', 'message', str(contact_id)],
			capture_output=True,
			text=True,
			timeout=60,
			cwd=SCRIPT_DIR
		)
		
		if result.returncode == 0:
			return {
				'success': True,
				'message': 'LinkedIn messages generated',
				'output': result.stdout
			}
		else:
			return {
				'success': False,
				'error': result.stderr or 'LinkedIn generation failed'
			}
	except subprocess.TimeoutExpired:
		return {'success': False, 'error': 'LinkedIn generation timed out'}
	except Exception as e:
		return {'success': False, 'error': str(e)}
	
	
def run_sales_nav_generator(contact_id: int) -> Dict:
	"""Generate Sales Navigator insights and outreach strategy"""
	try:
		result = subprocess.run(
			[sys.executable, 'linkedin_sales_nav.py', 'strategy', str(contact_id)],
			capture_output=True,
			text=True,
			timeout=60,
			cwd=SCRIPT_DIR
		)
		
		if result.returncode == 0:
			return {
				'success': True,
				'message': 'Sales Nav strategy generated',
				'output': result.stdout
			}
		else:
			return {
				'success': False,
				'error': result.stderr or 'Sales Nav generation failed'
			}
	except subprocess.TimeoutExpired:
		return {'success': False, 'error': 'Sales Nav generation timed out'}
	except Exception as e:
		return {'success': False, 'error': str(e)}
	
	
# Export all functions
__all__ = [
	'run_email_generator',
	'run_call_script_generator',
	'run_linkedin_generator',
	'run_sales_nav_generator'
]
