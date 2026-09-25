from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

GROQ_KEY = os.environ.get("GROQ_KEY")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

@app.route("/")
def home():
    return """
    <html><body style='font-family:sans-serif;text-align:center;padding-top:50px'>
    <h1>TiTech AI is Live!</h1>
    <p>API is running. Use /api/chat to chat.</p>
    </body></html>
    """

@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_msg = data.get("message", "")
    if not user_msg:
        return jsonify({"error":"No message"}), 400

    headers = {"Authorization": f"Bearer {GROQ_KEY}", "Content-Type":"application/json"}
    payload = {
        "model": "llama3-8b-8192",
        "messages": [{"role":"user","content":user_msg}]
    }
    r = requests.post(GROQ_URL, json=payload, headers=headers)
    result = r.json()
    reply = result["choices"][0]["message"]["content"]
    return jsonify({"reply": reply})

if __name__ == "__main__":
    app.run()
