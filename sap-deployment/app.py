from flask import Flask, jsonify, request
from transformers import pipeline
import os

app = Flask(__name__)

# Initialize the chatbot pipeline
@app.before_first_request
def load_model():
    global chatbot
    model_name = os.getenv('MODEL_NAME', 'google/flan-t5-small')
    chatbot = pipeline('text2text-generation', model=model_name)

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
        data = request.get_json()
        question = data.get('question', '')
        
        if not question:
            return jsonify({"error": "No question provided"}), 400
        
        # Generate response
        response = chatbot(
            f"Answer this sustainability question: {question}",
            max_length=200,
            do_sample=True,
            temperature=0.7
        )
        
        return jsonify({
            "question": question,
            "answer": response[0]['generated_text']
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)