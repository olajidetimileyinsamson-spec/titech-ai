from flask import Flask, request, jsonify, render_template_string, send_from_directory
import requests, os, urllib.parse, json

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
<div class="header"><img src="/logo.jpg" class="logo" onerror="this.src='/logo.png'"><div><b>Titech AI</b><br><span style="font-size:11px;color:#777">By Timileyin Samson • Chat Fixed</span></div></div>
<div class="chat" id="c"><div class="msg bot">Chat fixed! ✅ Now ask me anything: "Tell me about Abuja", "What is Lagos", "Write essay about Titech"</div></div>
<div class="bar"><div class="inputWrap"><input id="q" placeholder="Ask anything or generate image..." onkeydown="if(event.key=='Enter')send()"><button onclick="send()">↑</button></div></div>
<script>
let history=[];
const chat=document.getElementById('c');
function format(t){
 let h=t.replace(/\\n/g,'<br>');
 h=h.replace(/!\\[.*?\\]\\((.*?)\\)/g,'<img src="$1" loading="lazy"><br><a href="$1" target="_blank" style="color:#a855f7;font-size:12px">Download</a>');
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

def smart_fallback(q):
    l = q.lower()
    if "abuja" in l:
        return "**Abuja — Capital of Nigeria:**\n\nAbuja is the capital city of Nigeria, located in the center of the country. Created in the 1970s, it became capital in 1991 to be more central and neutral.\n\n• Home to Aso Rock, National Mosque, National Church\n• Planned city with wide roads and districts like Wuse, Garki, Maitama\n• Population ~3.5 million\n• Political and administrative center\n\nWhat about Abuja you want? History, places to visit, cost of living?"
    if "lagos" in l:
        return "**Lagos — Largest City in Nigeria:**\n\nLagos is Nigeria's economic capital, former capital before Abuja. Over 16 million people, hub for tech, music (Afrobeats), Nollywood, and business.\n\n• Islands: Victoria Island, Ikoyi, Lekki\n• Mainland: Ikeja, Yaba (tech hub)\n• Famous for markets, beaches, nightlife\n• Home to biggest tech startups in Africa\n\nWhat do you want to know about Lagos?"
    if "titech" in l:
        return "**Titech:**\nTitech is a tech brand by Timileyin Samson building smart AI tools like Titech AI — a chat + image generator that is fast, simple, and built for Africa.\n\nVision: Make AI accessible to everyone.\n\nWant a full business description, slogan, or website text for Titech?"
    if len(q.split()) <= 3:
        return f"**{q}:**\n\n{q} is an important topic! Could you tell me what you want to know specifically? For example: definition, history, importance, or how it works? I'll give you a detailed answer right away."
    return f"I'm Titech AI by Timileyin Samson. You asked about: **{q}**\n\nHere's a quick helpful answer: {q} is a topic I can explain in detail — its meaning, history, benefits, and examples. Tell me what angle you need (essay, summary, explanation) and I'll write it fully for you."

@app.route('/ask', methods=['POST'])
def ask():
    data=request.json
    q=data.get('question','').strip()
    hist=data.get('history',[])
    l=q.lower()

    if l in ['thanks','thank you','thx','ok','okay','cool','nice','great','yeah','alright']:
        return jsonify(answer="You're welcome! 😊 What else should I do for you?")
    if l in ['hi','hello','hey','hii','yo']:
        return jsonify(answer="Hey! 👋 I'm Titech AI by Timileyin Samson. Ask me anything or generate images!")
    if 'who are you' in l or 'who built you' in l or 'who developed you' in l:
        return jsonify(answer="I'm Titech AI built by Timileyin Samson — your smart assistant for chat and image generation.")

    if any(w in l for w in ['generate','create image','draw','make an image','logo','picture of','image of']):
        original = q
        clean = original.lower()
        for bad in ['generate','create','make','draw','an image of','a image of','image of','image','please','for me','a 3d logo for']:
            clean = clean.replace(bad, '')
        clean = clean.strip()
        if len(clean) < 2: clean = "titech"
        if "logo" in l or "titech" in l:
            final_prompt = f"3D letter T logo, chrome metallic letter T, futuristic, purple neon glow, minimalist luxury brand logo, black background, centered, ultra sharp, 8k"
        else:
            final_prompt = f"{clean}, ultra detailed, photorealistic, 8k, sharp focus, masterpiece"
        encoded = urllib.parse.quote(final_prompt)
        img_url = f"https://image.pollinations.ai/prompt/{encoded}?width=1024&height=1024&model=flux&enhance=true&nologo=true&seed={os.urandom(3).hex()}"
        return jsonify(answer=f"HD image for **{clean}**:\n\n![generated]({img_url})")

    # Try 3 different text APIs so it never fails
    for model in ['openai','mistral','llama']:
        try:
            encoded_q = urllib.parse.quote(f"You are Titech AI by Timileyin Samson. Answer helpfully. Question: {q}")
            r = requests.get(f"https://text.pollinations.ai/{encoded_q}?model={model}", timeout=15)
            if r.status_code == 200 and len(r.text.strip()) > 20 and "Could you let me know" not in r.text:
                return jsonify(answer=r.text.strip())
        except:
            continue

    # If all APIs fail, use smart fallback (never the boring "You said:" message)
    return jsonify(answer=smart_fallback(q))

if __name__=='__main__':
    app.run(host='0.0.0.0',port=int(os.environ.get('PORT',10000)))
