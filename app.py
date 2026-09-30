import os, json
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from groq import Groq
from supabase import create_client

app = Flask(__name__)
CORS(app)

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPA_KEY")
FEEDBACK_EMAIL = "olajidetimileyinsamson@gmail.com"

groq_client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None
supabase = None
if SUPABASE_URL and SUPABASE_KEY:
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    except:
        pass

@app.route('/logo.png')
def logo():
    return send_from_directory('.', 'logo.png')

@app.route('/')
def home():
    return """<!DOCTYPE html>
<html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1,user-scalable=no">
<title>Titech AI 🚀</title>
<style>
*{box-sizing:border-box;margin:0;padding:0}html,body{height:100%;width:100%;max-width:100vw;overflow-x:hidden!important}
body{background:#020611;color:#fff;font-family:-apple-system,sans-serif;display:flex;flex-direction:column;height:100dvh;background-image:linear-gradient(rgba(0,242,255,0.07) 1px, transparent 1px),linear-gradient(90deg, rgba(0,242,255,0.07) 1px, transparent 1px);background-size:48px 48px}
.wrap{width:100%;max-width:400px;margin:0 auto;display:flex;flex-direction:column;height:100dvh;position:relative}
.header{margin:10px 12px;display:flex;justify-content:space-between;align-items:center;padding:12px 14px;background:rgba(15,22,40,0.9);border:1px solid rgba(0,242,255,0.18);border-radius:18px}
.h-left{display:flex;align-items:center;gap:10px}.logo{width:30px;height:30px;border-radius:8px;background:#0a1328}
.h-title{font-weight:800}.pill{font-size:11px;padding:5px 10px;border-radius:20px;background:rgba(130,255,180,0.12);border:1px solid rgba(130,255,180,0.28);color:#a7ffbf}
.icon-btn{width:30px;height:30px;border-radius:50%;border:1px solid rgba(255,255,255,0.12);background:rgba(255,255,255,0.08);color:#fff;cursor:pointer}
#chat{flex:1;overflow-y:auto;overflow-x:hidden!important;padding:10px 12px 130px 12px;display:flex;flex-direction:column;gap:14px}
.ai-wrap{max-width:86%;align-self:flex-start}.ai{background:linear-gradient(135deg,#00d4ff,#7a3dff);padding:14px 16px;border-radius:18px 18px 18px 4px;font-size:14px;line-height:1.5;word-break:break-word;overflow-wrap:anywhere;white-space:pre-wrap}
.user-wrap{max-width:82%;align-self:flex-end;display:flex;flex-direction:column;align-items:flex-end;width:100%}.user{background:rgba(255,255,255,0.09);border:1px solid rgba(0,242,255,0.22);padding:12px 16px;border-radius:18px 18px 4px 18px;font-size:14px;width:100%;word-break:break-word;overflow-wrap:anywhere;white-space:pre-wrap}
.actions{display:flex;gap:6px;margin-top:5px}.actions button{background:rgba(255,255,255,0.08);border:1px solid rgba(255,255,255,0.1);color:#9bb8c5;font-size:10px;padding:3px 8px;border-radius:8px}
.bottom{position:fixed;bottom:0;left:50%;transform:translateX(-50%);width:100%;max-width:400px;padding:10px 12px;background:linear-gradient(to top,#020611 90%,transparent)}
.input-bar{display:flex;align-items:center;gap:8px;background:rgba(15,22,40,0.95);border:1px solid rgba(0,242,255,0.18);border-radius:28px;padding:6px 6px 6px 14px}
.input-bar input{flex:1;background:transparent;border:none;color:#fff;outline:none;font-size:14px;min-width:0}.send{width:36px;height:36px;border-radius:50%;border:none;background:radial-gradient(circle at 30% 30%,#00f2ff,#7a3dff);color:#fff}
#settingsModal{display:none;position:fixed;inset:0;z-index:999;background:rgba(0,0,0,0.6);backdrop-filter:blur(10px);align-items:center;justify-content:center;padding:20px}
#settingsModal.show{display:flex}
.settingsBox{width:100%;max-width:320px;background:#0f1628;border:1px solid rgba(0,242,255,0.2);border-radius:20px;padding:18px}
.settingsBox h3{margin-bottom:12px}.opt{display:flex;justify-content:space-between;align-items:center;padding:10px 0;border-bottom:1px solid rgba(255,255,255,0.06)}
.opt select{background:#0a1328;color:#fff;border:1px solid rgba(255,255,255,0.1);border-radius:8px;padding:5px}
.closeBtn{width:100%;margin-top:14px;padding:10px;border-radius:12px;border:none;background:linear-gradient(135deg,#00d4ff,#7a3dff);color:#fff;font-weight:700}
</style></head>
<body><div class="wrap">
<div class="header"><div class="h-left"><img src="logo.png" class="logo" onerror="this.style.display='none'"><div class="h-title">Titech AI 🚀</div></div><div class="h-right"><span id="modePill" class="pill">hype</span><button class="icon-btn" onclick="openSettings()">⚙️</button></div></div>
<div id="chat"><div class="ai-wrap"><div class="ai">Yo! 👋 I be Titech AI 🚀 — ready to help. What you wan do today?</div></div></div>
<div class="bottom"><div class="input-bar"><input id="msg" placeholder="Ask Titech AI 🚀..." onkeypress="if(event.key==='Enter')send()"><button class="send" onclick="send()">↑</button></div></div>
</div>
<div id="settingsModal" onclick="if(event.target==this)closeSettings()"><div class="settingsBox"><h3>⚙️ Settings</h3><div class="opt"><span>Personality</span><select id="pers" onchange="changePers(this.value)"><option value="friendly">Friendly</option><option value="hype" selected>Hype</option><option value="professional">Professional</option><option value="pidgin">Pidgin</option></select></div><div class="opt"><span>Clear Chat</span><button onclick="clearChat()" style="background:#ff3344;border:none;color:#fff;padding:5px 10px;border-radius:8px">Clear</button></div><div class="opt"><span>Developer</span><span style="font-size:11px;color:#9bb8c5">Olajide Timileyin Samson</span></div><div class="opt"><span>Contact</span><span style="font-size:9px;color:#9bb8c5">olajidetimileyinsamson@gmail.com</span></div><button class="closeBtn" onclick="closeSettings()">Close</button></div></div>
<script>
let chat=document.getElementById('chat'), inp=document.getElementById('msg');
let currentPers = localStorage.getItem('titech_pers') || 'hype';
document.getElementById('pers').value=currentPers;
document.getElementById('modePill').innerText=currentPers;
function openSettings(){document.getElementById('settingsModal').classList.add('show')}
function closeSettings(){document.getElementById('settingsModal').classList.remove('show')}
function changePers(v){currentPers=v;localStorage.setItem('titech_pers',v);document.getElementById('modePill').innerText=v;closeSettings()}
function clearChat(){chat.innerHTML='<div class="ai-wrap"><div class="ai">Chat cleared! Yo! 👋 I be Titech AI 🚀 — ready again.</div></div>';closeSettings()}
function add(t,c){let w=document.createElement('div');w.className=c+'-wrap';let d=document.createElement('div');d.className=c;d.innerText=t;let a=document.createElement('div');a.className='actions';a.innerHTML='<button onclick="navigator.clipboard.writeText(this.parentElement.previousElementSibling.innerText)">📋 Copy</button><button onclick="this.closest(\\'.'+c+'-wrap\\').remove()">🗑️</button>';w.appendChild(d);w.appendChild(a);chat.appendChild(w);chat.scrollTop=chat.scrollHeight}
async function send(){let t=inp.value.trim();if(!t)return;add(t,'user');inp.value='';let ty=document.createElement('div');ty.className='ai-wrap';ty.innerHTML='<div class="ai">Thinking...</div>';chat.appendChild(ty);chat.scrollTop=chat.scrollHeight;try{let r=await fetch('/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({message:t,personality:currentPers})});let d=await r.json();ty.remove();add(d.reply||'No reply','ai');}catch{ty.remove();add('Network glitch','ai');}}
</script></body></html>"""

