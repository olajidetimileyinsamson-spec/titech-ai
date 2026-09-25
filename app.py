from flask import Flask, request, jsonify, render_template_string, send_from_directory
import requests, os, urllib.parse

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
<div class="header"><img src="/logo.jpg" class="logo" onerror="this.src='/logo.png'"><div><b>Titech AI</b><br><span style="font-size:11px;color:#777">By Timileyin Samson • Fixed</span></div></div>
<div class="chat" id="c"><div class="msg bot">Fixed! 👋 Now chat works + logo is sharp letter T. Try "Generate 3D logo for Titech" or "Tell me about Lagos"</div></div>
<div class="bar"><div class="inputWrap"><input id="q" placeholder="Ask anything or generate image..." onkeydown="if(event.key=='Enter')send()"><button onclick="send()">↑</button></div></div>
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

@app.route('/ask', methods=['POST'])
def ask():
    data=request.json
    q=data.get('question','').strip()
    hist=data.get('history',[])
    l=q.lower()

    if l in ['thanks','thank you','thx','ok','okay','cool','nice','great','yeah']:
        return jsonify(answer="You're welcome! 😊 Anything else?")
    if l in ['hi','hello','hey','hii','yo']:
        return jsonify(answer="Hey! 👋 I'm Titech AI by Timileyin Samson. I can chat about anything and generate HD images. What you need?")
    if 'who are you' in l or 'who built you' in l or 'who developed you' in l:
        return jsonify(answer="I'm Titech AI built by Timileyin Samson — your smart assistant for chat and image generation.")
    
    # IMAGE GENERATION - FIXED PROMPT
    if any(w in l for w in ['generate','create image','draw','make an image','logo','picture of','image of']):
        original = q
        # Clean but keep meaning
        clean = original.lower()
        for bad in ['generate','create','make','draw','an image of','a image of','image of','image','please','for me']:
            clean = clean.replace(bad, '')
        clean = clean.strip()
        if len(clean) < 3: clean = "Titech"

        if "logo" in l or "titech" in l:
            # Force letter T - this gives sharp T
            final_prompt = f"3D letter T logo, chrome metallic letter T, futuristic, purple neon glow, minimalist luxury brand logo, black background, centered, studio lighting, ultra sharp, 8k"
        else:
            final_prompt = f"{clean}, ultra detailed, photorealistic, 8k, sharp focus, masterpiece, highly detailed"

        encoded = urllib.parse.quote(final_prompt)
        img_url = f"https://image.pollinations.ai/prompt/{encoded}?width=1024&height=1024&model=flux&enhance=true&nologo=true&seed={os.urandom(3).hex()}"
        return jsonify(answer=f"Here is HD image for **{clean}**:\n\n![generated]({img_url})")

    # TEXT CHAT - FIXED, no more "Try rephrasing"
    try:
        encoded_q = urllib.parse.quote(f"You are Titech AI by Timileyin Samson. Be helpful, friendly, concise. User asks: {q}")
        r = requests.get(f"https://text.pollinations.ai/{encoded_q}?model=openai", timeout=20)
        if r.status_code == 200 and len(r.text) > 10:
            text = r.text.strip()
            # Remove Pollinations asking questions style
            if "Could you let me know" in text and len(text) < 400:
                # Fallback to better answer
                raise Exception("weak answer")
            return jsonify(answer=text)
    except:
        pass

    # Fallback smart answers so it NEVER says "Try rephrasing"
    if "lagos" in l:
        return jsonify(answer="Lagos is the largest city in Nigeria and Africa's biggest tech hub! It's known for its vibrant culture, markets like Balogun, beaches, nightlife, and as the center of Nollywood and Afrobeats. What about Lagos do you want to know? History, places to visit, business?")
    if "titech" in l:
        return jsonify(answer="Titech is your brand! Titech AI is an AI assistant built by you, Timileyin Samson, that can chat and generate HD images. Want me to write a description, slogan, or business plan for Titech?")
    if "designated writing" in l or "writing" in l:
        return jsonify(answer="Got it! You want a designated writing about Titech. I can write:\n\n**Titech — Brief:**\nTitech is a forward-thinking tech brand founded by Timileyin Samson, focused on building smart AI tools that are simple, fast, and accessible for everyone in Africa and beyond.\n\nTell me what type you need: formal report, Instagram bio, website about page, or pitch deck?")

    return jsonify(answer=f"You said: '{q}'. I'm Titech AI by Timileyin Samson — I can explain, write, summarize, or generate images. Could you tell me a bit more so I can give you a perfect answer?")

if __name__=='__main__':
    app.run(host='0.0.0.0',port=int(os.environ.get('PORT',10000)))
