import os
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from groq import Groq
from tavily import TavilyClient

app = Flask(__name__)
CORS(app)

groq_client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
tavily_client = TavilyClient(api_key=os.environ.get("TAVILY_API_KEY")) if os.environ.get("TAVILY_API_KEY") else None

@app.route("/logo.png")
def logo():
    try:
        return send_from_directory(".", "logo.png")
    except:
        return "", 404

@app.route("/")
def home():
    return """
<!DOCTYPE html><html><head><title>Titech AI 🚀</title><meta name="viewport" content="width=device-width, initial-scale=1">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap" rel="stylesheet">
<style>
*{box-sizing:border-box;font-family:'Inter',sans-serif}
body{margin:0;background:#0a0a0a;color:#fff;display:flex;flex-direction:column;height:100vh}
/* NEAT HEADER */
.header{position:sticky;top:0;z-index:10;background:rgba(15,15,15,0.95);backdrop-filter:blur(12px);border-bottom:1px solid #1f1f1f;padding:10px 14px;display:flex;align-items:center;justify-content:space-between;gap:10px}
.brand{display:flex;align-items:center;gap:10px;min-width:0}
.brand img{width:36px;height:36px;border-radius:10px;background:#111;object-fit:cover}
.brand h1{font-size:18px;margin:0;line-height:1.1;font-weight:700;white-space:nowrap}
.brand h1 span{font-size:14px}
.controls{display:flex;align-items:center;gap:8px;flex-shrink:0}
select{appearance:none;background:#1a1a1a;color:#fff;border:1px solid #2a2a2a;border-radius:999px;padding:8px 28px 8px 12px;font-size:12.5px;outline:none}
.icon-btn{width:36px;height:36px;border-radius:50%;background:#1a1a1a;border:1px solid #2a2a2a;color:#fff;display:grid;place-items:center;cursor:pointer;font-size:14px}
.icon-btn:active{transform:scale(0.95)}
#chat{flex:1;overflow-y:auto;padding:16px;display:flex;flex-direction:column;gap:6px}
.msg{max-width:84%;padding:13px 15px;border-radius:20px;line-height:1.5;font-size:14.5px;position:relative;word-wrap:break-word;white-space:pre-wrap}
.user{background:#0b84ff;align-self:flex-end;border-bottom-right-radius:6px}
.ai{background:#1c1c1e;align-self:flex-start;border-bottom-left-radius:6px;padding-bottom:34px}
.msg img{max-width:100%;border-radius:14px;margin-top:10px;display:block}
.btn-row{position:absolute;right:8px;bottom:6px;display:flex;gap:6px}
.c-btn{background:#2a2a2a;border:none;color:#ccc;border-radius:999px;padding:4px 9px;font-size:11px;cursor:pointer}
.c-btn:active{background:#0b84ff;color:#fff}
#bar{position:sticky;bottom:0;background:#0f0f0f;border-top:1px solid #1f1f1f;padding:10px 12px;display:flex;gap:10px;align-items:center}
#bar input{flex:1;background:#1c1c1e;border:1px solid #2a2a2a;color:#fff;padding:14px 18px;border-radius:999px;outline:none;font-size:15px}
.send{width:52px;height:46px;border-radius:999px;border:none;background:#0b84ff;color:#fff;font-weight:700;cursor:pointer}
@media(max-width:380px){.brand h1{font-size:16px} select{max-width:95px}}
</style></head>
<body>
<div class="header">
<div class="brand"><img src="/logo.png" onerror="this.style.display='none'"><h1>Titech AI <span>🚀</span></h1></div>
<div class="controls">
<select id="personality"><option value="friendly">Friendly 😊</option><option value="naija">Naija 🔥</option><option value="professional">Pro 💼</option><option value="funny">Funny 😂</option><option value="motivational">Motivate 💪</option><option value="genz">Gen Z ✨</option></select>
<button class="icon-btn" onclick="saveChatFile()" title="Save">💾</button>
<button class="icon-btn" onclick="clearChat()" title="Clear">🗑️</button>
</div>
</div>
<div id="chat"></div>
<div id="bar"><input id="input" placeholder="Ask or 'generate picture of...' " onkeypress="if(event.key==='Enter')send()"><button class="send" onclick="send()">Send</button></div>
<script>
const CHAT_KEY='titech_ai_forever_chat';
let history=JSON.parse(localStorage.getItem(CHAT_KEY)||'[]');
const chatDiv=document.getElementById('chat');
let v=localStorage.getItem('titech_vibe'); if(v) document.getElementById('personality').value=v;
document.getElementById('personality').addEventListener('change', e=>localStorage.setItem('titech_vibe', e.target.value));
function renderAll(){chatDiv.innerHTML=''; if(history.length===0){chatDiv.innerHTML=`<div class="msg ai">Hey there! 👋😊 I'm Titech AI, ready to help with anything. Your chats auto-save forever.<div class="btn-row"><button class="c-btn" onclick="copyText(this)">Copy</button></div></div>`;return;} history.forEach((item,idx)=>{if(item.role==='user'){chatDiv.innerHTML+=`<div class="msg user">${item.content}<div class="btn-row"><button class="c-btn" onclick="editMsg(${idx})">Edit</button><button class="c-btn" onclick="deleteMsg(${idx})">Del</button></div></div>`;}else{let img=item.image?`<br><img src="${item.image}"><div class="btn-row"><button class="c-btn" onclick="copyText(this)">Copy</button><button class="c-btn" onclick="downloadImage('${item.image}')">Download</button><button class="c-btn" onclick="deleteMsg(${idx})">Del</button></div>`:`<div class="btn-row"><button class="c-btn" onclick="copyText(this)">Copy</button><button class="c-btn" onclick="editMsg(${idx})">Edit</button><button class="c-btn" onclick="deleteMsg(${idx})">Del</button></div>`; chatDiv.innerHTML+=`<div class="msg ai">${item.content}${img}</div>`;}}); chatDiv.scrollTop=chatDiv.scrollHeight;}
function copyText(b){let p=b.closest('.msg');let t=p.innerText.replace(/Copy|Download|Edit|Del|Copied!/g,'').trim();navigator.clipboard.writeText(t);let o=b.innerText;b.innerText='Copied!';setTimeout(()=>b.innerText=o,1000);}
function downloadImage(u){let a=document.createElement('a');a.href=u;a.download='titech-image.jpg';a.target='_blank';a.click();}
function saveChatFile(){let o='';history.forEach(m=>{o+=(m.role==='user'?'You: ':'AI: ')+m.content+'\\n';});let b=new Blob([o],{type:'text/plain'});let a=document.createElement('a');a.href=URL.createObjectURL(b);a.download='titech-chat.txt';a.click();}
function clearChat(){if(confirm('Clear all?')){history=[];localStorage.setItem(CHAT_KEY,JSON.stringify(history));renderAll();}}
function persist(){localStorage.setItem(CHAT_KEY,JSON.stringify(history));}
function deleteMsg(i){history.splice(i,1);persist();renderAll();}
function editMsg(i){let n=prompt('Edit:',history[i].content); if(n){history[i].content=n.trim();persist();renderAll();}}
renderAll();
async function send(){
let input=document.getElementById('input');let text=input.value.trim();if(!text)return;
let vibe=document.getElementById('personality').value;input.value='';
history.push({role:'user',content:text});persist();renderAll();
let low=text.toLowerCase();
let isImg=(low.includes('generate')||low.includes('create')||low.includes('make')||low.includes('give')) && (low.includes('image')||low.includes('picture')||low.includes('photo')||low.includes('pic'));
if(isImg){
let prompt=text.replace(/generate.*?(image|picture|photo|pic) of|create.*?(image|picture|photo|pic) of|make.*?(image|picture|photo|pic) of|give me.*?(image|picture|photo|pic) of|generate.*?(image|picture|photo|pic)|create.*?(image|picture|photo|pic)|make.*?(image|picture|photo|pic)|image of|picture of|photo of|pic of/gi,'').trim()||'cute dog';
let url=`https://image.pollinations.ai/prompt/${encodeURIComponent(prompt+', high quality, 4k') }?nologo=true&enhance=true&seed=${Date.now()}`;
history.push({role:'assistant',content:`✅ Generated: "${prompt}"`,image:url});persist();renderAll();return;
}
try{
let res=await fetch('/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({message:text, personality:vibe, history:history.slice(-12)})});
let data=await res.json();history.push({role:'assistant',content:data.reply});persist();renderAll();
}catch(e){history.push({role:'assistant',content:'Network error 😅'});persist();renderAll();}
}
</script></body></html>
"""

