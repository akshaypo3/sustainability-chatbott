from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)
SAP_API_URL = os.getenv('SAP_MODEL_URL')  # Will be provided by SAP

@app.route('/v1/predict', methods=['POST'])
def predict():
    data = request.json
    prompt = data.get("prompt", "")
    
    # Forward to SAP's model server
    response = requests.post(
        f"{SAP_API_URL}/v1/models/model:predict",
        json={"prompt": prompt}
    )
    
    return jsonify(response.json())

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy"})