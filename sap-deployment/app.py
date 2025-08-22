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
        model_name = os.getenv('MODEL_NAME', 'google/flan-t5-base')  # Use base for better quality
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

# Pre-defined professional answers for common questions
PROFESSIONAL_ANSWERS = {
    'solar': "Solar energy harnesses sunlight through photovoltaic panels to generate clean electricity. It's a renewable source that reduces carbon emissions, lowers energy costs, and decreases dependence on fossil fuels. Solar power is key to sustainable energy transition.",
    
    'renewable': "Renewable energy comes from naturally replenished sources like sunlight, wind, water, and geothermal heat. These sustainable alternatives to fossil fuels reduce greenhouse gas emissions, promote energy independence, and support environmental conservation.",
    
    'wind': "Wind power converts wind energy into electricity using turbines. It's a clean, renewable energy source that produces zero emissions, reduces air pollution, and contributes to climate change mitigation through sustainable power generation.",
    
    'recycl': "Recycling conserves natural resources by reprocessing materials into new products. It reduces landfill waste, saves energy, decreases pollution, and supports circular economy principles for sustainable waste management.",
    
    'climate': "Climate change refers to long-term shifts in global weather patterns primarily caused by human activities like burning fossil fuels. Sustainable solutions include renewable energy adoption, emissions reduction, and environmental conservation efforts.",
    
    'environment': "Environmental sustainability involves protecting natural resources and ecosystems while meeting human needs. It encompasses renewable energy, waste reduction, conservation, and practices that minimize ecological impact for future generations.",
    
    'energy': "Sustainable energy focuses on renewable sources like solar, wind, and hydropower that minimize environmental impact. These clean alternatives reduce carbon emissions, promote energy security, and support long-term ecological balance.",
    
    'green': "Green technology encompasses environmentally friendly solutions like renewable energy systems, energy-efficient devices, sustainable materials, and clean transportation. These innovations reduce ecological footprint and promote sustainable development."
}

def get_professional_answer(question):
    """Get pre-defined professional answer based on keywords"""
    question_lower = question.lower()
    
    # Check for specific keywords and return pre-defined answers
    for keyword, answer in PROFESSIONAL_ANSWERS.items():
        if keyword in question_lower:
            return answer
    
    # Default professional answer for other sustainability questions
    return "Sustainable practices focus on renewable resources, environmental protection, and reducing carbon footprint. This includes adopting clean energy, efficient resource use, and conservation efforts to maintain ecological balance for future generations."

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
        
        # Use pre-defined professional answers for reliability
        professional_answer = get_professional_answer(question)
        
        # Only use AI for complex questions if needed
        if len(question.split()) > 4:  # Complex questions
            try:
                prompt = f"Provide a concise professional answer about sustainability: {question}"
                response = chatbot(
                    prompt,
                    max_length=120,
                    do_sample=True,
                    temperature=0.3,
                    top_p=0.85
                )
                ai_answer = response[0]['generated_text'].strip()
                if len(ai_answer) > 20 and not any(x in ai_answer for x in ['?', '(', ')', '[', ']']):
                    professional_answer = ai_answer
            except:
                pass  # Fall back to pre-defined answer
        
        return jsonify({
            "question": question,
            "answer": professional_answer,
            "topic": "sustainability"
        })
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        # Fallback to pre-defined answer
        return jsonify({
            "question": question,
            "answer": get_professional_answer(question),
            "topic": "sustainability",
            "error_handled": True
        })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)