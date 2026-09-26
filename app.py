import os, requests, urllib.parse
from flask import Flask, request, jsonify
app = Flask(__name__)
GROQ_KEY = os.environ.get("GROQ_API_KEY","").strip()
URL = "https://api.groq.com/openai/v1/chat/completions"

HTML = """<html><head><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Titech AI</title><style>
body{background:#080a0f;color:#fff;font-family:sans-serif;margin:0;display:flex;flex-direction:column;height:100vh}
#chat{flex:1;overflow:auto;padding:20px;max-width:900px;margin:0 auto;width:100%}
.msg{margin:12px 0;padding:12px 16px;border-radius:12px;max-width:85%}
.user{background:#2563eb;margin-left:auto}.ai{background:#12182a}
#bar{display:flex;gap:8px;padding:12px;max-width:900px;margin:0 auto;width:100%}
input{flex:1;padding:12px;border-radius:10px;border:none;background:#222;color:#fff}
button{padding:12px 16px;border-radius:10px;border:none;background:#2563eb;color:#fff}
</style></head><body>
<div id="chat"><div class="msg ai">Titech AI - Live Search ON</div></div>
<div id="bar"><input id="inp" placeholder="Ask..."><button onclick="send()">Send</button></div>
<script>
async function send(){
 let i=document.getElementById('inp');let t=i.value.trim();if(!t)return;
 let c=document.getElementById('chat');c.innerHTML+=`<div class=msg user>${t}</div>`;i.value='';
 c.innerHTML+=`<div class=msg ai id=tmp>...</div>`;
 let r=await fetch('/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({message:t})});
 let d=await r.json();document.getElementById('tmp').remove();
 c.innerHTML+=`<div class=msg ai>${d.reply}<br>${d.image?`<img src=${d.image} style=max-width:100%>` :''}</div>`;
 c.scrollTop=c.scrollHeight;
}
</script></body></html>"""

def ask(model, msg):
  h={"Authorization":"Bearer "+GROQ_KEY,"Content-Type":"application/json"}
  p={"model":model,"messages":[{"role":"system","content":"You are Titech AI by Timileyin Samson. Friendly Naija bestie. Keep replies SHORT 4-5 sentences unless user asks detail."},{"role":"user","content":msg}]}
  r=requests.post(URL,headers=h,json=p,timeout=50)
  if r.status_code!=200:
    return f"Error {r.status_code}: {r.text[:200]}"
  return r.json()["choices"][0]["message"]["content"]

@app.route("/")
def home(): return HTML

@app.route("/chat", methods=["POST"])
def chat():
  m=request.get_json().get("message","")
  low=m.lower()
  if "image" in low:
    pr=low.replace("generate image of","").replace("image of","").strip() or "futuristic"
    u="https://image.pollinations.ai/prompt/"+urllib.parse.quote(pr)+"?seed="+os.urandom(2).hex()
    return jsonify({"reply":"Image for "+pr,"image":u})
  need=any(x in low for x in ["2026","2025","today","latest","current","price","richest","news"])
  mod="groq/compound-mini" if need else "openai/gpt-oss-120b"
  return jsonify({"reply":ask(mod,m)})

if __name__=="__main__":
  app.run(host="0.0.0.0",port=int(os.environ.get("PORT",10000)))