@app.route("/chat", methods=["POST"])
def chat():
    req=request.get_json()
    user_msg=req.get("message","")
    personality=req.get("personality","friendly")
    history=req.get("history",[])
    style={"friendly":"Friendly 😊","naija":"Naija 🔥","professional":"Pro 💼","funny":"Funny 😂","motivational":"Motivate 💪","genz":"Gen Z ✨"}.get(personality,"Friendly")
    search_q=user_msg
    if len(history)>=2:
        last=[h for h in history if h.get('role')=='user'][-2:-1]
        if last: search_q=f"{last[0]['content']} {user_msg}"[-350:]
    context=""
    if tavily_client:
        try:
            s=tavily_client.search(search_q, max_results=3, search_depth="advanced")
            context="\\n".join([r["content"][:500] for r in s["results"]])
        except: pass
    sys=f"You are Titech AI 🚀 by Olajide Timilehin Samson ONLY. Personality {personality}->{style}. Facts:{context}. History:{history[-4:]}. No fake info. If no facts say no verified info. Zinoleesky=Marlian. Never output pollinations links."
    msgs=[{"role":"system","content":sys}]
    for h in history[-12:]:
        if h.get('role') in ['user','assistant'] and 'content' in h and not h.get('image'):
            msgs.append({"role":h['role'],"content":h['content'][:1500]})
    if not msgs or msgs[-1].get('content')!=user_msg:
        msgs.append({"role":"user","content":user_msg})
    try:
        comp=groq_client.chat.completions.create(model="openai/gpt-oss-120b", messages=msgs, temperature=0.2, max_tokens=2000)
        return jsonify({"reply":comp.choices[0].message.content})
    except Exception as e:
        print(e); return jsonify({"reply":"Small glitch 😅"}),500

if __name__=="__main__":
    app.run(host="0.0.0.0", port=10000)
