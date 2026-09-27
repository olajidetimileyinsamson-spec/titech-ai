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
    try: return send_from_directory(".", "logo.png")
    except: return "",404

@app.route("/")
def home():
    return """
<!DOCTYPE html><html><head><title>Titech AI 🚀</title><meta name="viewport" content="width=device-width, initial-scale=1">
<style>
*{box-sizing:border-box;font-family:system-ui}
body{margin:0;background:#000;color:#fff;display:flex;flex-direction:column;height:100vh}
.header{position:sticky;top:0;z-index:10;background:#0f0f0f;border-bottom:1px solid #222;padding:10px 12px;display:flex;justify-content:space-between;align-items:center}
.brand{display:flex;align-items:center;gap:8px}.brand img{width:32px;height:32px;border-radius:8px}
.controls{display:flex;gap:8px;align-items:center}
select{background:#1e1e1e;color:#fff;border:1px solid #333;border-radius:20px;padding:7px 10px;font-size:12px}
.icon-btn{width:34px;height:34px;border-radius:50%;background:#1e1e1e;border:1px solid #333;color:#fff;display:grid;place-items:center}
#chat{flex:1;overflow-y:auto;padding:14px;display:flex;flex-direction:column;gap:12px}
.bubble-wrap{max-width:85%;display:flex;flex-direction:column;gap:5px}
.bubble-wrap.user{align-self:flex-end;align-items:flex-end}
.bubble-wrap.ai{align-self:flex-start;align-items:flex-start}
.msg{padding:12px 14px;border-radius:18px;line-height:1.5;font-size:14.5px;white-space:pre-wrap;word-break:break-word}
.user.msg{background:#0b84ff;color:#fff;border-bottom-right-radius:6px}
.ai.msg{background:#1c1c1e;color:#fff;border-bottom-left-radius:6px}
.msg img{max-width:100%;border-radius:12px;margin-top:8px;display:block}
.actions{display:flex;gap:6px;padding:0 4px}
.c-btn{background:#1e1e1e;border:1px solid #2a2a2a;color:#aaa;border-radius:12px;padding:3px 8px;font-size:11px;cursor:pointer}
.c-btn:hover{color:#fff;border-color:#555}
#bar{position:sticky;bottom:0;background:#0f0f0f;border-top:1px solid #222;padding:10px;display:flex;gap:8px}
#bar input{flex:1;background:#1e1e1e;border:1px solid #333;color:#fff;padding:13px 16px;border-radius:25px;outline:none}
.send{background:#0b84ff;border:none;color:#fff;padding:0 20px;border-radius:25px;font-weight:bold}
</style></head>
<body>
<div class="header"><div class="brand"><img src="/logo.png"><b>Titech AI 🚀</b></div>
<div class="controls"><select id="personality"><option value="friendly">Friendly 😊</option><option value="naija">Naija 🔥</option><option value="funny">Funny 😂</option><option value="professional">Pro 💼</option><option value="genz">Gen Z ✨</option></select>
<button class="icon-btn" onclick="saveChatFile()">💾</button><button class="icon-btn" onclick="clearChat()">🗑️</button></div></div>
<div id="chat"></div>
<div id="bar"><input id="input" placeholder="Ask or 'generate picture of dog'" onkeypress="if(event.key==='Enter')send()"><button class="send" onclick="send()">Send</button></div>
<script>
const CHAT_KEY='titech_ai_forever_chat';
let history=JSON.parse(localStorage.getItem(CHAT_KEY)||'[]');
const chatDiv=document.getElementById('chat');
function persist(){localStorage.setItem(CHAT_KEY,JSON.stringify(history));}
function renderAll(){
chatDiv.innerHTML='';
if(history.length==0){chatDiv.innerHTML='<div class="bubble-wrap ai"><div class="msg">Hi! I\\'m Titech AI by Olajide Timilehin Samson 🚀 Your chats auto-save forever.</div><div class="actions"><button class="c-btn" onclick="copyText(0)">Copy</button></div></div>';return;}
history.forEach((item,idx)=>{
let isUser=item.role==='user';
let img=item.image?`<img src="${item.image}" onerror="this.src='https://via.placeholder.com/300?text=Image+failed+retry'">`:'';
let actions=isUser
? `<div class="actions"><button class="c-btn" onclick="editMsg(${idx})">✏️ Edit</button><button class="c-btn" onclick="deleteMsg(${idx})">🗑️ Delete</button><button class="c-btn" onclick="copyText(${idx})">Copy</button></div>`
: `<div class="actions"><button class="c-btn" onclick="copyText(${idx})">Copy</button>${item.image?`<button class="c-btn" onclick="downloadImage('${item.image}')">Download</button>`:''}<button class="c-btn" onclick="editMsg(${idx})">✏️ Edit</button><button class="c-btn" onclick="deleteMsg(${idx})">🗑️ Delete</button></div>`;
chatDiv.innerHTML+=`<div class="bubble-wrap ${isUser?'user':'ai'}"><div class="msg">${escapeHtml(item.content)}${img}</div>${actions}</div>`;
});
chatDiv.scrollTop=chatDiv.scrollHeight;
}
function escapeHtml(t){let d=document.createElement('div');d.textContent=t;return d.innerHTML;}
function copyText(i){navigator.clipboard.writeText(history[i].content);alert('Copied!');}
function downloadImage(u){let a=document.createElement('a');a.href=u;a.target='_blank';a.download='titech.jpg';a.click();}
function saveChatFile(){let t=history.map(m=>`${m.role}: ${m.content}`).join('\\n\\n');let b=new Blob([t],{type:'text/plain'});let a=document.createElement('a');a.href=URL.createObjectURL(b);a.download='titech.txt';a.click();}
function clearChat(){if(confirm('Clear all?')){history=[];persist();renderAll();}}
function deleteMsg(i){history.splice(i,1);persist();renderAll();}
function editMsg(i){let n=prompt('Edit:',history[i].content); if(n){history[i].content=n;persist();renderAll();}}
renderAll();
async function send(){
let input=document.getElementById('input');let text=input.value.trim();if(!text)return;
input.value='';
history.push({role:'user',content:text});persist();renderAll();
let low=text.toLowerCase();
let isImg=(low.includes('generate')||low.includes('create')||low.includes('make')||low.includes('give')) && (low.includes('image')||low.includes('picture')||low.includes('photo')||low.includes('pic'));
if(isImg){
let prompt=text.replace(/generate.*?(image|picture|photo|pic) of|create.*?(image|picture|photo|pic) of|make.*?(image|picture|photo|pic) of|give me.*?(image|picture|photo|pic) of|generate.*?(image|picture|photo|pic)|create.*?(image|picture|photo|pic)|make.*?(image|picture|photo|pic)|image of|picture of|photo of|pic of/gi,'').trim()||'cute dog';
let url=`https://image.pollinations.ai/prompt/${encodeURIComponent(prompt+', high quality') }?seed=${Date.now()}&nologo=true`;
history.push({role:'assistant',content:`Generated: "${prompt}"`,image:url});persist();renderAll();return;
}
try{
let res=await fetch('/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({message:text,history:history.slice(-12)})});
let data=await res.json();history.push({role:'assistant',content:data.reply});persist();renderAll();
}catch(e){history.push({role:'assistant',content:'Network error 😅'});persist();renderAll();}
}
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
    sys=f"You are Titech AI by Olajide Timilehin Samson. Facts: {context}. NEVER give image prompts, NEVER give pollinations links, NEVER say use Midjourney/DALL-E. If user asks for image, say 'Image don generate for up 👆'. No fake info."
    msgs=[{"role":"system","content":sys}]
    for h in history[-10:]:
        if not h.get('image'): msgs.append({"role":h['role'],"content":h['content'][:1200]})
    msgs.append({"role":"user","content":user_msg})
    comp=groq_client.chat.completions.create(model="openai/gpt-oss-120b", messages=msgs, temperature=0.3, max_tokens=2000)
    return jsonify({"reply":comp.choices[0].message.content})

if __name__=="__main__":
    app.run(host="0.0.0.0", port=10000)
