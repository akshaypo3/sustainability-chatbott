FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# System deps for torch wheels
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc g++ curl && \
    rm -rf /var/lib/apt/lists/*

# Install Python deps (version pins reduce build flakiness)
RUN pip install --no-cache-dir \
    "flask==3.0.3" \
    "transformers==4.41.2" \
    "torch==2.2.2" \
    "gunicorn==21.2.0"

# Warm up the model so runtime is faster
RUN python - <<'PY'\nfrom transformers import pipeline\npipeline('text2text-generation', model='google/flan-t5-small')\nPY

COPY app.py /app/app.py

EXPOSE 5000
CMD ["gunicorn", "--workers", "2", "--threads", "4", "--timeout", "120", "--bind", "0.0.0.0:5000", "app:app"]
