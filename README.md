# APEX Sales Intelligence Platform

AI-powered contact enrichment and scoring system for Commercial Real Estate professionals.

## Features

- **HubSpot Integration**: Import and sync contacts
- **AI Enrichment**: Automated research using Perplexity AI
- **CRE-Focused Scoring**: MDCP + RSS scoring optimized for Commercial Real Estate
- **Intelligent Filtering**: Target only relevant CRE professionals
- **Cadence Management**: Automated outreach sequences
- **Dashboard**: React-based analytics and management interface

## Tech Stack

- **Backend**: Python/Flask API
- **Frontend**: React/TypeScript with Vite
- **Database**: SQLite
- **AI**: Perplexity API, OpenAI
- **Integrations**: HubSpot CRM

## Project Structure

apex/
├── api.py # Main Flask API
├── apps/
│ └── backend/
│ └── intelligence/
│ └── engines/
│ ├── enrichment/ # Contact enrichment logic
│ └── scoring/ # CRE-specific scoring engines
├── dashboard_v1/ # React frontend
│ ├── src/
│ │ ├── components/ # React components
│ │ └── App.tsx # Main app
│ └── package.json
├── apex.db # SQLite database (git-ignored)
└── .env # Environment variables (git-ignored)

text

## Setup

1. Clone the repository
2. Create virtual environment: `python -m venv venv`
3. Install Python dependencies: `pip install -r requirements.txt`
4. Install React dependencies: `cd dashboard_v1 && npm install`
5. Copy `.env.example` to `.env` and add your API keys
6. Run migrations: `python migrate.py`
7. Start API: `python api.py`
8. Start frontend: `cd dashboard_v1 && npm run dev`

## Environment Variables

Required in `.env`:
- `HUBSPOT_TOKEN`: HubSpot private app token
- `PERPLEXITY_API_KEY`: Perplexity AI key
- `OPENAI_API_KEY`: OpenAI API key
- `APEX_SCORING_PROFILE`: CRE_MORTGAGE, CRE_BROKERAGE, or COMMERCIAL_BANKING

## Scoring Profiles

The system uses industry-specific scoring profiles:
- **CRE_MORTGAGE**: Commercial mortgage brokers and lenders
- **CRE_BROKERAGE**: Commercial real estate brokers
- **COMMERCIAL_BANKING**: Commercial relationship managers

## API Endpoints

- `POST /api/hubspot/import`: Import contacts from HubSpot
- `POST /api/contacts/:id/enrich`: Enrich a contact
- `POST /api/contacts/:id/score`: Score a contact
- `POST /api/contacts/score-batch`: Batch scoring
- `GET /api/apex/scores`: Get all scored contacts

## License

Proprietary - All Rights Reserved
