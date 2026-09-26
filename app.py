import os, requests, urllib.parse
from flask import Flask, request, jsonify, send_from_directory, Response
app = Flask(__name__)
GROQ_KEY=os.environ.get("GROQ_API_KEY","").strip()
UNSPLASH_KEY=os.environ.get("UNSPLASH_KEY","").strip()
URL="https://api.groq.com/openai/v1/chat/completions"

def get_wiki(q):
    low=q.lower()
    if "nigeria" in low and "coat" in low:
        return "https://upload.wikimedia.org/wikipedia/commons/thumb/0/05/Coat_of_arms_of_Nigeria.svg/800px-Coat_of_arms_of_Nigeria.svg.png"
    if "nigeria" in low and "flag" in low:
        return "https://upload.wikimedia.org/wikipedia/commons/thumb/7/79/Flag_of_Nigeria.svg/800px-Flag_of_Nigeria.svg.png"
    try:
        s=requests.get(f"https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch={urllib.parse.quote(q)}&format=json&srlimit=1",timeout=8,headers={"User-Agent":"TitechAI"}).json()
        if not s["query"]["search"]: return None
        title=s["query"]["search"][0]["title"]
        p=requests.get(f"https://en.wikipedia.org/w/api.php?action=query&titles={urllib.parse.quote(title)}&prop=pageimages&format=json&pithumbsize=800",timeout=8,headers={"User-Agent":"TitechAI"}).json()
        for v in p["query"]["pages"].values():
            if "thumbnail" in v: return v["thumbnail"]["source"]
    except: pass
    return None

def get_unsplash(q):
    if not UNSPLASH_KEY: return None
    try:
        r=requests.get(f"https://api.unsplash.com/search/photos?query={urllib.parse.quote(q)}&per_page=1",headers={"Authorization":f"Client-ID {UNSPLASH_KEY}"},timeout=8).json()
        if r.get("results"): return r["results"][0]["urls"]["regular"]
    except: pass
    return None

@app.route("/logo.png")
def logo_file():
    return send_from_directory(".", "logo.png")

# NEW - This fixes broken images
@app.route("/proxy")
def proxy():
    img_url = request.args.get("url","")
    if not img_url: return "no url", 400
    try:
        r = requests.get(img_url, headers={"User-Agent":"Mozilla/5.0"}, timeout=10)
        return Response(r.content, content_type=r.headers.get("Content-Type","image/png"))
    except:
        return "error", 500

@app.route("/")
def home():
    return """<html><head><meta name=viewport content='width=device-width,initial-scale=1'><title>Titech AI</title></head><body style='margin:0;background:#070a14;color:#fff;font-family:system-ui;display:flex;flex-direction:column;height:100vh'>
<div style='padding:12px 16px;background:#0d1120;border-bottom:1px solid #1e294d;display:flex;align-items:center;gap:12px;font-weight:800;font-size:18px'>
<img src='/logo.png' style='width:38px;height:38px;border-radius:10px;object-fit:cover' onerror="this.style.display='none'">
TITECH AI
</div>
<div id=chat style='flex:1;overflow:auto;padding:16px;display:flex;flex-direction:column;gap:12px;padding-bottom:120px'></div>
<div style='position:fixed;bottom:0;left:0;right:0;padding:12px;background:#070a14'><div style='display:flex;gap:8px;background:#121a33;border:1px solid #2a365f;border-radius:28px;padding:6px 6px 6px 16px'><input id=inp placeholder='Ask Titech AI...' style='flex:1;background:transparent;border:none;color:#fff;outline:none'><button onclick=send() style='background:#2563eb;border:none;color:#fff;border-radius:20px;padding:10px 18px;font-weight:700'>Send</button></div></div>
<script>let c=document.getElementById('chat');async function send(){let i=document.getElementById('inp'),t=i.value.trim();if(!t)return;c.innerHTML+=`<div style='align-self:flex-end;background:#2563eb;padding:12px 16px;border-radius:18px;max-width:80%'>${t}</div>`;i.value='';c.innerHTML+=`<div id=tmp style='align-self:flex-start;background:#161f3a;padding:12px;border-radius:18px'>Searching...</div>`;c.scrollTop=c.scrollHeight;let r=await fetch('/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({message:t})});let d=await r.json();document.getElementById('tmp')?.remove();let imgHtml=d.image?`<div style='margin-top:10px;border-radius:12px;overflow:hidden;background:#fff'><img src="/proxy?url=${encodeURIComponent(d.image)}" style='width:100%;max-height:500px;object-fit:contain;display:block;background:#fff'></div>`:'';c.innerHTML+=`<div style='align-self:flex-start;background:#161f3a;border:1px solid #243157;padding:12px;border-radius:18px;max-width:85%'>${d.reply}${imgHtml}</div>`;c.scrollTop=c.scrollHeight}document.getElementById('inp').addEventListener('keydown',e=>{if(e.key==='Enter')send()});c.innerHTML+=`<div style='align-self:flex-start;background:#161f3a;padding:12px;border-radius:18px'>Welcome to Titech AI! 🚀 Try Nigeria coat of arms</div>`;</script></body></html>"""

@app.route("/chat",methods=["POST"])
def chat():
    m=request.get_json().get("message","")
    low=m.lower()
    clean=low.replace("generate","").replace("a image of","").replace("image of","").replace("picture of","").replace("photo of","").strip()
    if any(w in low for w in ["image","picture","photo","flag","coat","lion","iphone","stadium","hilux","benz"]):
        url=get_wiki(clean) or get_unsplash(clean)
        if url: return jsonify({"reply":f"✅ Real image: {clean.title()}","image":url})
        return jsonify({"reply":f"No real image for {clean}."})
    try:
        h={"Authorization":f"Bearer {GROQ_KEY}","Content-Type":"application/json"}
        d={"model":"openai/gpt-oss-120b","messages":[{"role":"system","content":"You are TITECH AI, created by Timileyin Samson. You are NOT ChatGPT."},{"role":"user","content":m}]}
        r=requests.post(URL,headers=h,json=d,timeout=20).json()
        return jsonify({"reply":r["choices"][0]["message"]["content"]})
    except: return jsonify({"reply":"I am Titech AI!"})

if __name__=="__main__": app.run(host="0.0.0.0",port=int(os.environ.get("PORT",10000)))
