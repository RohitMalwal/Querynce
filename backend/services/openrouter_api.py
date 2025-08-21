import os, json, requests
from dotenv import load_dotenv

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_REFERRER = os.getenv("OPENROUTER_REFERRER", "")
OPENROUTER_SITE = os.getenv("OPENROUTER_SITE", "Querynce")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

def _post(messages, model="deepseek/deepseek-r1-0528:free", max_tokens=1024, temperature=0.3):
    if not OPENROUTER_API_KEY:
        raise RuntimeError("Missing OPENROUTER_API_KEY in environment")

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }
    # Optional attribution headers
    if OPENROUTER_REFERRER:
        headers["HTTP-Referer"] = OPENROUTER_REFERRER
    if OPENROUTER_SITE:
        headers["X-Title"] = OPENROUTER_SITE

    payload = {
        "model": model,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": temperature,
    }

    r = requests.post(OPENROUTER_URL, headers=headers, data=json.dumps(payload), timeout=60)
    try:
        r.raise_for_status()
    except requests.HTTPError as e:
        # Surface full error for debugging
        raise RuntimeError(f"OpenRouter error {r.status_code}: {r.text}") from e
    data = r.json()
    return data["choices"][0]["message"]["content"]

def chat(user_content, model="deepseek/deepseek-r1-0528:free"):
    messages = [
        {"role": "system", "content": "You are an AI research assistant."},
        {"role": "user", "content": user_content},
    ]
    return _post(messages, model=model)

def summarize(text, model="deepseek/deepseek-r1-0528:free"):
    """
    Returns dict: { "summary": str, "bullets": [str, ...] }
    """
    messages = [
        {"role": "system", "content": "You are a concise assistant for summarizing documents."},
        {"role": "user", "content": (
            "Summarize the document below. Respond ONLY as strict JSON:\n"
            '{ "summary": "<3-4 sentence brief>", "bullets": ["point1","point2","point3","point4","point5"] }\n\n'
            f"Document:\n{text}"
        )},
    ]
    raw = _post(messages, model=model)
    # Best-effort JSON parse (model might wrap in code fences)
    raw_str = raw.strip()
    if raw_str.startswith("```"):
        raw_str = raw_str.strip("`").split("\n", 1)[1]
    try:
        obj = json.loads(raw_str)
        # minimal validation
        if "summary" in obj and "bullets" in obj and isinstance(obj["bullets"], list):
            return obj
    except Exception:
        pass
    # Fallback if JSON parsing fails
    return {"summary": raw, "bullets": []}

if __name__ == "__main__":
    print(chat("Say hi in one short line."))