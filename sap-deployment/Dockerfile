# Use lightweight Python base
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies (needed for torch, transformers)
RUN apt-get update && apt-get install -y \
    git \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for caching
COPY requirements.txt /app/requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code
COPY . /app

EXPOSE 5000

# Run the app
CMD ["python", "app.py"]
