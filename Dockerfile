# Use lightweight Python image
FROM python:3.9-slim

# Install dependencies
RUN pip install torch transformers flask gunicorn

# Download model & tokenizer
RUN python -c "from transformers import pipeline; pipeline('text2text-generation', model='google/flan-t5-small')"

# Copy app code
COPY app.py /app/app.py

# Run Flask server
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]