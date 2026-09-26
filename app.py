import os, requests, urllib.parse
from flask import Flask, request, jsonify

app = Flask(__name__)
GROQ_KEY = os.environ.get("GROQ_API_KEY","").strip()
URL = "https://api.groq.com/openai/v1/chat/completions"

# FULL DESIGN + LOGO BACK
HTML = """
<html><head><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Titech AI</title>
<style>
*{box-sizing:border-box}
body{margin:0;background:#070a12;color:#e8eaff;font-family:Inter,system-ui,sans-serif;display:flex;flex-direction:column;height:100vh}
header{padding:14px 18px;display:flex;align-items:center;gap:12px;background:#0d1120;border-bottom:1px solid #1c2340;position:sticky;top:0}
.logo{width:38px;height:38px;border-radius:10px;background:linear-gradient(135deg,#4f46e5,#06b6d4);display:flex;align-items:center;justify-content:center;font-weight:900;color:white}
.brand{font-weight:800;letter-spacing:0.5px}
.brand span{color:#60a5fa}
#chat{flex:1;overflow:auto;padding:18px;max-width:950px;margin:0 auto;width:100%}
.msg{margin:14px 0;padding:14px 16px;border-radius:16px;max-width:86%;line-height:1.5;white-space:pre-wrap}
.user{background:#2563eb;margin-left:auto;border-bottom-right-radius:6px}
.ai{background:#11172c;border:1px solid #1e294d;border-bottom-left-radius:6px}
#bar{display:flex;gap:10px;padding:14px;max-width:950px;margin:0 auto;width:100%;background:#0d1120;border-top:1px solid #1c2340}
input{flex:1;padding:14px 16px;border-radius:12px;border:1px solid #2a365f;background:#0f172a;color:#fff;outline:none}
button{padding:14px 20px;border-radius:12px;border:none;background:#2563eb;color:#fff;font-weight:700}
img.gen{max-width:100%;border-radius:12px;margin-top:10px;border:1px solid #2a365f}
</style></head><body>
<header><div class="logo">T</div><div class="brand">TITECH <span>AI</span></div></header>
<div id="chat"><div class="msg ai">👋 Hey! I'm <b>Titech AI</b> by Timileyin Samson — Live search ON, Image HD, No watermark. How can I help?</div></div>
<div id="bar"><input id="inp" placeholder="Ask anything..."><button onclick="send()">Send</button></div>
<script>
async function send(){
 let i=document.getElementById('inp');let t=i.value.trim();if(!t)return;
 let c=document.getElementById('chat');
 c.innerHTML+=`<div class=msg user>${t}</div>`;i.value='';
 c.innerHTML+=`<div class=msg ai id=tmp>Thinking...</div>`;
 let r=await fetch('/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({message:t})});
 let d=await r.json();document.getElementById('tmp').remove();
 c.innerHTML+=`<div class=msg ai>${d.reply}${d.image?`<br><img class=gen src=${d.image}>`:''}</div>`;
 c.scrollTop=c.scrollHeight;
}
document.getElementById('inp').addEventListener('keydown',e=>{if(e.key==='Enter')send()});
</script></body></html>
"""

def ask_groq(msg):
    h={"Authorization":"Bearer "+GROQ_KEY,"Content-Type":"application/json"}
    p={
      "model":"openai/gpt-oss-120b",
      "messages":[
        {"role":"system","content":"You are Titech AI built by Timileyin Samson. Be friendly Naija bestie. Keep answers SHORT 4-5 sentences unless user asks for long detail. Use current knowledge. No long boring essay."},
        {"role":"user","content":msg}
      ]
    }
    r=requests.post(URL,headers=h,json=p,timeout=60)
    if r.status_code!=200:
        return f"Groq error {r.status_code}: {r.text[:250]}"
    return r.json()["choices"][0]["message"]["content"]

@app.route("/")
def home():
    return HTML

@app.route("/chat", methods=["POST"])
def chat():
    data=request.get_json()
    m=data.get("message","").strip()
    low=m.lower()
    if "image" in low or "aeroplane" in low or "airplane" in low or "benz" in low or "car" in low:
        pr=low.replace("generate image of","").replace("generate an image of","").replace("image of","").replace("a realistic image of","").strip()
        if not pr: pr="futuristic"
        q=urllib.parse.quote(pr+" photorealistic, 4k, sharp, correct proportions, no distortion, no watermark, no logo, no text")
        img_url=f"https://image.pollinations.ai/prompt/{q}?model=flux&nologo=true&nofeed=true&enhance=true&seed={os.urandom(2).hex()}"
        return jsonify({"reply":f"Here is HD image for: {pr}","image":img_url})
    reply=ask_groq(m)
    return jsonify({"reply":reply})

if __name__=="__main__":
    app.run(host="0.0.0.0",port=int(os.environ.get("PORT",10000)))
