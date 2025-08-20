from flask import Flask, request, jsonify
from transformers import pipeline
import time
import os

app = Flask(__name__)

# Load model with CPU explicitly
model = pipeline(
    "text2text-generation", 
    model="google/flan-t5-small",
    device=-1  # Force CPU
)

@app.route('/v1/predict', methods=['POST'])
def predict():
    data = request.get_json(force=True, silent=True) or {}
    prompt = data.get("prompt", "")
    try:
        response = model(prompt, max_length=200)
        return jsonify({"answer": response[0]["generated_text"], "status": "success"})
    except Exception as e:
        return jsonify({"error": str(e), "status": "error"}), 500

@app.route('/v2/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy", "ready": True})

if __name__ == '__main__':
    time.sleep(45)
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)), debug=False)
