from flask import Flask, request, jsonify, render_template_string, send_file
import os, requests

app = Flask(__name__)
GROQ_KEY = os.environ.get("GROQ_API_KEY")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

def get_ai_reply(message, username="Friend"):
    # System identity
    system_prompt = f"You are Titech AI 🚀, a super helpful Nigerian AI assistant developed by Timileyin Samson, founder of Titech AI. You help Nigerians build future with AI. Be friendly, concise, use small pidgin sometimes. User's name is {username}. Always mention you were built by Timileyin Samson if asked who developed you."

    # If Groq key exists, use REAL AI brain
    if GROQ_KEY:
        try:
            payload = {
                "model": "llama-3.1-8b-instant",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": message}
                ],
                "temperature": 0.7,
                "max_tokens": 500
            }
            headers = {"Authorization": f"Bearer {GROQ_KEY}", "Content-Type": "application/json"}
            r = requests.post(GROQ_URL, json=payload, headers=headers, timeout=15)
            data = r.json()
            if "choices" in data:
                return data["choices"][0]["message"]["content"]
        except Exception as e:
            print(f"Groq error: {e}")

    # Fallback (if no key or error)
    msg = message.lower()
    if "develop" in msg or "creator" in msg or "built" in msg or "owner" in msg:
        return "I was developed by Timiley
