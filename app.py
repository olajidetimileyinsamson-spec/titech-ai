from flask import Flask, request, jsonify, render_template_string, send_from_directory
import requests, os, urllib.parse, random

app = Flask(__name__)

HTML = """
<!DOCTYPE html>
<html><head><meta name="viewport" content="width=device-width, initial-scale=1"><title>Titech AI</title>
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
<div class="header"><img src="/logo.jpg" class="logo" onerror="this.src='/logo.png'"><div><b>Titech AI</b><br><span style="font-size:11px;color:#777">By Timileyin Samson • Hybrid Brain</span></div></div>
<div class="chat" id="c"><div class="msg bot">Hybrid active! ✅ Main brain first, offline backup. Try "Explain quantum computing" or "Tell me about FUTA"</div></div>
<div class="bar"><div class="inputWrap"><input id="q" placeholder="Ask anything..." onkeydown="if(event.key=='Enter')send()"><button onclick="send()">↑</button></div></div>
<script>
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

def offline_answer(q):
    l=q.lower()
    if "abuja" in l:
        return "**Abuja - Capital of Nigeria**\n\nAbuja became capital in 1991, replacing Lagos. Located in FCT, center of Nigeria.\n\n• Population: ~3.8M\n• Key places: Aso Rock Villa, National Mosque, National Church, Millennium Park\n• Districts: Maitama, Asokoro, Wuse, Garki\n• Planned city with wide roads\n\nWhat about Abuja you need? History, places to visit, cost of living?"
    if "lagos" in l:
        return "**Lagos - Economic Hub**\n\nLargest city in Nigeria, 16M+ people, former capital.\n• VI, Ikoyi, Lekki - business areas\n• Yaba - tech hub (Paystack, Flutterwave)\n• Famous for Afrobeats, Nollywood, markets, nightlife\n\nAsk me more!"
    if "nigeria" in l:
        return "**Nigeria - Giant of Africa**\n\n• 230M+ people, 36 states\n• Capital: Abuja, Largest: Lagos\n• 250+ ethnic groups (Hausa, Yoruba, Igbo)\n• Independence: Oct 1, 1960\n• Economy: Oil, tech, entertainment\n\nWhat about Nigeria?"
    if "futa" in l:
        return "**FUTA - Federal University of Technology Akure**\n\nFounded 1981 in Ondo State. Top tech school.\n• Courses: Engineering, Computing, Architecture, Sciences\n• Known for technology and research\n• Motto: Technology for self-reliance\n\nNeed admission, cut-off, or courses?"
    if "quantum" in l:
        return "**Quantum Computing**\n\nNormal PC uses bits (0 or 1). Quantum uses qubits that can be 0 AND 1 at same time (superposition).\n\n• Superposition = parallel processing, very fast\n• Entanglement = linked qubits\n• Power: Solves in seconds what normal PC takes years\n• Use: Drug discovery, cryptography, AI\n\nLeaders: IBM, Google, Microsoft. Still early but future of computing."
    if "titech" in l:
        return "**Titech**\n\nTech brand by Timileyin Samson building AI tools like Titech AI (chat + HD images). Vision: Make AI accessible in Africa."
    # Generic but helpful - never deviates
    return f"**{q}**\n\nHere's a clear answer:\n\n{q} is important. In simple terms: it has key meaning, uses, and benefits that affect daily life and technology.\n\n• What it is: Core concept of {q}\n• Why it matters: Impact on people and industry\n• Example: How {q} is used in real world\n• Future: Growing fast\n\nTell me if you want essay, summary, or detailed explanation and I will write full article now."

@app.route('/ask', methods=['POST'])
def ask():
    data=request.json
    q=data.get('question','').strip()
    hist=data.get('history',[])
    l=q.lower()

    if not q:
        return jsonify(answer="Ask me anything!")
    if l in ['thanks','thank you','thx','ok','okay','cool','nice','great','yeah','alright']:
        return jsonify(answer="You're welcome! 😊 What next?")
    if l in ['hi','hello','hey','hii','yo']:
        return jsonify(answer="Hey! 👋 I'm Titech AI by Timileyin Samson. Main brain + backup active. What do you need?")
    if 'who are you' in l or 'who built you' in l or 'who developed you' in l:
        return jsonify(answer="I'm Titech AI built by Timileyin Samson — hybrid brain: main AI when online, smart offline backup when network slow.")

    # IMAGE - always works
    if any(w in l for w in ['generate','create image','draw','make an image','logo','picture of','image of']):
        clean=q.lower()
        for bad in ['generate','create','make','draw','an image of','a image of','image of','image','please','for me','a 3d logo for']:
            clean=clean.replace(bad,'')
        clean=clean.strip() or "titech"
        if "logo" in l or "titech" in l:
            final="3D letter T logo, chrome metallic letter T, futuristic purple neon glow, minimalist luxury brand logo, black background, centered, ultra sharp, 8k"
        else:
            final=f"{clean}, ultra detailed, photorealistic, 8k, masterpiece, sharp focus"
        encoded=urllib.parse.quote(final)
        url=f"https://image.pollinations.ai/prompt/{encoded}?width=1024&height=1024&model=flux&enhance=true&nologo=true&seed={random.randint(1,999999)}"
        return jsonify(answer=f"HD image for **{clean}**:\n\n![generated]({url})")

    # TRY MAIN BRAIN FIRST - POST method (more reliable on Render)
    try:
        payload={
            "model":"openai",
            "messages":[
                {"role":"system","content":"You are Titech AI by Timileyin Samson. Be helpful, concise, friendly. Answer directly, never ask 'what specifically do you want to know?' - just answer."},
                {"role":"user","content":q}
            ],
            "stream":False
        }
        r=requests.post("https://text.pollinations.ai/openai", json=payload, timeout=25)
        if r.status_code==200:
            j=r.json()
            # OpenAI format
            if 'choices' in j and len(j['choices'])>0:
                ans=j['choices'][0]['message']['content']
                if len(ans)>20:
                    return jsonify(answer=ans.strip())
            # plain text format
            if len(r.text)>20 and "You said:" not in r.text:
                return jsonify(answer=r.text.strip())
    except Exception as e:
        print("Main brain POST failed:", e)

    # TRY SECOND METHOD - GET with mistral
    try:
        encoded_q=urllib.parse.quote(f"You are Titech AI by Timileyin Samson. Answer: {q}")
        r=requests.get(f"https://text.pollinations.ai/{encoded_q}?model=mistral", timeout=15)
        if r.status_code==200 and len(r.text.strip())>30:
            if "Could you let me know" not in r.text and "You said:" not in r.text:
                return jsonify(answer=r.text.strip())
    except:
        pass

    # BACKUP OFFLINE - REAL ANSWER, NO DEVIATION
    return jsonify(answer=offline_answer(q))

if __name__=='__main__':
    app.run(host='0.0.0.0',port=int(os.environ.get('PORT',10000)))
