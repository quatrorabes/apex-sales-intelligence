FROM python:3.11-slim

# Force rebuild
ARG CACHEBUST=1

WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all Python files and JSON configs
COPY *.py ./
COPY *.json ./

# Expose port
EXPOSE 8000

# Run with Python (Flask dev server)
CMD ["python", "api.py"]
