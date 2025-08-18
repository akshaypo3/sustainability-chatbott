from flask import Flask, request, jsonify
from transformers import pipeline

app = Flask(__name__)
model = pipeline("text2text-generation", model="google/flan-t5-small")

@app.route('/predict', methods=['POST'])
def predict():
    data = request.json
    prompt = data.get("prompt", "")
    response = model(prompt, max_length=200)
    return jsonify({"answer": response[0]["generated_text"]})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)