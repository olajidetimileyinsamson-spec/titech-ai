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
<style>
body{font-family:sans-serif;background:#000;color:#fff;margin:0;display:flex;flex-direction:column;height:100vh}
.header{display:flex;align-items:center;justify-content:space-between;padding:12px 15px;background:#0a0a0a;border-bottom:1px solid #222;position:sticky;top:0}
.left{display:flex;align-items:center;gap:10px}.left img{width:34px;height:34px;border-radius:8px}
select,.small-btn{background:#222;color:#fff;border:1px solid #333;border-radius:20px;padding:6px 10px;font-size:11px;cursor:pointer}
#chat{flex:1;overflow-y:auto;padding:20px;display:flex;flex-direction:column}
.msg{margin:8px 0;padding:12px 16px;border-radius:18px;max-width:85%;line-height:1.45;position:relative;white-space:pre-wrap}
.user{background:#007aff;align-self:flex-end}.ai{background:#1e1e1e;align-self:flex-start;padding-bottom:32px}
.msg img{max-width:100%;border-radius:12px;margin-top:8px}
.btn-row{position:absolute;bottom:5px;right:8px;display:flex;gap:5px}
.c-btn{background:#333;color:#fff;border:none;border-radius:10px;padding:3px 8px;font-size:11px;cursor:pointer}
#bar{display:flex;padding:12px;background:#111;position:sticky;bottom:0}input{flex:1;padding:14px;border-radius:25px;border:none;outline:none}
button.send{margin-left:8px;padding:14px 18px;border-radius:25px;border:none;background:#007aff;color:#fff;font-weight:bold}
</style></head>
<body>
<div class="header"><div class="left"><img src="/logo.png"><h1>Titech AI 🚀</h1></div>
<div style="display:flex;gap:6px;align-items:center">
<select id="personality"><option value="friendly">Friendly 😊</option><option value="naija">Naija 🔥</option><option value="professional">Professional 💼</option><option value="funny">Funny 😂</option><option value="motivational">Motivational 💪</option><option value="genz">Gen Z ✨</option></select>
<button class="small-btn" onclick="saveChatFile()">💾 Save</button>
<button class="small-btn" onclick="clearChat()">🗑️ Clear</button>
</div></div>
<div id="chat"></div>
<div id="bar"><input id="input" placeholder="Ask or 'generate image of...' " onkeypress="if(event.key==='Enter')send()"><button class="send" onclick="send()">Send</button></div>
<script>
const CHAT_KEY='titech_ai_forever_chat';
let history=JSON.parse(localStorage.getItem(CHAT_KEY)||'[]');
const chatDiv=document.getElementById('chat');
let vibeSave=localStorage.getItem('titech_vibe'); if(vibeSave) document.getElementById('personality').value=vibeSave;
document.getElementById('personality').addEventListener('change', e=>localStorage.setItem('titech_vibe', e.target.value));

function renderAll(){
chatDiv.innerHTML='';
if(history.length===0){
chatDiv.innerHTML=`<div class="msg ai">Hi! I'm Titech AI by Olajide Timilehin Samson 😊🔥 Ask me anything! Your chats auto-save forever.<div class="btn-row"><button class="c-btn" onclick="copyText(this)">Copy</button></div></div>`;
return;
}
history.forEach(item=>{
if(item.role==='user'){
chatDiv.innerHTML+=`<div class="msg user">${escapeHtml(item.content)}</div>`;
}else{
let imgPart='';
if(item.image){imgPart=`<br><img src="${item.image}"><div class="btn-row"><button class="c-btn" onclick="copyText(this)">Copy</button><button class="c-btn" onclick="downloadImage('${item.image}')">Download</button></div>`;}
else {imgPart=`<div class="btn-row"><button class="c-btn" onclick="copyText(this)">Copy</button></div>`;}
chatDiv.innerHTML+=`<div class="msg ai">${item.content}${imgPart}</div>`;
}
});
chatDiv.scrollTop=chatDiv.scrollHeight;
}
function escapeHtml(t){let d=document.createElement('div');d.innerText=t;return d.innerHTML;}
function persist(){localStorage.setItem(CHAT_KEY, JSON.stringify(history));}
function copyText(b){let p=b.closest('.msg');let t=p.innerText.replace(/Copy|Download|Copied!/g,'').trim();navigator.clipboard.writeText(t);let o=b.innerText;b.innerText='Copied!';setTimeout(()=>b.innerText=o,1000);}
function downloadImage(u){let a=document.createElement('a');a.href=u;a.download='titech-image.jpg';a.target='_blank';a.click();}
function saveChatFile(){let o='';history.forEach(m=>{o+=(m.role==='user'?'You: ':'Titech AI: ')+(m.content+'\\n')+(m.image? '[Image: '+m.image+']\\n': '')+'\\n';});let b=new Blob([o],{type:'text/plain'});let a=document.createElement('a');a.href=URL.createObjectURL(b);a.download='titech-chat.txt';a.click();}
function clearChat(){if(confirm('Clear all forever saved chats?')){history=[];persist();renderAll();}}

renderAll();

async function send(){
let input=document.getElementById('input');let text=input.value.trim();if(!text)return;
let vibe=document.getElementById('personality').value;
input.value='';
history.push({role:'user',content:text}); persist(); renderAll();

if(text.toLowerCase().startsWith('generate image')||text.toLowerCase().startsWith('create image')){
let prompt=text.replace(/generate image of|create image of|generate image|create image/i,'').trim()||'futuristic AI';
let url=`https://image.pollinations.ai/prompt/${encodeURIComponent(prompt)}?nologo=true&enhance=true&seed=${Date.now()}`;
history.push({role:'assistant',content:`Generated image for: "${prompt}"`,image:url}); persist(); renderAll(); return;
}

try{
let res=await fetch('/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({message:text, personality:vibe, history:history.slice(-12)})});
let data=await res.json();
history.push({role:'assistant',content:data.reply}); persist(); renderAll();
}catch(e){history.push({role:'assistant',content:'Network error, try again 😅'}); persist(); renderAll();}
}
</script></body></html>
"""

@app.route("/chat", methods=["POST"])
def chat():
    req = request.get_json()
    user_msg = req.get("message","")
    personality = req.get("personality","friendly")
    history = req.get("history",[])

    personalities = {
        "friendly": "Friendly warm helpful detailed 😊🔥",
        "naija": "Naija vibe pidgin small funny energetic 🔥",
        "professional": "Professional detailed concise",
        "funny": "Funny witty detailed 😂",
        "motivational": "Motivational uplifting detailed 💪",
        "genz": "Gen Z slang fr no cap detailed ✨"
    }
    style = personalities.get(personality, personalities["friendly"])

    search_query = user_msg
    if len(history) >= 2:
        last_user = [h for h in history if h.get('role')=='user'][-2:-1]
        if last_user:
            search_query = f"{last_user[0]['content']} {user_msg}"[-350:]

    context = ""
    if tavily_client:
        try:
            s = tavily_client.search(search_query, max_results=3, search_depth="advanced")
            context = "\n".join([r["content"][:500] for r in s["results"]])
        except:
            context=""

    system_prompt = f"""
IDENTITY LOCK: You are Titech AI 🚀 built SOLELY by Olajide Timilehin Samson aka Titech. NEVER say OpenAI/ChatGPT/Llama/Meta.

PERSONALITY: {personality} -> {style}

ANTI-HALLUCINATION & LONG ANSWER:
- Chat History for pronoun resolution: {history[-6:]}
- Verified live facts: {context}
- RULE 1: NEVER invent net worth, age, birthday, label, address. Use ONLY verified facts.
- RULE 2: If user says "His net worth" after Elon Musk, you MUST understand His=Elon Musk from history, search Elon Musk only, not Trump.
- RULE 3: If verified facts empty or not contain answer, say "I no get verified live info about that yet 😅 Try rephrase" - DO NOT GUESS.
- RULE 4: Provide LONGER detailed answers (2-4 paragraphs) when asked about person net worth, biography, using ONLY verified facts.
- FIXED: Zinoleesky = Marlian Music ONLY.
- Private info about Olajide = contact olajidetimileyinsamson@gmail.com
"""

    messages=[{"role":"system","content":system_prompt}]
    for h in history[-12:]:
        if h.get('role') in ['user','assistant'] and 'content' in h:
            # don't send image entries as text
            if h.get('image'):
                continue
            messages.append({"role": h['role'], "content": h['content'][:1500]})

    if not messages[-1]['content'] == user_msg:
        messages.append({"role":"user","content":user_msg})

    try:
        comp = groq_client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=messages,
            temperature=0.2,
            max_tokens=2000
        )
        return jsonify({"reply": comp.choices[0].message.content})
    except Exception as e:
        print(e)
        return jsonify({"reply":"Small glitch, try again 😅"}),500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
