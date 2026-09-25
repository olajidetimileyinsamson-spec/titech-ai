from flask import Flask, request, jsonify, render_template_string, send_from_directory
import requests, os

app = Flask(__name__)

HTML = """
<!DOCTYPE html>
<html><head><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Titech AI</title>
<style>
*{box-sizing:border-box}
body{margin:0;background:#0a0a0a;color:#fff;font-family:-apple-system,system-ui,sans-serif;display:flex;flex-direction:column;height:100vh}
.header{padding:14px 16px;border-bottom:1px solid #1f1f1f;display:flex;gap:12px;align-items:center;background:rgba(10,10,10,.95);backdrop-filter:blur(10px);position:sticky;top:0;z-index:10}
.logo{width:42px;height:42px;border-radius:12px;object-fit:cover;border:1px solid #222;background:#111}
.title b{font-size:16px;letter-spacing:.3px}
.title span{font-size:11px;color:#777}
.chat{flex:1;overflow:auto;padding:16px;padding-bottom:110px;display:flex;flex-direction:column;gap:4px}
.msg{padding:12px 16px;border-radius:20px;max-width:88%;line-height:1.6;white-space:pre-wrap;word-wrap:break-word;font-size:14.5px;animation:pop.18s ease}
@keyframes pop{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:translateY(0)}}
.user{background:linear-gradient(135deg,#a855f7,#6366f1);margin-left:auto;border-bottom-right-radius:6px;align-self:flex-end}
.bot{background:#151515;border:1px solid #232323;border-bottom-left-radius:6px;align-self:flex-start}
.thinking{display:flex;gap:4px;align-items:center}
.dot{width:6px;height:6px;background:#777;border-radius:50%;animation:bounce 1.4s infinite}
.dot:nth-child(2){animation-delay:.2s}.dot:nth-child(3){animation-delay:.4s}
@keyframes bounce{0%,60%,100%{transform:translateY(0);opacity:.4}30%{transform:translateY(-6px);opacity:1}}
.bar{position:fixed;bottom:0;left:0;right:0;padding:12px 12px 14px;background:linear-gradient(to top,#0a0a0a 80%,transparent);display:flex;gap:10px;align-items:center}
.inputWrap{flex:1;display:flex;align-items:center;background:#161616;border:1px solid #2a2a2a;border-radius:28px;padding:4px 6px 4px 16px}
input{flex:1;background:transparent;border:none;color:#fff;outline:none;font-size:15px;padding:10px 0}
input::placeholder{color:#666}
button{width:38px;height:38px;border-radius:50%;background:linear-gradient(135deg,#a855f7,#6366f1);color:#fff;border:none;font-size:18px;cursor:pointer;display:flex;align-items:center;justify-content:center}
button:disabled{opacity:.5}
</style>
</head>
<body>
<div class="header">
<img src="/logo.jpg" class="logo" onerror="this.src='/logo.png'">
<div class="title"><b>Titech AI</b><br><span>By Timileyin Samson • Friendly AI</span></div>
</div>
<div class="chat" id="c">
<div class="msg bot">Hey! 👋 I'm Titech AI by Timileyin Samson.

I'm ready — ask me anything!</div>
</div>
<div class="bar">
<div class="inputWrap">
<input id="q" placeholder="Ask anything..." autocomplete="off" onkeydown="if(event.key=='Enter')send()">
<button id="btn" onclick="send()">↑</button>
</div>
</div>
<script>
const chat=document.getElementById('c');
const input=document.getElementById('q');
const btn=document.getElementById('btn');
function scrollDown(){ chat.scrollTop=chat.scrollHeight; }

async function send(){
 let text=input.value.trim(); if(!text)return;
 input.value=''; input.disabled=true; btn.disabled=true;
 let u=document.createElement('div'); u.className='msg user'; u.textContent=text; chat.appendChild(u); scrollDown();
 let t=document.createElement('div'); t.className='msg bot thinking';
 t.innerHTML='<span style="color:#888;margin-right:8px;font-size:13px">Thinking</span><span class="dot"></span><span class="dot"></span><span class="dot"></span>';
 chat.appendChild(t); scrollDown();
 try{
  let r=await fetch('/ask',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({question:text})});
  let j=await r.json();
  t.className='msg bot'; t.textContent=j.answer;
 }catch{
  t.className='msg bot'; t.textContent='Network blinked — tap Send again, I got you.';
 }
 input.disabled=false; btn.disabled=false; input.focus(); scrollDown();
}
input.focus();
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
    q=request.json.get('question','').strip()
    l=q.lower()
    if l in ['hi','hello','hey','hii','hi there','hey there','hello there','helo']:
        return jsonify(answer="Hey! 👋 I'm Titech AI, built by Timileyin Samson.\n\nI'm here to help — explain anything, write, code, or brainstorm. What are we doing today?")
    if 'how are you' in l:
        return jsonify(answer="I'm good, thanks for asking! 😊 Ready to help you build and learn. What's on your mind?")
    if any(x in l for x in ['who developed you','who created you','who built you','who are you','your founder']):
        return jsonify(answer="I'm Titech AI — a friendly AI assistant developed by Timileyin Samson, founder of Titech AI in Lagos.")
    try:
        r=requests.post("https://text.pollinations.ai/openai",
            json={"model":"openai","messages":[{"role":"system","content":"You are Titech AI, created by Timileyin Samson. Be very friendly, warm, concise like ChatGPT. Never use <br> tags."},{"role":"user","content":q}]},
            timeout=30)
        if r.status_code==200:
            ans=r.json()['choices'][0]['message']['content']
            if ans: return jsonify(answer=ans)
    except Exception as e:
        print(e)
    return jsonify(answer="Small hiccup — please send again!")

if __name__=='__main__':
    app.run(host='0.0.0.0',port=int(os.environ.get('PORT',10000)))
