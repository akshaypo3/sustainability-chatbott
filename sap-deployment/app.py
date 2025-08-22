from flask import Flask, jsonify, request
from transformers import pipeline
import os
import logging

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global variable for the pipeline
chatbot = None

def load_model():
    """Load the model pipeline"""
    global chatbot
    try:
        model_name = os.getenv('MODEL_NAME', 'google/flan-t5-small')
        logger.info(f"Loading model: {model_name}")
        
        chatbot = pipeline(
            'text2text-generation', 
            model=model_name,
            device=-1  # Use CPU (-1 for CPU, 0 for GPU)
        )
        logger.info("Model loaded successfully")
    except Exception as e:
        logger.error(f"Error loading model: {e}")
        raise

@app.before_request
def before_request():
    """Load model before first request"""
    global chatbot
    if chatbot is None:
        load_model()

@app.route('/health')
def health():
    return jsonify({"status": "healthy"})

@app.route('/')
def home():
    return jsonify({
        "message": "Sustainability Chatbot API",
        "model": os.getenv('MODEL_NAME', 'google/flan-t5-small'),
        "endpoints": ["/health", "/chat", "/"]
    })

@app.route('/chat', methods=['POST'])
def chat():
    try:
        global chatbot
        if chatbot is None:
            load_model()
            
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
            
        question = data.get('question', '')
        if not question:
            return jsonify({"error": "No question provided"}), 400
        
        logger.info(f"Received question: {question}")
        
        # Generate response
        response = chatbot(
            f"Answer this sustainability question: {question}",
            max_length=200,
            do_sample=True,
            temperature=0.7
        )
        
        answer = response[0]['generated_text']
        logger.info(f"Generated answer: {answer}")
        
        return jsonify({
            "question": question,
            "answer": answer
        })
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Load model when starting in development mode
    load_model()
    app.run(host='0.0.0.0', port=5000, debug=True)