import os
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from groq import Groq
from tavily import TavilyClient
from supabase import create_client

app = Flask(__name__)
CORS(app)

groq_client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
tavily_client = TavilyClient(api_key=os.environ.get("TAVILY_API_KEY")) if os.environ.get("TAVILY_API_KEY") else None

supabase_url = os.environ.get("SUPABASE_URL")
supabase_key = os.environ.get("SUPABASE_KEY")
supabase = create_client(supabase_url, supabase_key) if supabase_url and supabase_key else None

@app.route("/logo.png")
def logo():
    try: return send_from_directory(".", "logo.png")
    except: return "",404

@app.route("/debug")
def debug():
    return jsonify({"SUPABASE_URL": bool(supabase_url), "SUPABASE_KEY_long": bool(supabase_key and len(supabase_key) > 100), "GROQ_KEY": bool(os.environ.get("GROQ_API_KEY")), "MODEL": "openai/gpt-oss-120b"})

@app.route("/")
def home():
    s_url = supabase_url or ""
    s_key = supabase_key or ""
    return f"""
<!DOCTYPE html><html><head><title>Titech AI</title><meta name="viewport" content="width=device-width, initial-scale=1">
<script src="https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2"></script>
<style>
*{{box-sizing:border-box;font-family:system-ui}}
body{{margin:0;background:#101014;color:#fff;height:100vh;display:flex;flex-direction:column;overflow:hidden}}
#welcome{{position:fixed;inset:0;z-index:100;background:#0e0e12;display:flex;flex-direction:column;align-items:center;justify-content:center}}
#welcome.hide{{display:none}}
.wel-pattern{{position:absolute;inset:0;opacity:0.08;background-image: radial-gradient(circle at 1px 1px, #fff 1px, transparent 0);background-size:30px 30px}}
.wel-center{{display:flex;flex-direction:column;align-items:center;gap:18px;z-index:2;margin-top:-40px;width:90%;max-width:360px}}
.wel-logo{{width:90px;height:90px;border-radius:22px;background:linear-gradient(135deg,#a855f7,#5b21b6);display:grid;place-items:center}}
.wel-logo img{{width:70px;height:70px;border-radius:16px}}
.wel-greet{{font-size:32px;font-weight:800}}
.wel-sub{{color:#9ca3af;font-size:14px;margin-top:-10px}}
.login-box{{display:flex;flex-direction:column;gap:10px;width:100%;margin-top:15px}}
.login-box input{{padding:13px 16px;border-radius:14px;border:1px solid #27272a;background:#18181b;color:#fff;outline:none}}
.login-box button{{padding:13px;border-radius:14px;border:none;background:#fff;color:#000;font-weight:700;cursor:pointer}}
#topbar{{display:flex;justify-content:space-between;align-items:center;padding:12px 16px;background:#18181b;border-bottom:1px solid #27272a}}
#chat{{flex:1;overflow-y:auto;padding:16px;display:flex;flex-direction:column;gap:14px;background:#101014}}
.bubble-wrap{{max-width:85%;display:flex;flex-direction:column;gap:6px}}
.bubble-wrap.user{{align-self:flex-end;align-items:flex-end}}
.bubble-wrap.ai{{align-self:flex-start;align-items:flex-start}}
.msg{{padding:14px 16px;border-radius:20px;line-height:1.6;font-size:14.5px;white-space:pre-wrap}}
.user.msg{{background:linear-gradient(135deg,#0b84ff,#0066ff);border-bottom-right-radius:6px}}
.ai.msg{{background:#2a2c38;border:1px solid #3a3c4f;border-bottom-left-radius:6px}}
.msg img{{max-width:100%;border-radius:12px;margin-top:10px}}
.actions{{display:flex;gap:6px;padding:0 4px}}
.c-btn{{background:#22232a;border:1px solid #333542;color:#9aa0b3;border-radius:12px;padding:4px 9px;font-size:11px;cursor:pointer}}
#bar{{position:sticky;bottom:0;background:#18181b;border-top:1px solid #27272a;padding:10px;display:flex;gap:8px;align-items:center}}
#bar input{{flex:1;background:#27272a;border:none;color:#fff;padding:14px 18px;border-radius:28px;outline:none}}
.send{{width:42px;height:42px;border-radius:50%;background:#22c55e;border:none;font-weight:bold;cursor:pointer}}
#settings{{position:fixed;inset:0;z-index:200;background:rgba(0,0,0,0.6);display:none;align-items:center;justify-content:center}}
#settings.show{{display:flex}}
.set-box{{background:#18181b;border:1px solid #27272a;border-radius:20px;width:90%;max-width:380px;padding:20px;display:flex;flex-direction:column;gap:14px}}
.set-row{{display:flex;justify-content:space-between;align-items:center;padding:12px;background:#27272a;border-radius:12px;font-size:14px}}
.set-btn{{padding:12px;border-radius:12px;border:none;font-weight:600;cursor:pointer}}
.danger{{background:#ef4444;color:#fff}}
</style></head>
<body>

<div id="welcome">
  <div class="wel-pattern"></div>
  <div class="wel-center">
    <div class="wel-logo"><img src="/logo.png" onerror="this.src='https://cdn-icons-png.flaticon.com/512/4712/4712109.png'"></div>
    <div class="wel-greet">Hi, Titech</div>
    <div class="wel-sub" id="timeGreet">Good morning</div>
    <div class="login-box">
      <input id="email" placeholder="Email">
      <input id="pass" type="password" placeholder="Password">
      <button onclick="doLogin()">Continue</button>
      <small id="loginStatus" style="text-align:center;color:#9ca3af"></small>
      <small onclick="enterChat()" style="text-align:center;color:#555;cursor:pointer">Skip → offline only</small>
    </div>
  </div>
</div>

<div id="topbar">
  <div style="display:flex;align-items:center;gap:10px"><div class="wel-logo" style="width:36px;height:36px;border-radius:10px"><img src="/logo.png" style="width:26px;height:26px" onerror="this.src='https://cdn-icons-png.flaticon.com/512/4712/4712109.png'"></div><b>Titech AI</b></div>
  <div style="display:flex;gap:10px"><span onclick="openSettings()" style="cursor:pointer;font-size:20px">⚙️</span></div>
</div>

<div id="chat"></div>

<div id="bar">
  <input id="input" placeholder="Ask Titech AI 120b..." onkeypress="if(event.key==='Enter')send()">
  <button class="send" onclick="send()">➤</button>
</div>

<div id="settings" onclick="if(event.target.id==='settings') closeSettings()">
  <div class="set-box">
    <h3>Settings</h3>
    <div class="set-row"><span>Account (Gmail)</span><span id="setEmail" style="color:#22c55e;font-weight:700;max-width:180px;overflow:hidden;text-overflow:ellipsis">Not logged in</span></div>
    <div class="set-row"><span>Model</span><span>gpt-oss-120b</span></div>
    <div class="set-row"><span>Greeting</span><span id="setGreet">-</span></div>
    <button class="set-btn" onclick="clearChat()">Clear All Chats</button>
    <button class="set-btn danger" onclick="doLogout()">Logout</button>
    <button class="set-btn" style="background:#27272a;color:#fff" onclick="closeSettings()">Close</button>
  </div>
</div>

<script>
const CHAT_KEY='titech_ai_forever_chat';
const supaUrl="{s_url}"; const supaKey="{s_key}";
const supabaseClient=(supaUrl && supaKey)? supabase.createClient(supaUrl, supaKey) : null;
let history=JSON.parse(localStorage.getItem(CHAT_KEY)||'[]');
const chatDiv=document.getElementById('chat');
const welcome=document.getElementById('welcome');

// NO GOOD NIGHT - ONLY MORNING, AFTERNOON, EVENING
function setGreeting(){{
  let h=new Date().getHours(); let greet="Good morning", emoji="☀️";
  if(h>=12 && h<17){{greet="Good afternoon"; emoji="🌤️"}}
  else if(h>=17){{greet="Good evening"; emoji="🌙"}} // 5pm to 11:59pm = evening, no night
  document.getElementById('timeGreet').innerText=greet+" "+emoji;
  document.getElementById('setGreet').innerText=greet+" "+emoji;
}}
setGreeting();

function enterChat(){{ welcome.classList.add('hide'); }}
function openSettings(){{ document.getElementById('settings').classList.add('show'); checkSession(); }}
function closeSettings(){{ document.getElementById('settings').classList.remove('show'); }}
function clearChat(){{ if(confirm('Clear all memory?')){{ history=[]; localStorage.removeItem(CHAT_KEY); renderAll(); closeSettings(); }} }}
async function doLogout(){{ if(supabaseClient) await supabaseClient.auth.signOut(); localStorage.removeItem(CHAT_KEY); history=[]; location.reload(); }}

async function checkSession(){{
  if(!supabaseClient) return;
  let {{data}} = await supabaseClient.auth.getSession();
  let email = data.session?.user?.email;
  if(email){{
    document.getElementById('setEmail').innerText=email;
    document.getElementById('setEmail').style.color="#22c55e";
  }} else {{
    document.getElementById('setEmail').innerText="Not logged in (Offline)";
  }}
}}
checkSession();

function persist(){{localStorage.setItem(CHAT_KEY,JSON.stringify(history));}}
function renderAll(){{
  chatDiv.innerHTML='';
  history.forEach((item,idx)=>{{
    let isUser=item.role==='user'; let img=item.image?`<img src="${{item.image}}">`:'';
    let actions=`<div class="actions"><button class="c-btn" onclick="editMsg(${{idx}})">✏️ Edit</button><button class="c-btn" onclick="deleteMsg(${{idx}})">🗑️ Del</button><button class="c-btn" onclick="copyText(${{idx}})">Copy</button></div>`;
    chatDiv.innerHTML+=`<div class="bubble-wrap ${{isUser?'user':'ai'}}"><div class="${{isUser?'user':'ai'}} msg">${{item.content}}${{img}}</div>${{actions}}</div>`;
  }});
  chatDiv.scrollTop=chatDiv.scrollHeight;
}}
function copyText(i){{navigator.clipboard.writeText(history[i].content);}}
function deleteMsg(i){{history.splice(i,1);persist();renderAll();}}
function editMsg(i){{let n=prompt('Edit:',history[i].content); if(n){{history[i].content=n;persist();renderAll();}}}}
if(history.length>0){{welcome.classList.add('hide'); renderAll();}}

async function doLogin(){{
  let email=document.getElementById('email').value.trim();
  let pass=document.getElementById('pass').value.trim();
  if(!email ||!pass){{ document.getElementById('loginStatus').innerText='Enter email & password'; return; }}
  if(!supabaseClient){{ document.getElementById('loginStatus').innerText='Supabase not set'; setTimeout(enterChat,800); return; }}
  document.getElementById('loginStatus').innerText='Loading...';
  let {{data, error}} = await supabaseClient.auth.signInWithPassword({{email, password: pass}});
  if(error){{
    let {{data: sData, error: sErr}} = await supabaseClient.auth.signUp({{email, password: pass}});
    if(sErr){{ document.getElementById('loginStatus').innerText=sErr.message; return; }}
    data=sData;
  }}
  // SHOW GMAIL UNDER SETTINGS
  document.getElementById('setEmail').innerText=data.user?.email || email;
  document.getElementById('loginStatus').innerText='Login successful! ✅';
  setTimeout(enterChat,600);
}}

async function send(){{
  let input=document.getElementById('input');let text=input.value.trim();if(!text)return;
  enterChat(); input.value='';
  history.push({{role:'user',content:text}});persist();renderAll();
  let low=text.toLowerCase();
  let isImg=(low.includes('generate')||low.includes('create')||low.includes('make')) && (low.includes('image')||low.includes('picture')||low.includes('photo')||low.includes('pic'));
  if(isImg){{
    let prompt=text.replace(/generate.*?(image|picture|photo|pic) of|create.*?(image|picture|photo|pic) of|make.*?(image|picture|photo|pic) of|generate.*?(image|picture|photo|pic)|create.*?(image|picture|photo|pic)|make.*?(image|picture|photo|pic)|image of|picture of|photo of|pic of/gi,'').trim()||'cute dog';
    let url=`https://image.pollinations.ai/prompt/${{encodeURIComponent(prompt+', high quality') }}?seed=${{Date.now()}}&nologo=true`;
    history.push({{role:'assistant',content:`Generated: "${{prompt}}"`,image:url}});persist();renderAll();return;
  }}
  try{{
    let res=await fetch('/chat',{{method:'POST',headers:{{'Content-Type':'application/json'}},body:JSON.stringify({{message:text,history:history.slice(-12)}})}});
    let data=await res.json();history.push({{role:'assistant',content:data.reply}});persist();renderAll();
  }}catch(e){{history.push({{role:'assistant',content:'Network error 😅'}});persist();renderAll();}}
}}
</script></body></html>
"""

@app.route("/chat", methods=["POST"])
def chat():
    req=request.get_json()
    user_msg=req.get("message","")
    history=req.get("history",[])
    context=""
    if tavily_client:
        try:
            s=tavily_client.search(user_msg, max_results=2)
            context="\\n".join([r["content"][:400] for r in s["results"]])
        except: pass
    sys_prompt=f"You are Titech AI by Olajide Timilehin Samson. Facts: {context}."
    msgs=[{"role":"system","content":sys_prompt}]
    for h in history[-10:]:
        if not h.get('image'): msgs.append({"role":h['role'],"content":h['content'][:1200]})
    msgs.append({"role":"user","content":user_msg})
    comp=groq_client.chat.completions.create(model="openai/gpt-oss-120b", messages=msgs, temperature=0.3, max_tokens=2000)
    return jsonify({"reply":comp.choices[0].message.content})

if __name__=="__main__":
    app.run(host="0.0.0.0", port=10000)
