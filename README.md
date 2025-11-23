# APEX Sales Intelligence Platform

AI-Powered Contact Enrichment & Scoring System for Commercial Real Estate & SBA Lending

## Features

- **HubSpot Integration** - Automated contact import with filtering
- **AI Enrichment** - Perplexity AI-powered contact research
- **MDCP/RSS Scoring** - Adaptive dual-scoring engine
- **Persona Classification** - Automatic lead type detection
- **Priority Intelligence** - Action-ready contact insights

## Tech Stack

### Backend
- Python 3.11+
- Flask API Server
- SQLite Database
- Perplexity AI API
- HubSpot CRM API

### Frontend
- React 18 + TypeScript
- Vite
- Tailwind CSS
- Lucide Icons

## Project Structure

apex/
├── api.py # Flask API server
├── apex.db # SQLite database
├── .env # Environment variables (not in git)
├── apps/
│ └── backend/
│ └── intelligence/
│ └── engines/
│ ├── enrichment/
│ │ ├── apex_intelligence_engine.py
│ │ ├── scoring_orchestrator.py
│ │ └── perplexity_enrichment.py
│ └── scoring/
│ └── persona_classifier_cre_sba.py
└── dashboard_v1/ # React frontend
├── src/
│ ├── App.tsx
│ └── components/
└── package.json

text

## Setup

### 1. Environment Variables

Create `.env` file:

HubSpot
HUBSPOT_ACCESS_TOKEN=your_token_here

AI APIs
PERPLEXITY_API_KEY=your_key_here
OPENAI_API_KEY=your_key_here

text

### 2. Backend Setup

Create virtual environment
python3 -m venv venv
source venv/bin/activate

Install dependencies
pip install flask flask-cors python-dotenv requests

Run backend
python api.py

text

Backend runs on: http://localhost:8000

### 3. Frontend Setup

cd dashboard_v1

Install dependencies
npm install

Run development server
npm run dev

text

Frontend runs on: http://localhost:5173

## API Endpoints

### Contacts
- `GET /api/contacts` - List all contacts
- `GET /api/contacts/:id` - Get contact details
- `POST /api/hubspot/import` - Import from HubSpot

### Scoring
- `POST /api/contacts/:id/score` - Score single contact
- `POST /api/contacts/score-batch` - Score multiple contacts
- `GET /api/contacts/:id/scores` - Get contact scores

### Analytics
- `GET /api/analytics/dashboard` - Dashboard metrics

## Scoring System

### MDCP Score (Money, Decision, Credibility, Pain)
- **HOT**: 85+ (Immediate action)
- **WARM**: 70-84 (High priority)
- **QUALIFIED**: 55-69 (Standard outreach)
- **COLD**: <55 (Long-term nurture)

### RSS Score (Relationship Strength)
- **PLATINUM**: 80+ (Established relationship)
- **GOLD**: 65-79 (Active engagement)
- **SILVER**: 50-64 (Warming)
- **BRONZE**: <50 (New contact)

### Priority Score
Blended MDCP + RSS weighted by lifecycle stage

## Development

### Database Schema

CREATE TABLE contacts (
id INTEGER PRIMARY KEY,
name TEXT NOT NULL,
email TEXT,
company TEXT,
title TEXT,
mdcp_score REAL,
rss_score REAL,
priority_score REAL,
urgency_level TEXT,
enrichment_status TEXT,
-- ... more fields
);

text

### Running Tests

Score a contact
curl -X POST http://localhost:8000/api/contacts/1/score

Import from HubSpot
curl -X POST http://localhost:8000/api/hubspot/import

text

## Deployment

- **Backend**: Railway, Render, or Heroku
- **Frontend**: Vercel, Netlify
- **Database**: Railway PostgreSQL (for production)

## License

Private - All Rights Reserved

## Author

Chris Rabenold
