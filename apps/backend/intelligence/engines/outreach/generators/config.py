import os
APEX_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '../' * 6))
DB_PATH = os.path.join(APEX_ROOT, 'apex.db')
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY")
