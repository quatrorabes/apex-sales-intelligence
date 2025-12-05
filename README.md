# 🚀 APEX Sales Intelligence

AI-powered sales intelligence platform for lead enrichment, scoring, and outreach automation.

![Version](https://img.shields.io/badge/version-4.0.0-purple)
![License](https://img.shields.io/badge/license-MIT-blue)

## Features

### 📊 Dashboard
- **Landing Page** — Personalized greeting with quick stats
- **Today's Board** — Prioritized leads by match score
- **4 Contact Views** — Table, Cards, Kanban (drag & drop), Compact
- **Global Search** — `⌘K` to search contacts and pages instantly

### 🧠 Intelligence Engines
- **Match Scoring** — FIT + RELEVANCE + TIMING algorithm
- **Why Me Generator** — AI-generated personalized hooks
- **Email Drafter** — 5 templates + 3-email sequences
- **LinkedIn Generator** — Connection requests + InMails
- **Smart Lists** — 6 auto-segmented lists

### 📈 Analytics
- Tier distribution visualization
- Score breakdown charts
- Cold call funnel metrics
- Top companies by volume

## Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- OpenAI API key

### Installation

Clone the repo
git clone https://github.com/YOUR_USERNAME/apex.git
cd apex

Backend setup
python -m venv venv
source venv/bin/activate # or venv\Scripts\activate on Windows
pip install -r requirements.txt

Create .env file
cat > .env << 'ENVFILE'
OPENAI_API_KEY=your_key_here
DATABASE_URL=/path/to/apex/apex.db
ENVFILE

Frontend setup
cd dashboard_v1
npm install

text

### Running

Terminal 1: Backend
cd ~/projects/apex
python api.py

Terminal 2: Frontend
cd ~/projects/apex/dashboard_v1
npm run dev

text

Open [http://localhost:3000](http://localhost:3000)

## Project Structure

apex/
├── api.py # Flask API server
├── apex.db # SQLite database
├── requirements.txt # Python dependencies
├── .env # Environment variables (not committed)
│
├── apps/
│ └── backend/
│ └── intelligence/
│ ├── scoring/ # Match scoring engine
│ ├── why_me/ # Why Me generator
│ ├── cold_call/ # Cold call queue
│ └── outreach/ # Email & LinkedIn generators
│
└── dashboard_v1/ # React frontend
├── src/
│ ├── components/ # React components
│ ├── App.tsx # Main app with routing
│ └── main.tsx # Entry point
├── package.json
└── tailwind.config.js

text

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/todays-board` | Dashboard data |
| GET | `/api/contacts` | List all contacts |
| GET | `/api/contacts/:id` | Get single contact |
| POST | `/api/contacts/:id/enrich` | Enrich contact |
| POST | `/api/contacts/:id/score` | Score contact |
| POST | `/api/contacts/:id/why-me` | Generate Why Me |
| POST | `/api/contacts/:id/generate-email` | Generate email |
| POST | `/api/contacts/:id/generate-linkedin` | Generate LinkedIn message |
| PUT | `/api/contacts/:id/tier` | Update match tier |
| GET | `/api/analytics` | Pipeline analytics |
| GET | `/api/smart-lists` | Smart list definitions |
| POST | `/api/batch/rescore` | Batch re-score |
| POST | `/api/batch/enrich` | Batch enrich |

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `⌘K` / `Ctrl+K` | Open global search |
| `↑↓` | Navigate results |
| `Enter` | Select/Open |
| `Escape` | Close modal |

## Tech Stack

- **Frontend**: React 18, TypeScript, Tailwind CSS, Vite
- **Backend**: Python, Flask, SQLite
- **AI**: OpenAI GPT-4o
- **Icons**: Lucide React

## License

MIT License - see [LICENSE](LICENSE) for details.

---

Built with ☕ for closers
