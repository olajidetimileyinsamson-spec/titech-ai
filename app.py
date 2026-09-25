from flask import Flask, request, jsonify, render_template_string, send_from_directory
import requests, os, urllib.parse, random
app = Flask(__name__)

def get_html():
    return "<!DOCTYPE html><html><head><meta name='viewport' content='width=device-width, initial-scale=1'><title>Titech AI</title><link rel='manifest' href='/manifest.json'><meta name='theme-color' content='#00a6ff'><link rel='icon' href='/logo.jpg'><style>*{box-sizing:border-box}body{margin:0;background:#0a0a0a;color:#fff;font-family:system-ui,sans-serif;display:flex;flex-direction:column;height:100vh}.header{padding:14px 16px;border-bottom:1px solid #1f1f1f;display:flex;gap:12px;align-items:center}.logo{width:42px;height:42px;border-radius:12px;object-fit:cover;border:1px solid #222}.chat{flex:1;overflow:auto;padding:16px;padding-bottom:110px;display:flex;flex-direction:column;gap:8px}.msg{padding:12px 16px;border-radius:20px;max-width:88%;line-height:1.6;white-space:pre-wrap;font-size:14.5px;word-wrap:break-word}.user{background:#00a6ff;margin-left:auto;border-bottom-right-radius:6px;align-self:flex-end;color:#fff}.bot{background:#151515;border:1px solid #232323;border-bottom-left-radius:6px;align-self:flex-start}.bot img{max-width:100%;border-radius:12px;margin-top:10px;display:block}.thinking{display:flex;gap:6px;align-items:center;color:#888}.dot{width:6px;height:6px;background:#777;border-radius:50%;animation:b 1.4s infinite}.dot:nth-child(2){animation-delay:.2s}.dot:nth-child(3){animation-delay:.4s}@keyframes b{0%,60%,100%{transform:translateY(0);opacity:.4}30%{transform:translateY(-5px);opacity:1}}.bar{position:fixed;bottom:0;left:0;right:0;padding:12px;background:#0a0a0a;display:flex;gap:10px}.inputWrap{flex:1;display:flex;background:#161616;border:1px solid #2a2a2a;border-radius:28px;padding:4px 6px 4px 16px}input{flex:1;background:transparent;border:none;color:#fff;outline:none;font-size:15px;padding:10px 0}button{width:38px;height:38px;border-radius:50%;background:#00a6ff;color:#fff;border:none;cursor:pointer;font-weight:bold}</style></head><body><div class='header'><img src='/logo.jpg' class='logo'><div><b>Titech AI</b><br><span style='font-size:11px;color:#777'>By Timileyin Samson - Electric Blue</span></div></div><div class='chat' id='c'><div class='msg bot'>Electric Blue Ready! Install me from browser menu.</div></div><div class='bar'><div class='inputWrap'><input id='q' placeholder='Ask anything...' onkeydown=\"if(event.key=='Enter')send()\"><button onclick='send()'>&#8593;</button></div></div><script>if('serviceWorker' in navigator){navigator.serviceWorker.register('/sw.js')}let h=[];const chat=document.getElementById('c');function fmt(t){let x=t.replace(/\\n/g,'<br>');x=x.replace(/!\\[.*?\\]\\((.*?)\\)/g,'<img src=\"$1\" loading=\"lazy\"><br><a href=\"$1\" target=\"_blank\" style=\"color:#00a6ff;font-size:12px\">Download</a>');return x;}async function send(){let q=document.getElementById('q').value.trim();if(!q)return;document.getElementById('q').value='';let u=document.createElement('div');u.className='msg user';u.textContent=q;chat.appendChild(u);h.push({role:'user',content:q});let t=document.createElement('div');t.className='msg bot thinking';t.innerHTML='Thinking <span class=\"dot\"></span><span class=\"dot\"></span><span class=\"dot\"></span>';chat.appendChild(t);chat.scrollTop=chat.scrollHeight;let r=await fetch('/ask',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({question:q,history:h.slice(-8)})});let j=await r.json();t.className='msg bot';t.innerHTML=fmt(j.answer);h.push({role:'assistant',content:j.answer});chat.scrollTop=chat.scrollHeight;}</script></body></html>"

@app.route('/')
def home():
    return render_template_string(get_html())

@app.route('/logo.jpg')
def logo_jpg():
    return send_from_directory('.', 'logo.jpg')

@app.route('/manifest.json')
def manifest():
    return jsonify({"name": "Titech AI","short_name": "Titech AI","start_url": "/","display": "standalone","background_color": "#0a0a0a","theme_color": "#00a6ff","icons": [{"src": "/logo.jpg","sizes": "192x192","type": "image/jpeg"},{"src": "/logo.jpg","sizes": "512x512","type": "image/jpeg"}]})

@app.route('/sw.js')
def sw():
    js = "self.addEventListener('install',e=>self.skipWaiting());self.addEventListener('activate',e=>self.clients.claim());"
    return js, 200, {'Content-Type': 'application/javascript'}

@app.route('/ask', methods=['POST'])
def ask():
    data = request.json
    q = data.get('question','').strip()
    l = q.lower()
    if not q:
        return jsonify(answer="Ask me!")
    if l in ['hi','hello','hey']:
        return jsonify(answer="Hey! I am Titech AI by Timileyin Samson. Electric blue mode ON!")
    if 'who are you' in l:
        return jsonify(answer="I am Titech AI built by Timileyin Samson - electric blue edition!")
    if any(w in l for w in ['generate','create image','draw','logo','picture of','image of']):
        clean = q.lower()
        for bad in ['generate','create','make','draw','an image of','image of','image','please','logo for','a 3d logo for']:
            clean = clean.replace(bad,'')
        clean = clean.strip() or "titech"
        prompt = "3D letter T logo chrome metallic electric blue neon glow minimalist luxury black background 8k" if "titech" in clean or "logo" in l else clean + ", ultra detailed photorealistic 8k masterpiece electric blue theme"
        url = "https://image.pollinations.ai/prompt/" + urllib.parse.quote(prompt) + "?width=1024&height=1024&model=flux&enhance=true&nologo=true&seed=" + str(random.randint(1,999999))
        return jsonify(answer="HD image for **" + clean + "**:\n\n![gen](" + url + ")")
    try:
        r = requests.post("https://text.pollinations.ai/openai", json={"model":"openai","messages":[{"role":"system","content":"You are Titech AI by Timileyin Samson."},{"role":"user","content":q}]}, timeout=20)
        if r.status_code == 200:
            j = r.json()
            if 'choices' in j and j['choices']:
                ans = j['choices'][0]['message']['content']
                if len(ans) > 20:
                    return jsonify(answer=ans.strip())
    except:
        pass
    return jsonify(answer=q + " - Tell me more for detailed answer.")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT',10000)))
