from flask import Blueprint, request, jsonify
from services import parser, openrouter_api
from utils.chunker import chunk_text
import time

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

        # Handle YouTube transcripts
        elif input_type == "youtube":
            url = request.form.get("url", "")
            text = parser.extract_text_from_youtube(url)
            if text.startswith("ERROR"):
                return jsonify({"error": text}), 400

        else:
            return jsonify({"error": "Invalid input type"}), 400

        # --- 🔑 Apply chunking before summarization ---
        chunks = chunk_text(text, max_chars=3000)
        summaries = [openrouter_api.summarize(c) for c in chunks]

        # Merge summaries into one response
        combined_summary = " ".join([s["summary"] for s in summaries if "summary" in s])
        combined_bullets = []
        for s in summaries:
            combined_bullets.extend(s.get("bullets", []))

        # Include docId + raw text in response
        response = {
            "docId": "doc-" + str(int(time.time())),
            "summary": combined_summary,
            "bullets": combined_bullets[:10],  # keep top 10 bullets
            "text": text   # send extracted full text so frontend can use it in chat
        }

        return jsonify(response)

    except Exception as e:
        return jsonify({"error": str(e)}), 500
