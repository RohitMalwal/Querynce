from flask import Blueprint, request, jsonify
from services import parser, openrouter_api

ingest_bp = Blueprint("ingest", __name__)

@ingest_bp.route("/api/ingest", methods=["POST"])
def ingest():
    try:
        input_type = request.form.get("type")  # pdf, url, text, youtube

        # Handle PDF upload
        if input_type == "pdf":
            if "file" not in request.files:
                return jsonify({"error": "No file uploaded"}), 400
            file = request.files["file"]
            text = parser.extract_text_from_pdf(file.stream)

        # Handle URL input
        elif input_type == "url":
            url = request.form.get("url")
            if not url:
                return jsonify({"error": "No URL provided"}), 400
            text = parser.extract_text_from_url(url)

        # Handle plain text input
        elif input_type == "text":
            text = request.form.get("text", "")
            if not text:
                return jsonify({"error": "No text provided"}), 400

        elif input_type == "youtube":
            url = request.form.get("url", "")
            text = parser.extract_text_from_youtube(url)
            if text.startswith("ERROR"):
                return jsonify({"error": text}), 400
            summary = openrouter_api.summarize(text)
            return jsonify(summary)

        else:
            return jsonify({"error": "Invalid input type"}), 400

        # Pass extracted text to OpenRouter summarizer
        summary = openrouter_api.summarize(text)
        return jsonify(summary)

    except Exception as e:
        return jsonify({"error": str(e)}), 500
