from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

GROQ_KEY = os.environ.get("GROQ_KEY")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
<title>TiTech AI</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
body{font-family:system-ui;background:#0f0f0f;color:white;margin:0;display:flex;flex-direction:column;height:100vh}
.header{padding:16px;text-align:center;background:#1a1a1a;font-weight:bold;font-size:20px;border-bottom:1px solid #333}
#chat{flex:1;overflow-y:auto;padding:20px;display:flex;flex-direction:column;gap:14px}
.msg{max-width:85%;padding:12px 16px;border-radius:18px;line-height:1.5;font-size:15px}
.user{align-self:flex-end;background:#4f46e5}
.bot{align-self:flex-start;background:#222;border:1px solid #333}
.input-area{padding:14px;background:#1a1a1a;display:flex;gap:10px}
input{flex:1;padding:13px 16px;border-radius:25px;border:1px solid #333;background:#2a2a2a;color:white;outline:none}
button{padding:12px 22px;border-radius:25px;border:none;background:#4f46e5;color:white;font-weight:bold}
</style>
</head>
<body>
<div class="header">TiTech AI 🚀 - Live!</div>
<div id="chat"><div class="msg bot">Hello Timileyin! I'm TiTech AI, built by you. How can I help today?</div></div>
<div class="input-area">
<input id="msg" placeholder="Ask TiTech anything..." onkeypress="if(event.key==='Enter')send()" />
<button onclick="send()">Send</button>
</div>
<script>
async function send(){
 let i=document.getElementById('msg'); let t=i.value.trim(); if(!t)return;
 let c=document.getElementById('chat'); c.innerHTML+=`<div class="msg user">${t}</div>`; i.value='';
 let d=document.createElement('div'); d.className='msg bot'; d.textContent='Thinking...'; c.appendChild(d);
 c.scrollTop=c.scrollHeight;
 try{
  let r=await fetch('/api/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({message:t})});
  let j=await r.json(); d.textContent=j.reply || j.response || 'Done';
 }catch(e){ d.textContent='Error connecting to AI'; }
 c.scrollTop=c.scrollHeight;
}
</script>
</body>
</html>
"""

@app.route('/')
def home():
    return HTML_PAGE

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        user_msg = data.get('message', '')

        headers = {
            "Authorization": f"Bearer {GROQ_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "llama-3.1-8b-instant",
            "messages": [{"role": "user", "content": user_msg}]
        }

        res = requests.post(GROQ_URL, json=payload, headers=headers)
        result = res.json()
        reply = result['choices'][0]['message']['content']

        return jsonify({"reply": reply})
    except Exception as e:
        return jsonify({"reply": f"Error: {str(e)}"})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
