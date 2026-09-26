import os, requests, urllib.parse
from flask import Flask, request, jsonify, send_from_directory

app = Flask(__name__)
GROQ_KEY = os.environ.get("GROQ_API_KEY","").strip()
URL = "https://api.groq.com/openai/v1/chat/completions"

def get_wiki_image_only(query):
    try:
        # 1. Search Wikipedia
        s_url = f"https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch={urllib.parse.quote(query)}&format=json&srlimit=1"
        r = requests.get(s_url, timeout=15, headers={"User-Agent":"TitechAI/1.0"}).json()
        if not r.get("query",{}).get("search"):
            return None
        title = r["query"]["search"][0]["title"]

        # 2. Get all images on that page
        img_list_url = f"https://en.wikipedia.org/w/api.php?action=query&titles={urllib.parse.quote(title)}&prop=images&format=json&imlimit=30"
        r2 = requests.get(img_list_url, timeout=15, headers={"User-Agent":"TitechAI/1.0"}).json()
        pages = r2.get("query",{}).get("pages",{})
        image_titles = []
        for pid in pages:
            for img in pages[pid].get("images",[]):
                image_titles.append(img["title"])

        # 3. Find best real photo (JPG/PNG, not icon)
        for img_title in image_titles:
            low_img = img_title.lower()
            if any(x in low_img for x in ["icon","symbol","commons-logo","wikidata","small","disambig"]):
                continue

            info_url = f"https://en.wikipedia.org/w/api.php?action=query&titles={urllib.parse.quote(img_title)}&prop=imageinfo&iiprop=url&format=json"
            r3 = requests.get(info_url, timeout=15, headers={"User-Agent":"TitechAI/1.0"}).json()
            pgs = r3.get("query",{}).get("pages",{})
            for p in pgs:
                info = pgs[p].get("imageinfo",[{}])[0]
                url = info.get("url","")
                if not url:
                    continue

                # If SVG, convert to PNG using Wikimedia render
                if url.lower().endswith(".svg"):
                    # Use Special:FilePath to get PNG render
                    filename = img_title.replace("File:","")
                    png_url = f"https://commons.wikimedia.org/wiki/Special:FilePath/{urllib.parse.quote(filename)}?width=800"
                    return png_url, title

                if any(url.lower().endswith(ext) for ext in [".png",".jpg",".jpeg",".webp"]):
                    return url, title

    except Exception as e:
        print("Wiki error:", e)
        return None
    return None

