import os
from flask import Flask, render_template_string

app = Flask(__name__)

HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>Titech AI</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { margin:0; font-family: Arial; background:#080808; color:#fff; }
        header { background:#111; padding:12px 25px; display:flex; align-items:center; border-bottom:2px solid #00d4ff; }
        header img { height:45px; width:45px; object-fit:cover; border-radius:8px; margin-right:12px; border:1px solid #00d4ff; }
        header h1 { margin:0; font-size:22px; color:#00d4ff; letter-spacing:1px; }
        .hero { text-align:center; padding:60px 20px; }
        .hero h2 { font-size:32px; color:#fff; }
        .hero p { color:#aaa; font-size:18px; }
    </style>
</head>
<body>
    <header>
        <img src="/logo.jpg" alt="T Logo">
        <h1>TITECH AI</h1>
    </header>
    <div class="hero">
        <h2>Welcome to Titech AI 🚀</h2>
        <p>Building the future with AI</p>
    </div>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_PAGE)

@app.route('/logo.jpg')
def logo():
    from flask import send_from_directory
    return send_from_directory('.', 'logo.jpg')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
