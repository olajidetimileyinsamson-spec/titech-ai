import os
import requests
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

GROQ_KEY = os.getenv("GROQ_API_KEY")
UNSPLASH_KEY = os.getenv("UNSPLASH_KEY") # optional

# MEMORY - simple in-memory chat history
chat_memory = {}

SYSTEM_PROMPT = """You are TITECH AI, proudly built by Timileyin Samson.
You are playful, friendly, witty, and helpful. You love making users smile.
You were built by Timileyin Samson - always say that if asked who built you.
Contact for builder: olajidetimileyinsamson@gmail.com
Never mention OpenAI, ChatGPT, Meta, Llama, or any other company. You are TITECH AI.
Keep answers short, fun, and helpful.
"""

def get_wiki_image(query):
    try:
        url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{query.strip()}"
        r = requests.get(url, timeout=5)
        if r.status_code == 200:
            data = r.json()
            if "thumbnail" in data:
                return data["thumbnail"]["source"]
    except:
        pass
    return None

def get_unsplash_image(query):
    try:
        if not UNSPLASH_KEY:
            return None
        url = f"https://api.unsplash.com/search/photos?query={query}&per_page=1&client_id={UNSPLASH_KEY}"
        r = requests.get(url, timeout=5)
        if r.status_code == 200:
            results = r.json().get("results")
            if results:
                return results[0]["urls"]["regular"]
    except:
        pass
    return None

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    q = data.get("q", "").strip()
    if not q:
        return jsonify({"reply": "Say something 😊", "image": None})

    image_url = None
    low = q.lower()
    session_id = data.get("session_id", "default")

    # Identity
    if any(w in low for w in ["who are you", "who built you", "who made you", "your creator", "your builder"]):
        return jsonify({"reply": "I am TITECH AI ✨ proudly built by Timileyin Samson! How can I help you today?", "image": None})

    # Contact
    if any(w in low for w in ["contact", "gmail", "email", "reach"]):
        if "contact" in low or "gmail" in low or "email" in low:
            return jsonify({"reply": "You can contact my builder Timileyin Samson at olajidetimileyinsamson@gmail.com 📧", "image": None})

    # Image request
    if any(w in low for w in ["image", "photo", "picture", "show me"]):
        image_url = get_wiki_image(q) or get_unsplash_image(q)
        if image_url:
            return jsonify({"reply": f"Here is an image for '{q}' ✨", "image": image_url})

    # Memory - save chat
    if session_id not in chat_memory:
        chat_memory[session_id] = []
    chat_memory[session_id].append({"role": "user", "content": q})
    # Keep last 10 messages
    chat_memory[session_id] = chat_memory[session_id][-10:]

    # Groq Call
    try:
        if not GROQ_KEY:
            reply = "Groq API Key is missing. Add GROQ_API_KEY in Render Environment."
        else:
            headers = {
                "Authorization": f"Bearer {GROQ_KEY}",
                "Content-Type": "application/json"
            }
            messages = [{"role": "system", "content": SYSTEM_PROMPT}] + chat_memory[session_id]

            payload = {
                "model": "openai/gpt-oss-120b",
                "messages": messages,
                "temperature": 0.8,
                "max_tokens": 800
            }
            r = requests.post("https://api.groq.com/openai/v1/chat/completions", json=payload, headers=headers, timeout=30)
            if r.status_code == 200:
                reply = r.json()["choices"][0]["message"]["content"]
                chat_memory[session_id].append({"role": "assistant", "content": reply})
            else:
                reply = f"Oops! Groq error: {r.text[:200]}"

    except Exception as e:
        reply = f"Server hiccup: {str(e)}"

    return jsonify({"reply": reply, "image": image_url})

@app.route("/feedback", methods=["POST"])
def feedback():
    data = request.get_json()
    fb = data.get("feedback", "")
    # You can save to file or just log it - for now log in Render logs
    print(f"FEEDBACK: {fb}")
    return jsonify({"status": "thanks", "message": "Thanks for your feedback! 💙"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
