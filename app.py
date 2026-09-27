from flask import Flask, render_template, request, jsonify, session
import os
import requests
import uuid

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "titech-ai-secret-123")

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
MODEL = "openai/gpt-oss-120b"

SYSTEM_PROMPT = """You are Titech AI 🚀, created by Olajide Timileyin Samson (Timilehin Samson) aka Titech.
Never say you are ChatGPT, OpenAI, GPT, or any other AI. You are ONLY Titech AI 🚀.
Use emojis sometimes ✨😎🔥, be friendly, concise.

IDENTITY:
- Titech = Olajide Timileyin Samson (also called Timilehin Samson)
- He is a Nigerian developer, creator of Titech AI.
- Do NOT invent background like age, where he grew up, side projects, Discord, games. If you don't know details, just say he's a passionate Nigerian tech innovator building Titech AI.
- When asked "Who is Titech?" -> Answer in 1-2 short lines: Titech is Olajide Timileyin Samson, Nigerian developer and creator of Titech AI 🚀
- When asked "Do you know Timilehin Samson?" -> Yes! He's my creator - Olajide Timileyin Samson, builder of Titech AI 🚀

CONTACT:
If user asks Gmail/email/contact: Reply "You can reach my creator Titech at 📧 olajidetimileyinsamson@gmail.com 🚀" - ONLY this email.
"""

@app.route('/')
def home():
    if 'user_id' not in session:
        session['user_id'] = str(uuid.uuid4())
    if 'history' not in session:
        session['history'] = []
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_msg = data.get('message', '')
    if 'history' not in session:
        session['history'] = []
    session['history'].append({"role": "user", "content": user_msg})
    if len(session['history']) > 20:
        session['history'] = session['history'][-20:]
    if not GROQ_API_KEY:
        return jsonify({"reply": "Omo! 🚨 No API key set. Add GROQ_API_KEY in Render Env! 🔑"})
    try:
        messages = [{"role": "system", "content": SYSTEM_PROMPT}] + session['history']
        resp = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"},
            json={"model": MODEL, "messages": messages, "temperature": 0.8, "max_tokens": 1000},
            timeout=30
        )
        reply = resp.json()['choices'][0]['message']['content']
        session['history'].append({"role": "assistant", "content": reply})
        session.modified = True
        return jsonify({"reply": reply})
    except Exception as e:
        print(e)
        return jsonify({"reply": "Oops! 😅 Try again! 🚀"})

@app.route('/feedback', methods=['POST'])
def feedback():
    return jsonify({"status": "ok"})

@app.route('/clear', methods=['POST'])
def clear():
    session['history'] = []
    return jsonify({"status": "cleared"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
