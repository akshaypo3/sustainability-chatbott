FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

# Copy requirements first for caching
COPY requirements.txt /app/requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Warm up the model so runtime is faster
RUN python - <<'PY'
from transformers import pipeline
pipeline('text2text-generation', model='google/flan-t5-small')
PY

# Copy app code
COPY app.py /app/app.py

EXPOSE 5000

# Run the app with gunicorn
CMD ["gunicorn", "--workers", "2", "--threads", "4", "--timeout", "120", "--bind", "0.0.0.0:5000", "app:app"]
