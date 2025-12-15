# Railway Environment Variables

## API Service (Backend)
Set these in Railway Dashboard → API Service → Variables:

OPENAI_API_KEY=sk-your-key-here
DATABASE_URL=/app/apex.db
FLASK_DEBUG=0
PYTHON_VERSION=3.11

text

## Dashboard Service (Frontend)
Set these in Railway Dashboard → Dashboard Service → Variables:

VITE_API_URL=https://your-api-service.up.railway.app
NODE_ENV=production

text

## Notes
- Replace `your-api-service` with actual Railway URL after deployment
- DATABASE_URL uses SQLite locally; for production, consider PostgreSQL
