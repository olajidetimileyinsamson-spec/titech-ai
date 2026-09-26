import os, requests, urllib.parse
from flask import Flask, request, jsonify

app = Flask(__name__)

GROQ_KEY = os.environ.get("GROQ_API_KEY","").strip()
UNSPLASH_KEY = os.environ.get("UNSPLASH_KEY","").strip()
URL = "https://api.groq.com/openai/v1/chat/completions"

def get_wiki(q):
    low = q.lower()
    if "nigeria" in low and "coat" in low:
        return "https://upload.wikimedia.org/wikipedia/commons/7/79/Coat_of_arms_of_Nigeria.svg"
    if "nigeria" in low and "flag" in low:
        return "https://upload.wikimedia.org/wikipedia/commons/7/79/Flag_of_Nigeria.svg"
    try:
        s = requests.get(f"https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch={q}&format=json", timeout=5).json()
        if not s["query"]["search"]:
            return None
        title = s["query"]["search"][0]["title"]
        img = requests.get(f"https://en.wikipedia.org/w/api.php?action=query&titles={title}&prop=pageimages&pithumbsize=500&format=json", timeout=5).json()
        pages = img["query"]["pages"]
        for p in pages.values():
            if "thumbnail" in p:
                return p["thumbnail"]["source"]
    except:
        pass
    return None

def get_unsplash(q):
    if not UNSPLASH_KEY:
        return None
    try:
        r = requests.get(f"https://api.unsplash.com/search/photos?query={urllib.parse.quote(q)}&per_page=1&client_id={UNSPLASH_KEY}", timeout=5).json()
        if r.get("results"):
            return r["results"][0]["urls"]["regular"]
    except:
        pass
    return None

HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>TITECH AI</title>
<style>
body{background:#070c1f;color:white;font-family:Arial;margin:0}
.top{background:#111a3a;padding:16px;text-align:center;font-weight:bold;font-size:18px}
#chat{padding:15px;padding-bottom:95px;display:flex;flex-direction:column;gap:14px;min-height:70vh}
.user{background:#2b5cff;align-self:flex-end;padding:10px 14px;border-radius:18px 18px 2px 18px;max-width:80%;word-wrap:break-word}
.ai{background:#1a2447;align-self:flex-start;padding:12px 14px;border-radius:14px 14px 14px 2px;max-width:85%;position:relative}
.ai img{width:100%;border-radius:10px;margin-top:8px;display:block}
.txt{white-space:pre-wrap;line-height:1.4}
.btns{margin-top:8px;display:flex;gap:6px;flex-wrap:wrap}
.small{background:#24315f;color:#a9c2ff;border:1px solid #32407a;padding:6px 10px;border-radius:8px;font-size:12px;cursor:pointer}
.small:active{background:#2f4488}
.bottom{position:fixed;bottom:0;left:0;right:0;background:#0f1936;padding:10px;display:flex;gap:8px;border-top:1px solid #1e2a5a}
#inp{flex:1;background:#1a2447;border:none;color:white;padding:13px 16px;border-radius:25px;outline:none}
#send{background:#2b5cff;border:none;color:white;padding:13px 20px;border-radius:25px;font-weight:bold}
</style>
</head>
<body>
<div class="top">TITECH AI ✨</div>
<div id="chat">
<div class="ai"><div class="txt">Hello! I am TITECH AI. Ask me anything. You can now Copy my replies and Save images.</div>
<div class="btns"><button class="small" onclick="copyT(this)">📋 Copy</button></div>
</div>
</div>
<div class="bottom">
<input id="inp" placeholder="Ask me anything..." autocomplete="off">
<button id="send" onclick="sendMsg()">Send</button>
</div>
<script>
const chat=document.getElementById('chat');
const inp=document.getElementById('inp');
function copyT(btn){
  const txt=btn.closest('.ai').querySelector('.txt').innerText;
  navigator.clipboard.writeText(txt).then(()=>{
    let old=btn.innerText; btn.innerText='✅ Copied';
    setTimeout(()=>btn.innerText=old,1500);
  });
}
function saveImg(url){
  const a=document.createElement('a');
  a.href=url; a.download='titech-image.jpg'; a.target='_blank';
  document.body.appendChild(a); a.click(); a.remove();
}
async function sendMsg(){
  const msg=inp.value.trim(); if(!msg) return;
  chat.innerHTML+=`<div class="user">${msg}</div>`; inp.value='';
  window.scrollTo(0,document.body.scrollHeight);
  const res=await fetch('/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({message:msg})});
  const data=await res.json();
  let html=`<div class="ai"><div class="txt">${data.reply}</div>`;
  if(data.image){
    html+=`<img src="${data.image}"><div class="btns"><button class="small" onclick="saveImg('${data.image}')">⬇️ Save Image</button></div>`;
  }
  html+=`<div class="btns"><button class="small" onclick="copyT(this)">📋 Copy Text</button></div></div>`;
  chat.innerHTML+=html;
  window.scrollTo(0,document.body.scrollHeight);
}
inp.addEventListener('keypress',e=>{ if(e.key==='Enter') sendMsg(); });
</script>
</body>
</html>
"""

@app.route("/")
def home():
    return HTML_PAGE

@app.route("/chat", methods=["POST"])
def chat():
    q = request.json.get("message","")
    image_url = None
    low = q.lower()
    if any(w in low for w in ["image","photo","picture","flag","coat","logo","show"]):
        image_url = get_wiki(q) or get_unsplash(q)
    try:
        if not GROQ_KEY:
            reply = "Groq API Key not set in Render Environment."
        else:
            headers = {"Authorization": f"Bearer {GROQ_KEY}", "Content-Type": "application/json"}
            payload = {"model": "openai/gpt-oss-120b", "messages": [{"role":"user","content": q}]}
            r = requests.post(URL, headers=headers, json=payload, timeout=20)
            j = r.json()
            if "choices" in j:
                reply = j["choices"][0]["message"]["content"]
            else:
                reply = f"Groq Error: {j}"
    except Exception as e:
        reply = f"Error: {e}"
    return jsonify({"reply": reply, "image": image_url})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