@app.route('/chat', methods=['POST'])
def chat_api():
    data = request.get_json()
    user_msg = data.get('message','').strip()
    personality = data.get('personality','friendly')

    # FIX FOR "Hey" - short greeting, no Hey.com essay
    if user_msg.lower() in ['hey','hi','hello','yo','yo!','hi!','hello!','hey!','yo']:
        return jsonify({"reply": "Yo! 👋 I be Titech AI 🚀, created by Olajide Timileyin Samson. How I fit help you today? No long story, just gist me!"})

    if not groq_client:
        return jsonify({"reply": "Groq key never set for Render."})

    sys_prompt = f"""You are Titech AI 🚀, built by Olajide Timileyin Samson. Contact: {FEEDBACK_EMAIL}.
Personality: {personality} = friendly, hype, small pidgin, ultra concise 2-3 lines max unless user asks for long.
CRITICAL RULES:
- If user says just hey/hi/hello, give SHORT greeting only, DO NOT explain Hey.com email service.
- Never give long tables or Feature/Why you'll love am table unless user explicitly asks for detailed breakdown.
- Keep replies clean, no shift, no wide markdown tables. Use bullet points short.
- You are NOT Hey email, you are Titech AI. (titech-ai-120b model)
"""

    try:
        comp = groq_client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[{"role":"system","content":sys_prompt},{"role":"user","content":user_msg}],
            temperature=0.3,
            max_tokens=800
        )
        reply = comp.choices[0].message.content
        return jsonify({"reply": reply})
    except Exception as e:
        return jsonify({"reply": f"Error: {str(e)}"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT',10000)))
