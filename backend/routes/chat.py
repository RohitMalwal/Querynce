from flask import Blueprint, request, jsonify
from services import openrouter_api
from utils.chunker import chunk_text

chat_bp = Blueprint("chat", __name__)

@chat_bp.route("/api/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid request, expected JSON"}), 400

        question = data.get("question", "").strip()
        text = data.get("text", "").strip()   # frontend should send doc text OR cache it
        if not question:
            return jsonify({"error": "No question provided"}), 400
        if not text:
            return jsonify({"error": "No document text provided"}), 400

        # --- 🔑 Split text into chunks ---
        chunks = chunk_text(text, max_chars=3000)

        answers = []
        for c in chunks:
            user_prompt = f"Document chunk:\n{c}\n\nQuestion: {question}"
            ans = openrouter_api.chat(user_prompt)
            answers.append(ans)

        # --- 🔑 Merge answers ---
        if len(answers) == 1:
            final_answer = answers[0]
        else:
            # Optionally, ask the model to consolidate multiple chunk-answers
            merge_prompt = (
                "You are given answers from different chunks of a document.\n"
                "Combine them into one coherent and concise answer:\n\n"
                + "\n\n".join(answers)
            )
            final_answer = openrouter_api.chat(merge_prompt)

        return jsonify({"answer": final_answer})

    except Exception as e:
        return jsonify({"error": f"Chat processing failed: {str(e)}"}), 500
