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
        model_name = os.getenv('MODEL_NAME', 'google/flan-t5-base')  # Default to flan-t5-base
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

# Load model at startup
load_model()

def is_sustainability_related(question):
    """Check if question is related to sustainability"""
    sustainability_keywords = [
        'sustainab', 'environment', 'eco', 'green', 'renewable', 'carbon', 'climate',
        'energy', 'recycle', 'waste', 'pollution', 'conservation', 'biodiversity',
        'solar', 'wind', 'hydro', 'geothermal', 'organic', 'compost', 'emission',
        'electric vehicle', 'ev', 'zero waste', 'circular economy', 'green building',
        'sustainable development', 'clean energy', 'carbon footprint', 'global warming',
        'water conservation', 'deforestation', 'ecosystem', 'sustainable farming'
    ]
    
    question_lower = question.lower()
    return any(keyword in question_lower for keyword in sustainability_keywords)

# Pre-defined professional answers for reliability
PROFESSIONAL_ANSWERS = {
    'solar': "Solar energy harnesses sunlight through photovoltaic panels to generate clean electricity. It's a renewable source that reduces carbon emissions, lowers energy costs, and decreases dependence on fossil fuels.",
    
    'renewable': "Renewable energy comes from naturally replenished sources like sunlight, wind, water, and geothermal heat. These sustainable alternatives reduce greenhouse gas emissions and support long-term environmental protection.",
    
    'wind': "Wind power converts the kinetic energy of moving air into electricity using turbines. It produces no emissions, helps reduce dependence on fossil fuels, and supports climate change mitigation.",
    
    'recycl': "Recycling conserves natural resources by reprocessing materials into new products. It reduces landfill waste, saves energy, decreases pollution, and supports a circular economy.",
    
    'climate': "Climate change refers to long-term shifts in temperature and weather patterns mainly caused by human activity. Solutions include adopting renewable energy, cutting emissions, and protecting ecosystems.",
    
    'environment': "Environmental sustainability means protecting natural resources and ecosystems while meeting human needs. It includes renewable energy, waste reduction, and conservation efforts.",
    
    'energy': "Sustainable energy focuses on renewable sources like solar, wind, and hydropower that minimize environmental impact. These alternatives reduce carbon emissions and promote energy security.",
    
    'green': "Green technology includes eco-friendly solutions like renewable energy, sustainable construction, and clean transportation. It reduces environmental impact while supporting sustainable growth.",
    
    'water': "Water conservation involves efficient use of water to ensure long-term availability. Methods include rainwater harvesting, fixing leaks, and sustainable irrigation practices.",
    
    'deforestation': "Deforestation is the clearing of forests for agriculture, logging, or development. It threatens biodiversity and accelerates climate change. Reforestation and sustainable land management are key solutions."
}

def get_professional_answer(question):
    """Get pre-defined professional answer based on keywords"""
    question_lower = question.lower()
    
    for keyword, answer in PROFESSIONAL_ANSWERS.items():
        if keyword in question_lower:
            return answer
    
    return "Sustainable practices focus on renewable resources, environmental protection, and reducing carbon footprint. This includes clean energy adoption, efficient resource use, and conservation for future generations."

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
        
        # Check if sustainability-related
        if not is_sustainability_related(question):
            return jsonify({
                "question": question,
                "answer": "I specialize only in sustainability and environmental topics. Please ask me about renewable energy, climate change, recycling, or related subjects.",
                "topic_restriction": "sustainability_only"
            })
        
        # Default professional answer
        professional_answer = get_professional_answer(question)
        
        # Use AI for complex questions (5+ words)
        if len(question.split()) > 4:
            try:
                prompt = f"""
You are a sustainability expert.
Answer the following question with accurate, professional, and non-repetitive information.
Guidelines:
- Stay strictly on sustainability and environmental topics.
- Give a clear, factual explanation (3–5 sentences).
- Do not repeat words or phrases.
- Do not invent false facts. If unsure, politely say the answer is not available.
- Keep the tone professional and easy to understand.

Question: {question}
Answer:
"""
                response = chatbot(
                    prompt,
                    max_length=180,
                    do_sample=False,   # Deterministic output
                    temperature=0.0    # Prevent hallucination
                )
                ai_answer = response[0]['generated_text'].strip()
                
                if len(ai_answer) > 20 and not any(x in ai_answer for x in ['?', '(', ')', '[', ']']):
                    professional_answer = ai_answer
            except Exception as e:
                logger.error(f"AI generation failed, fallback used: {e}")
        
        return jsonify({
            "question": question,
            "answer": professional_answer,
            "topic": "sustainability"
        })
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        return jsonify({
            "question": question,
            "answer": get_professional_answer(question),
            "topic": "sustainability",
            "error_handled": True
        })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
