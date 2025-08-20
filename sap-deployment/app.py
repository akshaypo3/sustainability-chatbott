from flask import Flask, request, jsonify
from transformers import pipeline
import time
import os

app = Flask(__name__)

# Load model with CPU explicitly and error handling
def load_model():
    try:
        print("Loading FLAN-T5 model...")
        model = pipeline(
            "text2text-generation", 
            model="google/flan-t5-small",
            device=-1,  # Force CPU
            torch_dtype="auto"
        )
        print("Model loaded successfully!")
        return model
    except Exception as e:
        print(f"Model loading failed: {str(e)}")
        raise e

model = load_model()

@app.route('/v1/models/sustainability-chatbot:predict', methods=['POST'])
def predict():
    try:
        data = request.get_json()
        if not data or 'prompt' not in data:
            return jsonify({"error": "Missing 'prompt' in request"}), 400
            
        prompt = data['prompt']
        response = model(prompt, max_length=150, num_return_sequences=1)
        
        return jsonify({
            "answer": response[0]["generated_text"],
            "status": "success"
        })
    except Exception as e:
        return jsonify({"error": str(e), "status": "error"}), 500

@app.route('/v2/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy", "model_loaded": True})

@app.route('/v1/models/sustainability-chatbot', methods=['GET'])
def model_info():
    return jsonify({
        "name": "sustainability-chatbot",
        "version": "1.0",
        "ready": True
    })

if __name__ == '__main__':
    time.sleep(30)  # Give SAP time to initialize
    print("Starting sustainability chatbot server...")
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)), debug=False)