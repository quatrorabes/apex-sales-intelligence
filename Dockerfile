FROM python:3.11-slim

WORKDIR /app

# Force cache bust
ENV REBUILD_DATE="2025-12-07T04:30:00Z"

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Use Gunicorn to run Flask app
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8000", "--timeout", "120", "--log-level", "debug", "api:app"]
