from flask import Flask, request, jsonify, render_template_string
import requests, os

app = Flask(__name__)

HTML_PAGE = """
<!DOCTYPE html>
<html><head><title>Titech AI</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
body{font-family:sans-serif;background:#0a0a0a;color:white;margin:0;display:flex;flex-direction:column;height:100vh}
.header{padding:15px;border-bottom:1px solid #222;display:flex;align-items:center;gap:10px}
.logo{width:35px;height:35px;background:linear-gradient(135deg,#a855f7,#6366f1);border-radius:8px;display:flex;align-items:center;justify-content:center;font-weight:bold}
.chat{flex:1;overflow-y:auto;padding:20px}
.msg{margin:10px 0;padding:12px 16px;border-radius:15px;max-width:85%;line-height:1.4}
.user{background:#a855f7;margin-left:auto}
.bot{background:#1a1a1a;border:1px solid #222;white-space:pre-wrap}
.input-area{padding:15px;border-top:1px solid #222;display:flex;gap:10px;position:sticky;bottom:0;background:#0a0a0a}
input{flex:1;padding:12px;border-radius:25px;border:1px solid #333;background:#111;color:white;outline:none}
button{padding:12px 20px;background:#a855f7;color:white;border:none;border-radius:25px;cursor:pointer}
</style></head>
<body>
<div class="header"><div class="logo">T</div><div><b>Titech AI</b><div style="font-size:12px;color:#888">By Timileyin Samson</div></div></div>
<div class="chat" id="chat"></div>
<div class="input-area">
<input id="q" placeholder="Ask anything..." onkeypress="if(event.key==='Enter')ask()">
<button onclick="ask()">Send</button>
</div>
<script>
async function ask(){
 let q=document.getElementById('q').value.trim();
 if(!q)return;
 let chat=document.getElementById('chat');
 chat.innerHTML+='<div class="msg user">'+q+'</div>';
 document.getElementById('q').value='';
 chat.innerHTML+='<div class="msg bot" id="temp">Thinking...</div>';
 chat.scrollTop=chat.scrollHeight;
 try{
  let res=await fetch('/ask',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({question:q})});
  let data=await res.json();
  document.getElementById('temp').remove();
  chat.innerHTML+='<div class="msg bot">'+data.answer+'</div>';
 }catch(e){
  document.getElementById('temp').innerHTML='Error, try again';
 }
 chat.scrollTop=chat.scrollHeight;
}
</script></body></html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_PAGE)

@app.route('/ask', methods=['POST'])
def ask_ai():
    user_q = request.json.get('question','')
    low = user_q.lower()
    if 'who developed you' in low or 'who created you' in low or 'who built you' in low or 'who are you' in low:
        return jsonify({'answer': 'I am Titech AI, developed by Timileyin Samson, founder of Titech AI. Built in Lagos for Africa and the world.'})

    # TRY 3 FREE BRAINS
    try:
        # Brain 1 - Pollinations OpenAI compatible
        r = requests.post(
            "https://text.pollinations.ai/openai",
            json={
                "model": "openai",
                "messages": [
                    {"role": "system", "content": "You are Titech AI created by Timileyin Samson. Answer helpfully and concisely."},
                    {"role": "user", "content": user_q}
                ]
            },
            timeout=25
        )
        if r.status_code == 200:
            data = r.json()
            ans = data['choices'][0]['message']['content']
            if ans:
                return jsonify({'answer': ans})
    except Exception as e:
        print("Brain1 fail:", e)

    try:
        # Brain 2 - Groq-like free endpoint
        r = requests.get(f"https://api.dictionaryapi.dev/api/v2/entries/en/{user_q.split()[-1]}", timeout=5)
        # If above fails, use a simple fallback AI
        r2 = requests.post("https://api.pollinations.ai/v1/chat/completions",
            json={"messages":[{"role":"user","content": user_q}], "model":"openai"},
            timeout=25
        )
        if r2.status_code == 200:
            ans = r2.json()['choices'][0]['message']['content']
            return jsonify({'answer': ans})
    except Exception as e:
        print("Brain2 fail:", e)

    return jsonify({'answer': f'Here is what I know about "{user_q}": This is a great topic! As Titech AI by Timileyin Samson, I am currently connecting to my main brain. But briefly: I can help you learn, explain, write, code, and create. Please ask again in 2 seconds and I will give a detailed answer.'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT',10000)))
