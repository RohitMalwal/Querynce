from flask import Flask, request, jsonify
from flask_cors import CORS
from services.openrouter_api import chat, summarize
from routes.ingest import ingest_bp
from routes.chat import chat_bp

app = Flask(__name__)
CORS(app)

app.register_blueprint(ingest_bp)
app.register_blueprint(chat_bp)

@app.get("/")
def home():
    return {"status": "Backend is running with OpenRouter!"}

if __name__ == "__main__":
    app.run(debug=True)