HTML_PAGE = """
<html><head><meta name='viewport' content='width=device-width,initial-scale=1'>
<title>Titech AI</title>
<link href='https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap' rel='stylesheet'>
<style>
*{box-sizing:border-box;font-family:Inter,system-ui}
body{margin:0;background:#070a14;color:#e8eaff;display:flex;flex-direction:column;height:100vh}
header{padding:12px 16px;display:flex;align-items:center;gap:12px;background:#0d1120;border-bottom:1px solid #1e294d;position:sticky;top:0;z-index:10}
.logo{width:42px;height:42px;border-radius:12px;background:linear-gradient(135deg,#4f46e5,#06b6d4);display:flex;align-items:center;justify-content:center;font-weight:900;color:white;overflow:hidden}
.logo img{width:100%;height:100%;object-fit:cover}
.brand{font-weight:800;font-size:18px}.brand span{color:#60a5fa}
#chat{flex:1;overflow:auto;padding:16px 16px 120px 16px;max-width:900px;margin:0 auto;width:100%;display:flex;flex-direction:column;gap:12px}
.msg{padding:14px 18px;border-radius:20px;max-width:82%;line-height:1.5;font-size:15px;word-wrap:break-word;white-space:pre-wrap}
.user{align-self:flex-end;background:linear-gradient(135deg,#2563eb,#4f46e5);color:white;border-bottom-right-radius:6px}
.ai{align-self:flex-start;background:#161f3a;border:1px solid #243157;color:#dbe4ff;border-bottom-left-radius:6px}
.img-wrap{width:100%;height:400px;overflow:hidden;border-radius:16px;margin-top:12px;border:1px solid #2a365f;background:#ffffff;display:flex;align-items:center;justify-content:center}
.img-wrap img{width:100%;height:100%;object-fit:contain;background:white}
#bar{position:fixed;bottom:0;left:0;right:0;padding:14px;background:linear-gradient(to top,#070a14 85%,transparent);display:flex;justify-content:center}
.bar-inner{display:flex;gap:10px;align-items:center;width:100%;max-width:900px;background:#121a33;border:1px solid #2a365f;border-radius:28px;padding:7px 7px 7px 18px}
.bar-inner input{flex:1;background:transparent;border:none;color:#fff;outline:none;font-size:15px;padding:10px 0}
.bar-inner button{background:#2563eb;color:#fff;border:none;border-radius:22px;padding:12px 22px;font-weight:700;cursor:pointer}
</style></head><body>
<header><div class='logo'><img src='/logo' onerror="this.style.display='none';this.parentNode.innerText='T'"></div><div class='brand'>TITECH <span>AI</span></div></header>
<div id='chat'><div class='msg ai'>Welcome to Titech AI — Now with REAL Wikipedia Images Only! 🌍
Try: Nigeria coat of arms, Eiffel Tower, Lion</div></div>
<div id='bar'><div class='bar-inner'><input id='inp' placeholder='Ask anything...'><button onclick='send()'>Send</button></div></div>
<script>
async function send(){
 let i=document.getElementById('inp');let t=i.value.trim();if(!t)return;
 let c=document.getElementById('chat');
 c.innerHTML+=`<div class=msg user>${t}</div>`;i.value='';
 c.innerHTML+=`<div class=msg ai id=tmp>Searching Wikipedia...</div>`;c.scrollTop=c.scrollHeight;
 let r=await fetch('/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({message:t})});
 let d=await r.json();document.getElementById('tmp')?.remove();
 c.innerHTML+=`<div class=msg ai>${d.reply}${d.image?`<div class="img-wrap"><img src="${d.image}"></div>`:''}</div>`;
 c.scrollTop=c.scrollHeight;
}
document.getElementById('inp').addEventListener('keydown',e=>{if(e.key==='Enter')send()});
</script></body></html>
"""

def ask_groq(msg):
    h={"Authorization":f"Bearer {GROQ_KEY}","Content-Type":"application/json"}
    p={"model":"openai/gpt-oss-120b","messages":[{"role":"system","content":"You are Titech AI by Timileyin Samson. Friendly Naija bestie. Short answers."},{"role":"user","content":msg}]}
    try:
        r=requests.post(URL,headers=h,json=p,timeout=60)
        return r.json()["choices"][0]["message"]["content"]
    except:
        return "I dey here! Ask again."

@app.route("/")
def home():
    return HTML_PAGE

@app.route("/logo")
@app.route("/logo.png")
@app.route("/logo.jpg")
def logo():
    for name in ["logo.png","logo.jpg","logo.jpeg","logo.webp"]:
        if os.path.exists(name):
            return send_from_directory(".",name)
    return "",404

@app.route("/chat", methods=["POST"])
def chat_route():
    m=(request.get_json() or {}).get("message","").strip()
    if not m:
        return jsonify({"reply":"Yes boss?"})
    low=m.lower()
    pic_triggers=["picture","image","photo","flag","coat of arms","stadium","football","lion","eiffel","tower","nigeria"]
    is_pic = any(w in low for w in pic_triggers)

    if is_pic:
        # Clean prompt
        pr=low
        for bad in ["generate a picture of","picture of","image of","photo of","generate","please","show me"]:
            pr=pr.replace(bad,"")
        pr=pr.strip()
        if len(pr)<2:
            pr=low

        wiki = get_wiki_image_only(pr)
        if wiki:
            url, title = wiki
            return jsonify({"reply":f"Here is REAL Wikipedia image: {title}","image":url})
        else:
            return jsonify({"reply":f"Sorry boss, I no see '{pr.title()}' image for Wikipedia. Try clearer name like 'Coat of arms of Nigeria' or 'Lion'. I no dey generate fake AI again — na Wikipedia only now."})

    return jsonify({"reply":ask_groq(m)})

if __name__=="__main__":
    app.run(host="0.0.0.0",port=int(os.environ.get("PORT",10000)))
