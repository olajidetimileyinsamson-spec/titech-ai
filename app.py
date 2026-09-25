from flask import Flask, request, jsonify, render_template_string, send_from_directory
import requests, os, urllib.parse, random

app = Flask(__name__)

HTML = """
<!DOCTYPE html>
<html><head>
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Titech AI</title>
<link rel="manifest" href="/manifest.json">
<meta name="theme-color" content="#a855f7">
<link rel="icon" href="/logo.jpg">
<style>
*{box-sizing:border-box}
body{margin:0;background:#0a0a0a;color:#fff;font-family:system-ui,sans-serif;display:flex;flex-direction:column;height:100vh}
.header{padding:14px 16px;border-bottom:1px solid #1f1f1f;display:flex;gap:12px;align-items:center;position:sticky;top:0;background:#0a0a0a;z-index:10}
.logo{width:42px;height:42px;border-radius:12px;object-fit:cover;border:1px solid #222}
.chat{flex:1;overflow:auto;padding:16px;padding-bottom:110px;display:flex;flex-direction:column;gap:8px}
.msg{padding:12px 16px;border-radius:20px;max-width:88%;line-height:1.6;white-space:pre-wrap;font-size:14.5px;word-wrap:break-word}
.user{background:#a855f7;margin-left:auto;border-bottom-right-radius:6px;align-self:flex-end}
.bot{background:#151515;border:1px solid #232323;border-bottom-left-radius:6px;align-self:flex-start}
.bot img{max-width:100%;border-radius:12px;margin-top:10px;display:block;clip-path: inset(0 0 24px 0); margin-bottom:-24px}
.thinking{display:flex;gap:6px;align-items:center;color:#888}
.dot{width:6px;height:6px;background:#777;border-radius:50%;animation:b 1.4s infinite}
.dot:nth-child(2){animation-delay:.2s}.dot:nth-child(3){animation-delay:.4s}
@keyframes b{0%,60%,100%{transform:translateY(0);opacity:.4}30%{transform:translateY(-5px);opacity:1}}
.bar{position:fixed;bottom:0;left:0;right:0;padding:12px;background:#0a0a0a;display:flex;gap:10px}
.inputWrap{flex:1;display:flex;background:#161616;border:1px solid #2a2a2a;border-radius:28px;padding:4px 6px 4px 16px}
input{flex:1;background:transparent;border:none;color:#fff;outline:none;font-size:15px;padding:10px 0}
button{width:38px;height:38px;border-radius:50%;background:#a855f7;color:#fff;border:none;cursor:pointer}
</style></head>
<body>
<div class="header"><img src="/logo.jpg" class="logo" onerror="this.src='/logo.png'"><div><b>Titech AI</b><br><span style="font-size:11px;color:#777">By Timileyin Samson • PWA Ready</span></div></div>
<div class="chat" id="c"><div class="msg bot">PWA Active! ✅ Install me from browser menu. Hybrid brain on. Ask anything!</div></div>
<div class="bar"><div class="inputWrap"><input id="q" placeholder="Ask anything or generate image..." onkeydown="if(event.key=='Enter')send()"><button onclick="send()">↑</button></div></div>
<script>
if('serviceWorker' in navigator){navigator.serviceWorker.register('/sw.js')}
let history=[];
const chat=document.getElementById('c');
function format(t){
 let h=t.replace(/\\n/g,'<br>');
 h=h.replace(/!\\[.*?\\]\\((.*?)\\)/g,'<img src="$1" loading="lazy"><br><a href="$1" target="_blank" style="color:#a855f7;font-size:12px">Download HD</a>');
 return h;
}
async function send(){
 let text=document.getElementById('q').value.trim(); if(!text)return;
 document.getElementById('q').value='';
 let u=document.createElement('div'); u.className='msg user'; u.textContent=text; chat.appendChild(u);
 history.push({role:'user',content:text});
 let t=document.createElement('div'); t.className='msg bot thinking'; t.innerHTML='Thinking <span class="dot"></span><span class="dot"></span><span class="dot"></span>'; chat.appendChild(t);
 chat.scrollTop=chat.scrollHeight;
 let r=await fetch('/ask',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({question:text,history:history.slice(-8)})});
 let j=await r.json();
 t.className='msg bot'; t.innerHTML=format(j.answer);
 history.push({role:'assistant',content:j.answer});
 chat.scrollTop=chat.scrollHeight;
}
</script>
</body>
</html>
"""

@app.route('/')
def home(): return render_template_string(HTML)

@app.route('/logo.jpg')
def logo_jpg(): return send_from_directory('.', 'logo.jpg')
@app.route('/logo.png')
def logo_png():
    if os.path.exists('logo.jpg'): return send_from_directory('.', 'logo.jpg')
    if os.path.exists('logo.png'): return send_from_directory('.', 'logo.png')
    return "",404

@app.route('/manifest.json')
def manifest():
    return jsonify({
        "name": "Titech AI",
        "short_name": "Titech AI",
        "start_url": "/",
        "display": "standalone",
        "background_color": "#0a0a0a",
        "theme_color": "#a855f7",
        "icons": [
            {"src": "/logo.jpg", "sizes": "192x192", "type": "image/jpeg"},
            {"src": "/logo.jpg", "sizes": "512x512", "type": "image/jpeg"}
        ]
    })

