FROM python:3.11-slim

# Force rebuild with timestamp
ARG CACHE_BUST=1
ENV CACHE_BUST_TIME="2025-12-07T06:00:00Z"

WORKDIR /app

# Copy requirements and install (fresh)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy ALL application code (fresh)
COPY api.py .
COPY playbook_api.py .
COPY playbook.json .

# Expose port
EXPOSE 8000

# Use Python directly (Flask dev server works, Gunicorn crashes)
CMD ["python", "api.py"]
