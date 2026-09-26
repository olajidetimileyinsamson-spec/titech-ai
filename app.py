import os
import requests
from flask import Flask, request, jsonify, render_template_string
import urllib.parse

app = Flask(__name__)

# --- GET KEY ---
GROQ_KEY = os.environ.get("GROQ_API_KEY", "").strip()
print(f"DEBUG KEY CHECK: Found key? {bool(GROQ_KEY)} Length: {len(GROQ_KEY)} Starts with: {GROQ_KEY[:8] if GROQ_KEY else 'NONE'}")

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

def ask_groq(message):
    if not GROQ_KEY or not GROQ_KEY.startswith("gsk_"):
        return "❌ ERROR: GROQ_API_KEY missing on Render. Go to Render -> Environment -> check key name is GROQ_API_KEY and value starts with gsk_. Then Save + Manual Deploy."

    headers = {"Authorization": f"Bearer {GROQ_KEY}", "Content-Type": "application/json"}
    data = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": "You are Titech AI, created by Timileyin Samson. Friendly, smart, explain well. Support Yoruba, English, Pidgin."},
            {"role": "user", "content": message}
        ],
        "temperature": 0.7
    }
    try:
        r = requests.post(GROQ_URL, headers=headers, json=data, timeout=30)
        print(f"GROQ Status: {r.status_code} Body: {r.text[:200]}")
        if r.status_code!= 200:
            return f"Groq API Error {r.status_code}: {r.text[:200]} - Check your key is valid at console.groq.com"
        return r.json()["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"Exception: {e}")
        return f"Connection error: {str(e)}"

@app.route("/")
def index():
    # your HTML here - keep your current index.html content
    return render_template_string(open("templates/index.html").read() if os.path.exists("templates/index.html") else "<h1>Titech AI</h1>")

@app.route("/chat", methods=["POST"])
def chat():
    user_msg = request.json.get("message", "")
    if "generate image of" in user_msg.lower() or "a picture of" in user_msg.lower():
        prompt = user_msg.lower().replace("generate image of","").replace("a picture of","").strip()
        encoded = urllib.parse.quote(prompt)
        url = f"https://image.pollinations.ai/prompt/{encoded}"
        return jsonify({"reply": f"Here you go! **{prompt}**:", "image": url})

    reply = ask_groq(user_msg)
    return jsonify({"reply": reply})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
