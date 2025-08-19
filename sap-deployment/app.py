from flask import Flask, request, jsonify
from transformers import pipeline
import os
import time

app = Flask(__name__)

# Initialize model as None
model = None

def load_model():
    global model
    if model is None:
        print("Loading FLAN-T5 model...")
        try:
            # Load with CPU only and smaller settings
            model = pipeline(
                "text2text-generation", 
                model="google/flan-t5-small",
                device=-1,  # Force CPU
                torch_dtype="auto",
                low_cpu_mem_usage=True
            )
            print("✅ Model loaded successfully")
        except Exception as e:
            print(f"❌ Model loading failed: {str(e)}")
            raise e

@app.route('/v2/health', methods=['GET'])
def health():
    try:
        load_model()
        return jsonify({"status": "healthy", "model_loaded": model is not None}), 200
    except Exception as e:
        return jsonify({"status": "unhealthy", "error": str(e)}), 500

@app.route('/v2/predict', methods=['POST'])
def predict():
    try:
        load_model()
        
        data = request.get_json()
        if not data or 'prompt' not in data:
            return jsonify({"error": "Missing 'prompt' in request"}), 400
            
        prompt = data['prompt']
        
        # Generate response with safe parameters
        response = model(
            prompt, 
            max_length=100,
            min_length=1,
            num_return_sequences=1,
            early_stopping=True
        )
        
        return jsonify({
            "answer": response[0]["generated_text"],
            "status": "success"
        })
        
    except Exception as e:
        return jsonify({"error": str(e), "status": "error"}), 500

@app.route('/', methods=['GET'])
def home():
    return jsonify({"message": "Sustainability Chatbot API"})

if __name__ == '__main__':
    # Give time for SAP AI Core health checks
    time.sleep(5)
    print("Starting Flask server...")
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)), debug=False, threaded=True)