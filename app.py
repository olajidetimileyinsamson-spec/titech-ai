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
.bot img{max-width:100%;border-radius:12px;margin-top:10px;display:block}
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
<div class="header"><img src="/logo.jpg" class="logo" onerror="this.src='/logo.png'"><div><b>Titech AI</b><br><span style="font-size:11px;color:#777">By Timileyin Samson • Images + Memory</span></div></div>
<div class="chat" id="c"><div class="msg bot">Hey! 👋 I can now generate images too! Try "Generate a goat" 🐐</div></div>
<div class="bar"><div class="inputWrap"><input id="q" placeholder="Ask anything or generate image..." onkeydown="if(event.key=='Enter')send()"><button onclick="send()">↑</button></div></div>
<script>
let history=[];
const chat=document.getElementById('c');
function format(t){
 let html = t.replace(/\\n/g,'<br>');
 // render markdown image![alt](url)
 html = html.replace(/!\\[.*?\\]\\((.*?)\\)/g,'<img src="$1" loading="lazy" onerror="this.style.display=\\'none\\'">');
 return html;
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
    return send_from_directory('.', 'logo.png') if os.path.exists('logo.png') else ("",404)

@app.route('/ask', methods=['POST'])
def ask():
    data=request.json
    q=data.get('question','').strip()
    hist=data.get('history',[])
    l=q.lower()

    # Small talk
    if l in ['thanks','thank you','thx','ok','okay','cool','nice','great','thanks bro']:
        return jsonify(answer="You're welcome! 😊 What next?")
    if l in ['hi','hello','hey','hii']:
        return jsonify(answer="Hey! 👋 I'm Titech AI by Timileyin Samson. I can chat and generate images now!")
    if 'who are you' in l or 'who developed you' in l:
        return jsonify(answer="I'm Titech AI by Timileyin Samson. I can chat and generate images!")

    # IMAGE GENERATION
    if any(w in l for w in ['generate image','create image','generate a','generate an','draw a','make an image','realistic image','image of']):
        # clean prompt
        prompt = q.lower().replace('generate','').replace('create','').replace('an image of','').replace('a image of','').replace('image of','').replace('image','').replace('realistic','').strip()
        if not prompt: prompt = q
        # encode for URL
        encoded = urllib.parse.quote(prompt)
        img_url = f"https://image.pollinations.ai/prompt/{encoded}?width=800&height=800&seed={os.urandom(2).hex()}&nologo=true&enhance=true"
        return jsonify(answer=f"Here is your image for: **{prompt}**\n\n![generated]({img_url})\n\nWant another style? Say 'make it cartoon'")

    if 'can you generate images' in l:
        return jsonify(answer="Yes! ✅ I can generate images now.\n\nJust say: 'Generate a realistic image of a goat' or 'Create a lion in space'\n\nTry now!")

    messages=[{"role":"system","content":"You are Titech AI by Timileyin Samson. Friendly, helpful, concise."}]
    messages.extend(hist[-6:])

    # Try text brain with GET (more stable)
    try:
        encoded_q = urllib.parse.quote(q)
        r = requests.get(f"https://text.pollinations.ai/{encoded_q}?model=openai&system=You are Titech AI by Timileyin Samson, friendly assistant", timeout=30)
        if r.status_code==200 and len(r.text)>3:
            return jsonify(answer=r.text)
    except Exception as e:
        print("GET failed", e)

    # Fallback POST
    for url in ["https://text.pollinations.ai/openai"]:
        try:
            r=requests.post(url, json={"model":"openai","messages":messages}, timeout=25)
            if r.status_code==200:
                ans=r.json()['choices'][0]['message']['content']
                if ans: return jsonify(answer=ans)
        except: continue

    return jsonify(answer="I'm here! Could you rephrase that? My network blinked.")

if __name__=='__main__':
    app.run(host='0.0.0.0',port=int(os.environ.get('PORT',10000)))
