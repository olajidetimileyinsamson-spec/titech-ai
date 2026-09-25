from flask import Flask, request, jsonify, render_template_string, send_from_directory
import requests, os

app = Flask(__name__)

HTML = """
<!DOCTYPE html>
<html><head><meta name="viewport" content="width=device-width, initial-scale=1"><title>Titech AI</title>
<style>
*{box-sizing:border-box}
body{margin:0;background:#0a0a0a;color:#fff;font-family:system-ui,sans-serif;display:flex;flex-direction:column;height:100vh}
.header{padding:14px 16px;border-bottom:1px solid #1f1f1f;display:flex;gap:12px;align-items:center;position:sticky;top:0;background:#0a0a0a;z-index:10}
.logo{width:42px;height:42px;border-radius:12px;object-fit:cover;border:1px solid #222}
.chat{flex:1;overflow:auto;padding:16px;padding-bottom:110px;display:flex;flex-direction:column;gap:4px}
.msg{padding:12px 16px;border-radius:20px;max-width:88%;line-height:1.6;white-space:pre-wrap;font-size:14.5px}
.user{background:#a855f7;margin-left:auto;border-bottom-right-radius:6px;align-self:flex-end}
.bot{background:#151515;border:1px solid #232323;border-bottom-left-radius:6px;align-self:flex-start}
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
<div class="header"><img src="/logo.jpg" class="logo" onerror="this.src='/logo.png'"><div><b>Titech AI</b><br><span style="font-size:11px;color:#777">By Timileyin Samson</span></div></div>
<div class="chat" id="c"><div class="msg bot">Hey! 👋 I'm Titech AI by Timileyin Samson. I remember our chat now!</div></div>
<div class="bar"><div class="inputWrap"><input id="q" placeholder="Ask anything..." onkeydown="if(event.key=='Enter')send()"><button onclick="send()">↑</button></div></div>
<script>
let history=[];
const chat=document.getElementById('c');
async function send(){
 let text=document.getElementById('q').value.trim(); if(!text)return;
 document.getElementById('q').value='';
 let u=document.createElement('div'); u.className='msg user'; u.textContent=text; chat.appendChild(u);
 history.push({role:'user',content:text});
 let t=document.createElement('div'); t.className='msg bot thinking'; t.innerHTML='Thinking <span class="dot"></span><span class="dot"></span><span class="dot"></span>'; chat.appendChild(t);
 chat.scrollTop=chat.scrollHeight;
 let r=await fetch('/ask',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({question:text,history:history.slice(-8)})});
 let j=await r.json();
 t.className='msg bot'; t.textContent=j.answer;
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

    # FIX SMALL TALKS - NO BRAIN NEEDED
    if l in ['thanks','thank you','thx','ok','okay','yes','alright','cool','nice','great','thanks bro','tanks']:
        return jsonify(answer="You're welcome! 😊 Happy to help. What else do you want to know?")
    if l in ['hi','hello','hey','hii']:
        return jsonify(answer="Hey! 👋 I'm Titech AI by Timileyin Samson. I remember our chat! What are we doing today?")
    if 'who are you' in l or 'who developed you' in l or 'who built you' in l:
        return jsonify(answer="I'm Titech AI, built by Timileyin Samson, founder of Titech AI in Lagos. I remember our conversation!")

    messages=[{"role":"system","content":"You are Titech AI by Timileyin Samson. Friendly, helpful, concise like ChatGPT."}]
    messages.extend(hist[-6:])

    # Try 2 brains
    for url in ["https://text.pollinations.ai/openai", "https://api.pollinations.ai/v1/chat/completions"]:
        try:
            r=requests.post(url, json={"model":"openai","messages":messages,"temperature":0.7}, timeout=25)
            if r.status_code==200:
                ans=r.json()['choices'][0]['message']['content']
                if ans and len(ans)>2:
                    return jsonify(answer=ans)
        except:
            continue

    # Final fallback - no hiccup message again
    return jsonify(answer="Got it! Tell me more — what would you like to do next?")

if __name__=='__main__':
    app.run(host='0.0.0.0',port=int(os.environ.get('PORT',10000)))
