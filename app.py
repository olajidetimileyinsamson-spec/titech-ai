import os, requests, urllib.parse
from flask import Flask, request, jsonify

app = Flask(__name__)
GROQ_KEY = os.environ.get("GROQ_API_KEY","").strip()
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

HTML = """<!DOCTYPE html><html><head><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Titech AI</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap" rel="stylesheet">
<style>
*{box-sizing:border-box}body{margin:0;font-family:Inter,sans-serif;background:radial-gradient(1200px 600px at 20% -10%, #1e3aff33, transparent), radial-gradient(1000px 500px at 100% 0%, #00d5ff22, transparent), #080a0f;color:#e8eefc;display:flex;flex-direction:column;height:100vh}
header{padding:16px 20px;display:flex;align-items:center;gap:12px;border-bottom:1px solid #1a233d;background:#0b0f1bcc;backdrop-filter:blur(10px);position:sticky;top:0;z-index:10}
.logo{width:36px;height:36px;border-radius:10px;background:linear-gradient(135deg,#3b82f6,#06b6d4);display:grid;place-items:center;font-weight:800}
#chat{flex:1;overflow-y:auto;padding:24px;max-width:900px;width:100%;margin:0 auto}
.msg{margin:14px 0;padding:14px 18px;border-radius:16px;line-height:1.6;max-width:85%;animation:pop.2s ease}
.user{background:linear-gradient(135deg,#2563eb,#3b82f6);margin-left:auto;color:white;box-shadow:0 8px 20px #2563eb33}
.ai{background:#12182a;border:1px solid #1f2a4a}
#bar{max-width:900px;width:100%;margin:0 auto;padding:14px 20px 20px;display:flex;gap:10px;background:linear-gradient(to top,#080a0f,transparent)}
input{flex:1;padding:14px 16px;border-radius:14px;border:1px solid #223055;background:#10172a;color:white;outline:none}
input:focus{border-color:#3b82f6}
button{padding:14px 20px;border-radius:14px;border:none;background:#2563eb;color:white;font-weight:700;cursor:pointer}
img{max-width:100%;border-radius:12px;margin-top:10px;border:1px solid #223055}
.tag{font-size:11px;padding:4px 8px;border-radius:999px;background:#1e2a4a;color:#8db2ff;margin-left:8px}
@keyframes pop{from{transform:translateY(6px);opacity:0}to{transform:none;opacity:1}}
</style></head><body>
<header><div class="logo">T</div><div><b>Titech AI</b><br><small style="opacity:.6">by Timileyin Samson • Live Search Active</small></div><span class="tag">SMART + LIVE</span></header>
<div id="chat"><div class="msg ai">👋 I'm <b>Titech AI</b> — now with <b>live internet search</b> + image generation.<br><br>Try: "richest man 2026" or "generate image of futuristic Lagos"</div></div>
<div id="bar"><input id="inp" placeholder="Ask anything... news, 2026 data, images"><button onclick="send()">Send</button></div>
<script>
async function send(){
 let inp=document.getElementById('inp'); let t=inp.value.trim(); if(!t)return;
 let c=document.getElementById('chat'); c.innerHTML+=`<div class="msg user">${t}</div>`; inp.value=''; c.scrollTop=c.scrollHeight;
 c.innerHTML+=`<div class="msg ai" id="tmp">Searching...</div>`; c.scrollTop=c.scrollHeight;
 let r=await fetch('/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({message:t})});
 let d=await r.json(); document.getElementById('tmp')?.remove();
 let h=`<div class="msg ai">${d.reply.replace(/\\n/g,'<br>')}`;
 if(d.image){ h+=`<br><img src="${d.image}"><br><a href="${d.image}" target="_blank"><button style="margin-top:8px">Download Image</button></a>`; }
 if(d.source){ h+=`<br><br><small style="opacity:.5">🌐 Source: live search</small>`; }
 h+=`</div>`; c.innerHTML+=h; c.scrollTop=c.scrollHeight;
}
document.getElementById('inp').addEventListener('keydown',e=>{if(e.key==='Enter')send()});
</script></body></html>"""

def call_groq(model, message):
    headers = {"Authorization": "Bearer " + GROQ_KEY, "Content-Type": "application/json"}
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": "You are Titech AI by Timileyin Samson. You are very friendly, warm, playful, like a helpful Naija bestie. You explain simply but smart. Always be kind."},
            {"role": "user", "content": message}
        ]
    }
    r = requests.post(GROQ_URL, headers=headers, json=payload, timeout=50)
    if r.status_code!= 200:
        return f"Groq {r.status_code}: {r.text[:400]}", False
    return r.json()["choices"][0]["message"]["content"], True

def ask_smart(msg):
    low = msg.lower()
    needs_live = any(x in low for x in ["2026","2025","today","latest","current","now","price","news","richest","who is","forbes","president","score"])
    if needs_live:
        # compound does live web search
        content, ok = call_groq("groq/compound-mini", msg)
        if ok:
            return content, True
    # fallback to super smart reasoning
    content, _ = call_groq("openai/gpt-oss-120b", msg)
    return content, False

@app.route("/")
def home():
    return HTML

@app.route("/chat", methods=["POST"])
def chat_route():
    m = request.get_json().get("message","")
    low = m.lower()
    if "generate image" in low or "picture of" in low or "image of" in low:
        prompt = low.replace("generate image of","").replace("generate image","").replace("picture of","").replace("image of","").strip() or "futuristic Lagos city"
        url = "https://image.pollinations.ai/prompt/" + urllib.parse.quote(prompt) + "?nologo=true&enhance=true&seed=" + os.urandom(2).hex()
        return jsonify({"reply": f"Here is your image for **{prompt}**:", "image": url})
    ans, is_live = ask_smart(m)
    return jsonify({"reply": ans, "source": is_live})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT",10000)))
