# Connect to Railway Postgres and check schema
# First, get your DATABASE_URL from Railway dashboard, then:
psql "YOUR_DATABASE_URL" -c "\d contacts"
