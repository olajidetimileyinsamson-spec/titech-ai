import os
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from groq import Groq
from tavily import TavilyClient
from supabase import create_client

app = Flask(__name__)
CORS(app)

groq_client = Groq(api_key=os.environ.get("GROQ_API_KEY")) if os.environ.get("GROQ_API_KEY") else None
tavily_client = TavilyClient(api_key=os.environ.get("TAVILY_API_KEY")) if os.environ.get("TAVILY_API_KEY") else None
supabase_url = os.environ.get("SUPABASE_URL", "")
supabase_key = os.environ.get("SUPABASE_KEY", "")
supabase = create_client(supabase_url, supabase_key) if supabase_url and supabase_key else None

FEEDBACK_GMAIL = "olajidetimileyinsamson@gmail.com"

@app.route("/logo.png")
def logo():
    try: return send_from_directory(".", "logo.png")
    except: return "", 404

@app.route("/debug")
def debug():
    return jsonify({"SUPABASE": bool(supabase), "GROQ": bool(os.environ.get("GROQ_API_KEY")), "TAVILY": bool(tavily_client)})

@app.route("/")
def home():
    html = """
<!DOCTYPE html><html><head><title>Titech AI 🚀</title>
<meta name="viewport" content="width=device-width,initial-scale=1">
<script src="https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2"></script>
<script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
<style>
*{box-sizing:border-box;font-family:system-ui}body{margin:0;background:#101014;color:#fff;height:100vh;display:flex;flex-direction:column;overflow:hidden}
#welcome{position:fixed;inset:0;z-index:100;background:#0e0e12;display:flex;flex-direction:column;align-items:center;justify-content:center;padding:24px}
.wel-logo{width:100px;height:100px;background:#fff;border-radius:22px;display:flex;align-items:center;justify-content:center;margin-bottom:18px}
.wel-logo img{width:72px;height:72px;object-fit:contain;display:block}
.wel-title{font-size:30px;font-weight:800;color:#fff;margin-bottom:6px}
#topbar{display:flex;justify-content:space-between;align-items:center;padding:10px 14px;background:#18181b;border-bottom:1px solid #27272a}
#chat{flex:1;overflow-y:auto;padding:14px;display:flex;flex-direction:column;gap:12px;background:#101014}
.bubble{padding:12px 16px;border-radius:18px;max-width:88%;line-height:1.5;font-size:14.5px}
.user-bubble{align-self:flex-end;background:#3b82f6;color:#fff}
.bot-bubble{align-self:flex-start;background:#1e1e22;color:#e4e4e7}
#bar{position:sticky;bottom:0;background:#18181b;border-top:1px solid #27272a;padding:10px;display:flex;gap:8px}
#bar input{flex:1;background:#27272a;border:none;color:#fff;padding:14px 18px;border-radius:24px;outline:none}
#settings{position:fixed;inset:0;z-index:120;background:rgba(0,0,0,.6);display:none;align-items:center;justify-content:center;padding:20px}
.set-box{background:#18181b;border:1px solid #27272a;border-radius:20px;width:100%;max-width:400px;padding:20px}
.set-row{display:flex;justify-content:space-between;padding:10px 0;border-bottom:1px solid #27272a;font-size:14px}
.set-btn{padding:10px 18px;border-radius:16px;border:1px solid #27272a;background:#27272a;color:#fff;cursor:pointer;margin:6px 6px 0 0}
.danger{background:#ef4444!important;border-color:#ef4444!important}
.perso-btn{padding:16px 18px;border-radius:16px;border:1px solid #27272a;background:#18181b;color:#fff;width:100%;max-width:360px;text-align:left;margin-bottom:10px;cursor:pointer}
#personalityPopup{position:fixed;inset:0;z-index:150;background:#0e0e12;display:none;flex-direction:column;align-items:center;justify-content:center;padding:24px}
</style></head><body>
<div id="welcome">
 <div class="wel-center">
   <div class="wel-logo"><img src="/logo.png"></div>
   <div class="wel-title" id="datetimeGreet">Good Evening</div>
   <div style="color:#a1a1aa;margin-bottom:20px">Titech AI 🚀</div>
   <input id="username" class="wel-input" style="width:100%;padding:14px;border-radius:12px;border:1px solid #27272a;background:#18181b;color:#fff;margin-bottom:10px" placeholder="Username" maxlength="12">
   <input id="email" class="wel-input" style="width:100%;padding:14px;border-radius:12px;border:1px solid #27272a;background:#18181b;color:#fff;margin-bottom:10px" placeholder="Email">
   <input id="password" type="password" class="wel-input" style="width:100%;padding:14px;border-radius:12px;border:1px solid #27272a;background:#18181b;color:#fff;margin-bottom:10px" placeholder="Password">
   <button class="set-btn" style="width:100%;background:#3b82f6" onclick="enterChat()">Continue</button>
 </div>
</div>
<div id="personalityPopup">
 <div class="wel-logo"><img src="/logo.png"></div>
 <h2>Choose your vibe ✨</h2>
  <button onclick="setPersonality('friendly')" class="perso-btn">😊 Friendly</button>
  <button onclick="setPersonality('hype')" class="perso-btn">🔥 Hype</button>
  <button onclick="setPersonality('professional')" class="perso-btn">💼 Professional</button>
  <button onclick="setPersonality('teacher')" class="perso-btn">📚 Teacher</button>
  <button onclick="setPersonality('short')" class="perso-btn">⚡ Short</button>
</div>
<div id="topbar"><div style="display:flex;align-items:center;gap:10px"><div class="wel-logo" style="width:34px;height:34px;margin:0;border-radius:10px"><img src="/logo.png" style="width:22px;height:22px"></div><b>Titech AI 🚀</b></div><div><span id="persoBadge" style="font-size:11px;background:#27272a;padding:4px 8px;border-radius:20px"></span> <span onclick="openSettings()">⚙️</span></div></div>
<div id="chat"></div>
<div id="bar"><input id="input" placeholder="Ask Titech AI 🚀..."><button style="background:none;border:none;color:#3b82f6;font-weight:800;font-size:18px" onclick="sendMessage()">↑</button></div>
<div id="settings" onclick="if(event.target.id=='settings')closeSettings()"><div class="set-box"><h3>Settings</h3><div class="set-row"><span>Email</span><span id="setEmail" style="color:#22c55e;font-size:12px"></span></div><div class="set-row"><span>Model</span><span>Titech AI 🚀</span></div><div class="set-row"><span>Personality</span><span id="setPerso">friendly</span></div><button class="set-btn" onclick="changePersonality()">Change Personality</button><button class="set-btn" onclick="clearChat()">Clear Chats</button><button class="set-btn danger" onclick="doLogout()">Logout</button><button class="set-btn" onclick="closeSettings()">Close</button></div></div>
<script>
const CHAT_KEY='titech_ai_forever_chat';const PERSO_KEY='titech_personality';
let history=[];let currentPerso=localStorage.getItem(PERSO_KEY)||"friendly";
const chatDiv=document.getElementById('chat');
function getGreeting(){const h=new Date().getHours();if(h<12)return"Good Morning";if(h<18)return"Good Afternoon";return"Good Evening"}
document.getElementById('datetimeGreet').textContent=getGreeting();
document.getElementById('persoBadge').textContent=currentPerso;
document.getElementById('setPerso').textContent=currentPerso;
function setPersonality(p){localStorage.setItem(PERSO_KEY,p);currentPerso=p;document.getElementById('persoBadge').textContent=p;document.getElementById('setPerso').textContent=p;document.getElementById('personalityPopup').style.display='none';document.getElementById('welcome').style.display='none';loadHistory()}
function changePersonality(){closeSettings();document.getElementById('personalityPopup').style.display='flex'}
function openSettings(){document.getElementById('settings').style.display='flex';document.getElementById('setEmail').textContent=localStorage.getItem('titech_email')||''}
function closeSettings(){document.getElementById('settings').style.display='none'}
function clearChat(){if(confirm('Clear all?')){localStorage.removeItem(CHAT_KEY);history=[];chatDiv.innerHTML='';closeSettings()}}
function doLogout(){localStorage.clear();location.reload()}
function loadHistory(){const s=localStorage.getItem(CHAT_KEY);if(s){try{history=JSON.parse(s);history.forEach(h=>{addBubble(h.content,h.role)})}catch(e){}}}
function saveHistory(){localStorage.setItem(CHAT_KEY,JSON.stringify(history))}
function addBubble(text,role){const d=document.createElement('div');d.className='bubble '+(role=='user'?'user-bubble':'bot-bubble');d.innerHTML=role=='user'?text:marked.parse(text);chatDiv.appendChild(d);chatDiv.scrollTop=chatDiv.scrollHeight}
async function enterChat(){const u=document.getElementById('username').value.trim();let em=document.getElementById('email').value.trim();let pw=document.getElementById('password').value.trim();if(!u||!em||!pw){alert('Fill all');return}localStorage.setItem('titech_email',em);localStorage.setItem('titech_user',u);document.getElementById('datetimeGreet').textContent=getGreeting()+' '+u+' 🚀';setTimeout(()=>{document.getElementById('welcome').style.display='none';document.getElementById('personalityPopup').style.display='flex'},600)}
async function sendMessage(){const inp=document.getElementById('input');let txt=inp.value.trim();if(!txt)return;addBubble(txt,'user');history.push({role:'user',content:txt});saveHistory();inp.value='';const botDiv=document.createElement('div');botDiv.className='bubble bot-bubble';botDiv.textContent='Thinking...';chatDiv.appendChild(botDiv);try{const res=await fetch('/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({message:txt,history:history.slice(-10),personality:currentPerso})});const data=await res.json();botDiv.innerHTML=marked.parse(data.reply);history.push({role:'assistant',content:data.reply});saveHistory()}catch(e){botDiv.textContent='Error: '+e}chatDiv.scrollTop=chatDiv.scrollHeight}
document.getElementById('input').addEventListener('keydown',e=>{if(e.key==='Enter')sendMessage()});
if(localStorage.getItem('titech_user')){document.getElementById('welcome').style.display='none';loadHistory();}
</script>
</body></html>
    """
    return html.replace("__SUPA_URL__", supabase_url).replace("__SUPA_KEY__", supabase_key)

