from flask import Flask, request, jsonify, render_template_string
import requests
import os

app = Flask(__name__)

# HTML - WITH YOUR LOGO
HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
<title>Titech AI</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
body{font-family:sans-serif;background:#0a0a0a;color:white;margin:0;display:flex;flex-direction:column;height:100vh}
.header{padding:15px;border-bottom:1px solid #222;display:flex;align-items:center;gap:10px}
.logo{width:35px;height:35px;background:linear-gradient(135deg,#a855f7,#6366f1);border-radius:8px;display:flex;align-items:center;justify-content:center;font-weight:bold}
.chat{flex:1;overflow-y:auto;padding:20px}
.msg{margin:10px 0;padding:12px 16px;border-radius:15px;max-width:80%}
.user{background:#a855f7;margin-left:auto}
.bot{background:#1a1a1a;border:1px solid #222}
.input-area{padding:15px;border-top:1px solid #222;display:flex;gap:10px}
input{flex:1;padding:12px;border-radius:25px;border:1px solid #333;background:#111;color:white;outline:none}
button{padding:12px 20px;background:#a855f7;color:white;border:none;border-radius:25px;cursor:pointer}
</style>
</head>
<body>
<div class="header">
<div class="logo">T</div>
<div><b>Titech AI</b><div style="font-size:12px;color:#888">By Timileyin Samson</div></div>
</div>
<div class="chat" id="chat"></div>
<div class="input-area">
<input id="q" placeholder="Ask anything..." onkeypress="if(event.key==='Enter')ask()">
<button onclick="ask()">Send</button>
</div>
<script>
async function ask(){
 let q=document.getElementById('q').value;
 if(!q)return;
 let chat=document.getElementById('chat');
 chat.innerHTML+='<div class="msg user">'+q+'</div>';
 document.getElementById('q').value='';
 chat.innerHTML+='<div class="msg bot" id="temp">Thinking...</div>';
 chat.scrollTop=chat.scrollHeight;
 let res=await fetch('/ask',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({question:q})});
 let data=await res.json();
 document.getElementById('temp').remove();
 chat.innerHTML+='<div class="msg bot">'+data.answer+'</div>';
 chat.scrollTop=chat.scrollHeight;
}
</script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_PAGE)

@app.route('/ask', methods=['POST'])
def ask_ai():
    data = request.json
    user_question = data.get('question', '')

    if 'who developed you' in user_question.lower() or 'who created you' in user_question.lower():
        return jsonify({'answer': 'I was developed by Timileyin Samson, founder of Titech AI. A powerful AI built for Africa and the world.'})

    try:
        # Using free AI API
        response = requests.post(
            'https://api.deepseek.com/v1/chat/completions',
            headers={'Content-Type': 'application/json'},
            json={
                'model': 'deepseek-chat',
                'messages': [{'role': 'user', 'content': user_question}]
            },
            timeout=20
        )
        if response.status_code == 200:
            answer = response.json()['choices'][0]['message']['content']
            return jsonify({'answer': answer})
    except:
        pass

    return jsonify({'answer': f'Great question! About "{user_question}" - Titech AI is here to help. I am developed by Timileyin Samson. Please try again, my full brain is connecting...'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 10000)))
