import os, requests, urllib.parse
from flask import Flask, request, jsonify, send_from_directory

app = Flask(__name__)
GROQ_KEY = os.environ.get("GROQ_API_KEY","").strip()
URL = "https://api.groq.com/openai/v1/chat/completions"

def get_wiki_image(query):
    try:
        # 1. Search Wikipedia
        s_url = f"https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch={urllib.parse.quote(query)}&format=json&srlimit=1"
        r = requests.get(s_url, timeout=10, headers={"User-Agent":"TitechAI/1.0"}).json()
        if not r.get("query",{}).get("search"): return None
        title = r["query"]["search"][0]["title"]
        # 2. Get real image
        p_url = f"https://en.wikipedia.org/w/api.php?action=query&titles={urllib.parse.quote(title)}&prop=pageimages&format=json&pithumbsize=800"
        r2 = requests.get(p_url, timeout=10, headers={"User-Agent":"TitechAI/1.0"}).json()
        pages = r2.get("query",{}).get("pages",{})
        for pid in pages:
            thumb = pages[pid].get("thumbnail",{}).get("source")
            if thumb: return thumb, title
    except: pass
    return None

HTML = """
<html><head><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Titech AI</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap" rel="stylesheet">
<style>
*{box-sizing:border-box;font-family:Inter,system-ui}
body{margin:0;background:#070a14;color:#e8eaff;display:flex;flex-direction:column;height:100vh}
header{padding:12px 16px;display:flex;align-items:center;gap:12px;background:#0d1120;border-bottom:1px solid #1e294d;position:sticky;top:0;z-index:10}
.logo{width:42px;height:42px;border-radius:12px;background:linear-gradient(135deg,#4f46e5,#06b6d4);display:flex;align-items:center;justify-content:center;font-weight:900;color:white;overflow:hidden}
.logo img{width:100%;height:100%;object-fit:cover}
.brand{font-weight:800;font-size:18px}.brand span{color:#60a5fa}
#chat{flex:1;overflow:auto;padding:16px 16px 120px 16px;max-width:900px;margin:0 auto;width:100%;display:flex;flex-direction:column;gap:12px}
.msg{padding:14px 18px;border-radius:20px;max-width:82%;line-height:1.5;font-size:15px;word-wrap:break-word}
.user{align-self:flex-end;background:linear-gradient(135deg,#2563eb,#4f46e5);color:white;border-bottom-right-radius:6px;box-shadow:0 4px 16px rgba(37,99,235,.35)}
.ai{align-self:flex-start;background:#161f3a;border:1px solid #243157;color:#dbe4ff;border-bottom-left-radius:6px}
.img-wrap{width:100%;height:310px;overflow:hidden;border-radius:14px;margin-top:12px;border:1px solid #2a365f;background:#0a0f20;position:relative}
.img-wrap img{position:absolute;top:0;left:0;width:100%;height:115%;object-fit:cover;object-position:top}
.img-wrap::after{content:'';position:absolute;bottom:0;left:0;right:0;height:32px;background:#161f3a;z-index:2}
#bar{position:fixed;bottom:0;left:0;right:0;padding:14px;background:linear-gradient(to top,#070a14 80%,transparent);display:flex;justify-content:center}
.bar-inner{display:flex;gap:10px;align-items:center;width:100%;max-width:900px;background:#121a33;border:1px solid #2a365f;border-radius:28px;padding:7px 7px 7px 18px;box-shadow:0 10px 30px rgba(0,0,0,.5)}
.bar-inner input{flex:1;background:transparent;border:none;color:#fff;outline:none;font-size:15px;padding:10px 0}
.bar-inner button{background:#2563eb;color:#fff;border:none;border-radius:22px;padding:12px 22px;font-weight:700;cursor:pointer}
</style></head><body>
<header><div class="logo"><img src="/logo" onerror="this.style.display='none';this.parentNode.innerText='T'"></div><div class="brand">TITECH <span>AI</span></div></header>
<div id="chat"><div class="msg ai">👋 Welcome to <b>Titech AI</b> by Timileyin Samson<br>Ask anything or generate image — I now show REAL images from Wikipedia!</div></div>
<div id="bar"><div class="bar-inner"><input id="inp" placeholder="Ask anything..."><button onclick="send()">Send</button></div></div>
<script>
async function send(){
 let i=document.getElementById('inp');let t=i.value.trim();if(!t)return;
 let c=document.getElementById('chat');
 c.innerHTML+=`<div class=msg user>${t}</div>`;i.value='';
 c.innerHTML+=`<div class=msg ai id=tmp>Searching...</div>`;c.scrollTop=c.scrollHeight;
 let r=await fetch('/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({message:t})});
 let d=await r.json();document.getElementById('tmp')?.remove();
 c.innerHTML+=`<div class=msg ai>${d.reply}${d.image?`<div class=img-wrap><img src=${d.image}></div>`:''}</div>`;
 c.scrollTop=c.scrollHeight;
}
document.getElementById('inp').addEventListener('keydown',e=>{if(e.key==='Enter')send()});
</script></body></html>
"""

def ask_groq(msg):
    h={"Authorization":f"Bearer {GROQ_KEY}","Content-Type":"application/json"}
    p={"model":"openai/gpt-oss-120b","messages":[{"role":"system","content":"You are Titech AI by Timileyin Samson. Friendly Naija bestie. Short 4-5 sentences."},{"role":"user","content":msg}]}
    try:
        r=requests.post(URL,headers=h,json=p,timeout=60)
        return r.json()["choices"][0]["message"]["content"]
    except: return "I dey here! Ask me again."

@app.route("/")
def home(): return HTML
@app.route("/logo")
@app.route("/logo.png")
@app.route("/logo.jpg")
def logo():
    for n in ["logo.png","logo.jpg","logo.jpeg","logo.webp"]:
        if os.path.exists(n): return send_from_directory(".",n)
    return "",404

@app.route("/chat", methods=["POST"])
def chat():
    m=request.get_json().get("message","").strip()
    low=m.lower()
    pic_words=["image","picture","photo","generate","draw","create","coat of arms","flag","stadium","football","soccer","car","benz","hilux","aeroplane","lion","tiger","eiffel","building"]
    is_pic = any(w in low for w in pic_words)

    if is_pic:
        pr=low
        for bad in ["generate the picture of","generate a picture of","generate the image of","picture of","image of","photo of","generate","please","show me","can you"]:
            pr=pr.replace(bad,"")
        pr=pr.strip()
        if len(pr)<2: pr=low

        # TRY WIKIPEDIA FIRST FOR REAL IMAGE
        wiki = get_wiki_image(pr)
        if wiki:
            img_url, real_title = wiki
            return jsonify({"reply":f"{real_title} - Real image from Wikipedia","image":img_url})

        # IF NO WIKI, FALLBACK TO AI GENERATION
        q=urllib.parse.quote(pr+" photorealistic, ultra detailed, 4k, no text, no watermark")
        img_url=f"https://image.pollinations.ai/prompt/{q}?model=flux-realism&nologo=true&seed={os.urandom(2).hex()}&width=1024&height=1024"
        return jsonify({"reply":pr.title(),"image":img_url})

    return jsonify({"reply":ask_groq(m)})

if __name__=="__main__":
    app.run(host="0.0.0.0",port=int(os.environ.get("PORT",10000)))
