FROM python:3.11-slim

# Force fresh build - 1765089056
ARG CACHEBUST=1765089056

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Force fresh copy
COPY api.py ./api.py
COPY playbook_api.py ./playbook_api.py
COPY *.json ./

EXPOSE 8000
CMD ["python", "api.py"]
