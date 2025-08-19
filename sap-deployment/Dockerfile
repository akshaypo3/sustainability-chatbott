FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install flask==2.3.2 transformers==4.30.2 torch --extra-index-url https://download.pytorch.org/whl/cpu accelerate sentencepiece protobuf

# Copy app code
COPY app.py .

EXPOSE 5000

# Add delay for SAP AI Core startup
CMD sleep 10 && python app.py