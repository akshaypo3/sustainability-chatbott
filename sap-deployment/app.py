from flask import Flask, jsonify, request
from transformers import pipeline
import os
import logging
import re

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
        model_name = os.getenv('MODEL_NAME', 'google/flan-t5-base')
        logger.info(f"Loading model: {model_name}")
        
        chatbot = pipeline(
            'text2text-generation', 
            model=model_name,
            device=-1
        )
        logger.info("Model loaded successfully")
    except Exception as e:
        logger.error(f"Error loading model: {e}")
        raise

# Load model when module is imported
load_model()

def is_sustainability_related(question):
    """Check if question is related to sustainability"""
    sustainability_keywords = [
        'sustainab', 'environment', 'eco', 'green', 'renewable', 'carbon', 'climate',
        'energy', 'recycle', 'waste', 'pollution', 'conservation', 'biodiversity',
        'solar', 'wind', 'hydro', 'geothermal', 'organic', 'compost', 'emission',
        'electric vehicle', 'ev', 'zero waste', 'circular economy', 'green building',
        'sustainable development', 'clean energy', 'carbon footprint', 'global warming'
    ]
    
    question_lower = question.lower()
    return any(keyword in question_lower for keyword in sustainability_keywords)

@app.route('/health')
def health():
    return jsonify({"status": "healthy"})

@app.route('/')
def home():
    return jsonify({
        "message": "Sustainability Expert Chatbot API",
        "model": os.getenv('MODEL_NAME', 'google/flan-t5-base'),
        "endpoints": ["/health", "/chat", "/"],
        "specialization": "Sustainability and Environmental topics only"
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
            
        question = data.get('question', '').strip()
        if not question:
            return jsonify({"error": "No question provided"}), 400
        
        logger.info(f"Received question: {question}")
        
        # Check if question is sustainability-related
        if not is_sustainability_related(question):
            return jsonify({
                "question": question,
                "answer": "I specialize only in sustainability and environmental topics. Please ask me about renewable energy, climate change, recycling, green technology, or other environmental subjects.",
                "topic_restriction": "sustainability_only"
            })
        
        # PROFESSIONAL PROMPT THAT WORKS:
        prompt = f"""Q: {question}
A: """
        
        # Generate response with optimized parameters
        response = chatbot(
            prompt,
            max_length=100,
            min_length=20,
            do_sample=True,
            temperature=0.3,  # Lower temperature for more focused answers
            top_p=0.9,
            top_k=30,
            repetition_penalty=2.0,  # Very high penalty for repetition
            num_beams=4,
            early_stopping=True,
            no_repeat_ngram_size=2  # Prevent repeating 2-word phrases
        )
        
        answer = response[0]['generated_text'].strip()
        
        # Clean up the response
        answer = re.sub(r'^(Q:|A:|Question:|Answer:)', '', answer, flags=re.IGNORECASE)
        answer = answer.strip()
        
        # Ensure the answer makes sense
        if not answer or len(answer) < 10:
            answer = "I provide information on sustainability topics. Please ask about renewable energy, environmental conservation, climate action, or green technology."
        
        logger.info(f"Generated answer: {answer}")
        
        return jsonify({
            "question": question,
            "answer": answer,
            "topic": "sustainability"
        })
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        return jsonify({"error": str(e)}), 500
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
