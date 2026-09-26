import os, requests, urllib.parse
from flask import Flask, request, jsonify

app = Flask(__name__)
GROQ_KEY = os.environ.get("GROQ_API_KEY","").strip()
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

HTML = """<!DOCTYPE html><html><head><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Titech AI</title><style>
body{background:#0a0a0a;color:white;font-family:sans-serif;margin:0;display:flex;flex-direction:column;height:100vh}
#chat{flex:1;overflow-y:auto;padding:20px}.msg{margin:10px 0;padding:12px 16px;border-radius:12px;max-width:85%}
.user{background:#2563eb;margin-left:auto}.ai{background:#1f1f1f}
#bar{display:flex;padding:12px;background:#111;gap:8px}
input{flex:1;padding:12px;border-radius:8px;border:none;background:#222;color:white}
button{padding:12px 20px;border-radius:8px;border:none;background:#2563eb;color:white;font-weight:bold}
img{max-width:100%;border-radius:10px;margin-top:8px}</style></head><body>
<div id="chat"><div class="msg ai">I'm Titech AI by Timileyin Samson. Ask me anything or say "generate image of..."</div></div>
<div id="bar"><input id="inp" placeholder="Ask Titech AI..."><button onclick="send()">Send</button></div>
<script>
async function send(){
 let inp=document.getElementById('inp'); let txt=inp.value.trim(); if(!txt)return;
 let chat=document.getElementById('chat');
 chat.innerHTML+=`<div class="msg user">${txt}</div>`; inp.value=''; chat.scrollTop=chat.scrollHeight;
 let r=await fetch('/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({message:txt})});
 let d=await r.json();
 let html=`<div class="msg ai">${d.reply.replace(/\\n/g,'<br>')}`;
 if(d.image){ html+=`<br><img src="${d.image}"><br><a href="${d.download_url||d.image}" target="_blank"><button>Download</button></a>`; }
 html+=`</div>`; chat.innerHTML+=html; chat.scrollTop=chat.scrollHeight;
}
document.getElementById('inp').addEventListener('keydown',e=>{if(e.key==='Enter')send()});
</script></body></html>"""

def ask_groq(msg):
    if not GROQ_KEY:
        return "GROQ_API_KEY missing on Render."
    headers = {"Authorization": f"Bearer {GROQ_KEY}", "Content-Type": "application/json"}
    payload = {
        "model": "llama-3.1-8b-instant",
        "messages": [
            {"role": "system", "content": "You are Titech AI by Timileyin Samson. Helpful, concise."},
            {"role": "user", "content": msg}
        ]
    }
    try:
        r = requests.post(GROQ_URL, headers=headers, json=payload, timeout=40)
        if r.status_code!= 200:
            return f"Groq {r.status_code}: {r.text[:200]}"
        return r.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return f"Error: {e}"

@app.route("/")
def home():
    return HTML

@app.route("/chat", methods=["POST"])
def chat():
    m = request.get_json().get("message","")
    low = m.lower()
    if "generate image" in low or "picture of" in low:
        prompt = low.replace("generate image of","").replace("generate image","").replace("a picture of","").replace("picture of","").strip() or "futuristic"
        url = f"https://image.pollinations.ai/prompt/{urllib.parse.quote(prompt)}?nologo=true&seed={os.urandom(2).hex()}"
        return jsonify({"reply": f"Here is your image for {prompt}:", "image": url, "download_url": url})
    return jsonify({"reply": ask_groq(m)})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT",10000)))