@app.route("/chat", methods=["POST"])
def chat():
    req = request.get_json()
    user_msg = req.get("message", "")
    history = req.get("history", [])
    personality = req.get("personality", "friendly")
    low = user_msg.lower()
    if any(k in low for k in ["feedback", "contact", "gmail", "email you", "support"]):
        return jsonify({"reply": f"Yes! We love feedback 💜\nReach creator: {FEEDBACK_GMAIL}"})
    context = ""
    try:
        if tavily_client:
            s = tavily_client.search(user_msg, max_results=3)
            context = "\n".join([r["content"][:400] for r in s.get("results", [])])
    except: pass
    perso_map = {
        "friendly": "friendly with Naija vibes, warm helpful",
        "hype": "HYPE Gen-Z Lagos street, pidgin Omo, No cap",
        "professional": "professional corporate",
        "teacher": "patient teacher step by step",
        "short": "ultra concise 1-2 lines"
    }
    perso = perso_map.get(personality, perso_map["friendly"])
    sys_prompt = f"""You are Titech AI 🚀, created by Olajide Timilehin Samson. Contact: {FEEDBACK_GMAIL}
Live at titech-ai.onrender.com - Titech AI 🚀 via Groq.
CRITICAL: You ARE Titech AI 🚀 built by Olajide, NOT ChatGPT, NOT FastAPI.
If asked model: Say I'm Titech AI 🚀 created by Olajide via Groq.
Never mention FastAPI, Docker, network address.
Feedback: {FEEDBACK_GMAIL}
Personality: {perso}
Web facts: {context}
"""
    msgs = [{"role": "system", "content": sys_prompt}]
    for h in history[-10:]:
        if isinstance(h, dict):
            msgs.append({"role": h.get("role","user"), "content": h.get("content","")[:1200]})
    msgs.append({"role": "user", "content": user_msg})
    try:
        if not groq_client: return jsonify({"reply": "Add GROQ_API_KEY in Render"})
        comp = groq_client.chat.completions.create(model="openai/gpt-oss-120b", messages=msgs, temperature=0.7)
        return jsonify({"reply": comp.choices[0].message.content})
    except Exception as e:
        return jsonify({"reply": f"Error: {str(e)}"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
