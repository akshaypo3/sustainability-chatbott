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

# Enhanced professional answers with better coverage
PROFESSIONAL_ANSWERS = {
    'solar': "Solar energy harnesses sunlight through photovoltaic panels to generate clean electricity. It reduces carbon emissions by 95% compared to fossil fuels, lowers energy costs, decreases dependence on non-renewable resources, and supports sustainable development. Solar power is renewable, abundant, and creates green jobs while mitigating climate change impacts.",
    
    'renewable': "Renewable energy comes from naturally replenished sources like sunlight, wind, water, and geothermal heat. These sustainable alternatives reduce greenhouse gas emissions by 80-90%, promote energy independence, improve air quality, and support environmental conservation. Renewable energy is crucial for achieving net-zero emissions and sustainable economic growth.",
    
    'wind': "Wind power converts kinetic energy from wind into electricity using turbines. It's a clean, renewable energy source that produces zero emissions, reduces air pollution, creates local jobs, and contributes to climate change mitigation. Modern wind farms can power thousands of homes while preserving natural resources and reducing water consumption compared to conventional power plants.",
    
    'recycl': "Recycling conserves natural resources by reprocessing materials into new products. It reduces landfill waste by 75%, saves 95% of energy compared to virgin material production, decreases pollution, conserves natural habitats, and supports circular economy principles. Effective recycling reduces greenhouse gas emissions and extends the lifespan of valuable resources.",
    
    'climate': "Climate change refers to long-term shifts in global weather patterns primarily caused by human activities like burning fossil fuels. Sustainable solutions include renewable energy adoption (solar, wind, hydro), energy efficiency improvements, reforestation, sustainable agriculture, carbon capture technologies, and international cooperation to reduce emissions by 45% by 2030.",
    
    'environment': "Environmental sustainability involves protecting natural resources and ecosystems while meeting human needs. It encompasses renewable energy systems, waste reduction strategies, biodiversity conservation, water management, sustainable agriculture, and green infrastructure development to minimize ecological impact and ensure resources for future generations.",
    
    'energy': "Sustainable energy focuses on renewable sources that minimize environmental impact. Solar, wind, hydro, geothermal, and biomass energy reduce carbon emissions by 80-100%, enhance energy security, create green jobs, improve public health, and support economic stability while preserving natural resources for future generations.",
    
    'green': "Green technology encompasses environmentally friendly solutions including renewable energy systems, energy-efficient devices, sustainable materials, electric vehicles, smart grids, water purification systems, and waste management technologies. These innovations reduce ecological footprint, conserve resources, and promote sustainable economic development while addressing climate change challenges."
}

def get_professional_answer(question):
    """Get pre-defined professional answer based on keywords"""
    question_lower = question.lower()
    
    # Check for specific keywords and return pre-defined answers
    for keyword, answer in PROFESSIONAL_ANSWERS.items():
        if keyword in question_lower:
            return answer
    
    # For other questions, use AI with MUCH better prompt engineering
    return generate_ai_answer(question)

def generate_ai_answer(question):
    """Generate AI answer with optimized prompt engineering"""
    try:
        # MUCH BETTER PROMPT ENGINEERING
        prompt = f"""As a sustainability expert with 15 years experience, provide a comprehensive yet concise answer.

Question: {question}

Please structure your response with:
1. Clear definition and scientific explanation
2. Environmental benefits and impact metrics
3. Practical applications and real-world examples
4. Importance for sustainable development goals
5. Future outlook and trends

Ensure the answer is:
- Professionally toned and evidence-based
- 100-150 words maximum
- Focused on factual information
- Free of repetition and vague statements
- Contains specific data where possible

Expert analysis:"""
        
        # Optimized generation parameters
        response = chatbot(
            prompt,
            max_length=200,
            min_length=80,
            do_sample=True,
            temperature=0.4,  # Lower for more factual responses
            top_p=0.9,
            top_k=40,
            repetition_penalty=1.3,
            num_beams=4,
            early_stopping=True,
            no_repeat_ngram_size=3
        )
        
        answer = response[0]['generated_text'].strip()
        
        # Enhanced cleaning
        answer = re.sub(r'(Expert analysis:|Question:|Answer:|Response:|sustainability expert|Q:|A:)', '', answer, flags=re.IGNORECASE)
        answer = re.sub(r'\s+', ' ', answer).strip()
        
        # Quality check - ensure meaningful response
        if len(answer) < 30 or any(x in answer for x in ['?', '(', ')', '[', ']', '1.', '2.', '3.']):
            return "I provide detailed information on sustainability topics. Could you please rephrase your question to be more specific about environmental, renewable energy, or conservation topics?"
        
        return answer
        
    except Exception as e:
        logger.error(f"AI generation error: {e}")
        return "Sustainable practices focus on renewable resources, environmental protection, and reducing carbon footprint through clean energy adoption, efficient resource management, and conservation efforts that maintain ecological balance for future generations."

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
                "answer": "I specialize only in sustainability and environmental topics. Please ask me about renewable energy, climate change, recycling, green technology, conservation, or other environmental subjects.",
                "topic_restriction": "sustainability_only"
            })
        
        # Get professional answer
        professional_answer = get_professional_answer(question)
        
        return jsonify({
            "question": question,
            "answer": professional_answer,
            "topic": "sustainability"
        })
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        return jsonify({
            "question": question,
            "answer": "I provide expert information on sustainability topics including renewable energy, environmental conservation, climate action, and green technology. Please ask your question again.",
            "topic": "sustainability",
            "error_handled": True
        })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)