@app.route('/sw.js')
def sw():
    js = """
    self.addEventListener('install', e => self.skipWaiting());
    self.addEventListener('activate', e => self.clients.claim());
    self.addEventListener('fetch', e => {
      e.respondWith(fetch(e.request).catch(()=> caches.match(e.request)));
    });
    """
    return js, 200, {'Content-Type': 'application/javascript'}

def offline_answer(q):
    l=q.lower()
    is_article = any(x in l for x in ['article','essay','450','500','long','detailed','write','about nigeria'])
    if "nigeria" in l and is_article:
        return """**Nigeria - The Giant of Africa (450+ Words)**

Nigeria is the most populous country in Africa with over 230M people. Located in West Africa, bordered by Benin, Niger, Chad, Cameroon and Atlantic Ocean.

**History:** Independence Oct 1, 1960 from Britain. Became republic 1963. 36 states + FCT Abuja. Civil war 1967-1970.

**People & Culture:** 250+ ethnic groups - Hausa-Fulani (North), Yoruba (South-West), Igbo (South-East). 500+ languages, English official. World famous for Afrobeats (Burna Boy, Wizkid, Davido) and Nollywood (2nd largest film industry).

**Economy:** Largest economy in Africa. Oil largest producer in Africa, plus agriculture, tech (Flutterwave, Paystack in Lagos Yabacon Valley), entertainment. Lagos is economic hub, 16M+ people. Abuja is planned capital since 1991 with Aso Rock, National Mosque, etc.

**Future:** Young population median 18 years driving innovation. Projected top 3 economy by 2050. Giant of Africa indeed.
"""
    if "nigeria" in l: return "**Nigeria - Giant of Africa**\n\n• 230M+ people, 36 states\n• Capital: Abuja (1991), Largest: Lagos\n• 250+ ethnic groups (Hausa, Yoruba, Igbo)\n• Independence Oct 1, 1960\n• Economy: Oil, tech, entertainment"
    if "abuja" in l: return "**Abuja**\n\nCapital since 1991, planned city in FCT. Places: Aso Rock Villa, National Mosque, Church, Millennium Park. Districts: Maitama, Asokoro, Wuse, Garki."
    if "lagos" in l: return "**Lagos**\n\nLargest city 16M+, former capital, tech hub Yaba, business hub VI/Lekki."
    if "futa" in l: return "**FUTA**\n\nFederal University of Technology Akure, founded 1981, top tech university for Engineering/Computing."
    if "quantum" in l: return "**Quantum Computing**\n\nUses qubits (0 AND 1 at same time). Superposition + entanglement = massive speed. For drug discovery, cryptography, AI. Leaders: IBM, Google."
    return f"**{q}**\n\n{q} is important. It has key meaning, uses, benefits. If you need article/essay, say 'Write 500-word article about {q}' and I'll give full."

@app.route('/ask', methods=['POST'])
def ask():
    data=request.json
    q=data.get('question','').strip()
    l=q.lower()
    if not q: return jsonify(answer="Ask me anything!")
    if l in ['thanks','thank you','thx','ok','okay','cool','nice','great','yeah','alright']:
        return jsonify(answer="You're welcome! 😊 What next?")
    if l in ['hi','hello','hey','hii','yo']:
        return jsonify(answer="Hey! 👋 I'm Titech AI by Timileyin Samson. Install me as app from your browser menu!")
    if 'who are you' in l or 'who built you' in l:
        return jsonify(answer="I'm Titech AI built by Timileyin Samson — now PWA installable!")

    if any(w in l for w in ['generate','create image','draw','make an image','logo','picture of','image of']):
        clean=q.lower()
        for bad in ['generate','create','make','draw','an image of','a image of','image of','image','please','for me','a 3d logo for']:
            clean=clean.replace(bad,'')
        clean=clean.strip() or "titech"
        final = "3D letter T logo, chrome metallic letter T, futuristic purple neon glow, minimalist luxury brand logo, black background, centered, ultra sharp, 8k" if ("logo" in l or "titech" in l) else f"{clean}, ultra detailed, photorealistic, 8k, masterpiece"
        encoded=urllib.parse.quote(final)
        url=f"https://image.pollinations.ai/prompt/{encoded}?width=1024&height=1024&model=flux&enhance=true&nologo=true&seed={random.randint(1,999999)}"
        return jsonify(answer=f"HD image for **{clean}**:\n\n![generated]({url})")

    # MAIN BRAIN
    try:
        payload={"model":"openai","messages":[{"role":"system","content":"You are Titech AI by Timileyin Samson. Be helpful, direct, answer fully. Never say 'You said:'. If asked for article, write at least 450 words."},{"role":"user","content":q}],"stream":False}
        r=requests.post("https://text.pollinations.ai/openai", json=payload, timeout=25)
        if r.status_code==200:
            j=r.json()
            if 'choices' in j and j['choices']:
                ans=j['choices'][0]['message']['content']
                if len(ans)>30: return jsonify(answer=ans.strip())
    except: pass

    try:
        encoded_q=urllib.parse.quote(f"You are Titech AI. Answer fully: {q}")
        r=requests.get(f"https://text.pollinations.ai/{encoded_q}?model=mistral", timeout=15)
        if r.status_code==200 and len(r.text.strip())>30 and "You said:" not in r.text:
            return jsonify(answer=r.text.strip())
    except: pass

    return jsonify(answer=offline_answer(q))

if __name__=='__main__':
    app.run(host='0.0.0.0',port=int(os.environ.get('PORT',10000)))
