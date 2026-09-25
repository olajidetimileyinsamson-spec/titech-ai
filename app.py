from flask import Flask, request, jsonify, render_template_string, send_from_directory
import requests, os, urllib.parse, random

app = Flask(__name__)
GROQ_KEY = os.environ.get("GROQ_API_KEY", "")

HTML = """
<!DOCTYPE html><html><head>
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Titech AI</title>
<link rel="manifest" href="/manifest.json">
<meta name="theme-color" content="#00a6ff">
<style>
*{box-sizing:border-box}
body{margin:0;background:#0a0a0a;color:#fff;font-family:system-ui;display:flex;flex-direction:column;height:100vh}
.header{padding:14px 16px;border-bottom:1px solid #1f1f1f;display:flex;gap:12px;align-items:center}
.logo{width:42px;height:42px;border-radius:12px;object-fit:cover}
.chat{flex:1;overflow:auto;padding:16px 16px 110px;display:flex;flex-direction:column;gap:10px}
.msg{padding:12px 16px;border-radius:20px;max-width:90%;line-height:1.6;white-space:pre-wrap;font-size:14.5px}
.user{background:#00a6ff;margin-left:auto;border-bottom-right-radius:6px;align-self:flex-end}
.bot{background:#151515;border:1px solid #232323;border-bottom-left-radius:6px;align-self:flex-start}
.bot img{max-width:100%;border-radius:14px;margin-top:10px}
.bar{position:fixed;bottom:0;left:0;right:0;padding:12px;background:#0a0a0a;display:flex;gap:10px}
.iw{flex:1;display:flex;background:#161616;border:1px solid #2a2a2a;border-radius:28px;padding:4px 6px 4px 16px}
input{flex:1;background:transparent;border:none;color:#fff;outline:none;font-size:15px}
button{width:38px;height:38px;border-radius:50%;background:#00a6ff;color:#fff;border:none;font-weight:bold}
</style></head><body>
<div class="header"><img src="/logo.jpg" class="logo"><div><b>Titech AI</b><br><span style="font-size:11px;color:#777">By Timileyin Samson</span></div></div>
<div class="chat" id="c"></div>
<div class="bar"><div class="iw"><input id="q" placeholder="Ask anything, or say generate image of..." onkeydown="if(event.key=='Enter')send()"><button onclick="send()">↑</button></div></div>
<script>
if('serviceWorker' in navigator){navigator.serviceWorker.register('/sw.js')}
let h=JSON.parse(localStorage.getItem('titech_v3')||'[]');
const chat=document.getElementById('c');
function save(){localStorage.setItem('titech_v3',JSON.stringify(h.slice(-60)))}
function fmt(t){let x=t.replace(/\\n/g,'<br>');x=x.replace(/!\\[.*?\\]\\((.*?)\\)/g,'<img src="$1"><br><a href="$1" target="_blank" style="color:#00a6ff;font-size:12px">Download HD</a>');return x;}
function add(role,text,s=true){let d=document.createElement('div');d.className='msg '+(role=='user'?'user':'bot');d.innerHTML=role=='user'?text:fmt(text);chat.appendChild(d);if(s){h.push({role:role,content:text});save()}chat.scrollTop=chat.scrollHeight}
function render(){chat.innerHTML='';if(h.length==0){let g=new Date().getHours()<12?'Good morning':new Date().getHours()<17?'Good afternoon':'Good evening';let w=document.createElement('div');w.className='msg bot';w.innerHTML='<b>'+g+'! I am Titech AI 👋</b><br><br>Connected to main brain. I understand English, Pidgin, Yoruba, Igbo, Hausa. Try: Bawo ni / Kedu / How far / Generate image of...';chat.appendChild(w);}else{h.forEach(m=>{let d=document.createElement('div');d.className='msg '+(m.role=='user'?'user':'bot');d.innerHTML=m.role=='user'?m.content:fmt(m.content);chat.appendChild(d);});}chat.scrollTop=chat.scrollHeight}render();
async function send(){let q=document.getElementById('q').value.trim();if(!q)return;document.getElementById('q').value='';add('user',q);let t=document.createElement('div');t.className='msg bot';t.textContent='Thinking...';chat.appendChild(t);chat.scrollTop=chat.scrollHeight;let r=await fetch('/ask',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({question:q,history:h.slice(-8)})});let j=await r.json();t.remove();add('assistant',j.answer);}
</script></body></html>
"""

@app.route('/')
def home(): return render_template_string(HTML)
@app.route('/logo.jpg')
def logo(): return send_from_directory('.', 'logo.jpg')
@app.route('/manifest.json')
def man(): return jsonify({"name":"Titech AI","short_name":"Titech AI","start_url":"/","display":"standalone","background_color":"#0a0a0a","theme_color":"#00a6ff","icons":[{"src":"/logo.jpg","sizes":"192x192","type":"image/jpeg"}]})
@app.route('/sw.js')
def sw(): return "self.addEventListener('install',e=>self.skipWaiting())",200,{'Content-Type':'application/javascript'}

@app.route('/ask',methods=['POST'])
def ask():
    data=request.json; q=data.get('question','').strip(); l=q.lower()

    # IMAGE - Flux HD
    if any(w in l for w in ['generate','create image','draw','logo','picture of','image of','make image']):
        clean=q
        for w in ['generate','create image','create','make an image of','make image of','image of','picture of','draw','please']: clean=clean.lower().replace(w,'')
        clean=clean.strip() or "futuristic T logo"
        if 'titech' in clean or 'logo' in l: prompt=f"3d letter T chrome metallic electric blue neon glow luxury minimal logo black background 8k {clean}"
        else: prompt=f"{clean}, ultra detailed photorealistic 8k masterpiece cinematic lighting highly detailed"
        url="https://image.pollinations.ai/prompt/"+urllib.parse.quote(prompt)+"?width=1024&height=1024&model=flux&enhance=true&nologo=true&seed="+str(random.randint(1,999999))
        return jsonify(answer=f"Generated **{clean}** with main brain Flux:\n\n![img]({url})")

    # MAIN BRAIN - GROQ
    if GROQ_KEY:
        try:
            r=requests.post("https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization":f"Bearer {GROQ_KEY}","Content-Type":"application/json"},
            json={"model":"llama-3.3-70b-versatile","messages":[{"role":"system","content":"You are Titech AI, built by Timileyin Samson. Be friendly, short, helpful. You MUST reply in the same language user used: English, Pidgin, Yoruba, Igbo, Hausa. If user says Bawo ni reply Yoruba, Kedu Igbo, Yaya Hausa, How far Pidgin. No prefix like 'You said'."},{"role":"user","content":q}],"temperature":0.7,"max_tokens":700},timeout=20)
            if r.status_code==200:
                return jsonify(answer=r.json()['choices'][0]['message']['content'].strip())
        except Exception as e: print(e)

    # backup
    return jsonify(answer="I'm Titech AI! Main brain is connecting... Try again. You said: "+q)

if __name__=='__main__': app.run(host='0.0.0.0',port=int(os.environ.get('PORT',10000)))
