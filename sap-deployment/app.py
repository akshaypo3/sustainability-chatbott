from flask import Flask, request, jsonify
from transformers import pipeline
import os

app = Flask(__name__)

# Initialize model at startup (no more before_first_request)
model = pipeline("text2text-generation", model="google/flan-t5-small")

@app.route('/v1/predict', methods=['POST'])
def predict():
    data = request.get_json()
    prompt = data.get("prompt", "")
    
    try:
        response = model(prompt, max_length=200)
        return jsonify({
            "answer": response[0]["generated_text"],
            "status": "success"
        })
    except Exception as e:
        return jsonify({
            "error": str(e),
            "status": "error"
        }), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)