from flask import Flask, request, jsonify
from flask_cors import CORS
from services.openrouter_api import chat, summarize

app = Flask(__name__)
CORS(app)

@app.get("/")
def home():
    return {"status": "Backend is running with OpenRouter!"}

@app.post("/api/chat")
def chat_route():
    data = request.get_json(force=True)
    question = data.get("question", "")
    if not question:
        return jsonify({"error": "question is required"}), 400
    try:
        answer = chat(question)  # uses OpenRouter
        return jsonify({"answer": answer})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.post("/api/ingest")
def ingest_route():
    """
    For now, this accepts raw 'text' in JSON just to prove the flow.
    Later you'll replace with PDF/URL parsing and pass extracted text here.
    """
    data = request.get_json(force=True)
    text = data.get("text", "")
    if not text:
        return jsonify({"error": "text is required"}), 400
    try:
        result = summarize(text)
        # Return a fake docId for now; later store/reuse it
        return jsonify({"docId": "demo-1", **result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
