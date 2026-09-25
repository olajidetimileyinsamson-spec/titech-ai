from flask import Flask, request, jsonify, render_template_string, send_from_directory
import requests, os, urllib.parse, random

app = Flask(__name__)

HTML_PAGE = '''
<!DOCTYPE html>
<html><head>
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Titech AI</title>
<link rel="manifest" href="/manifest.json">
<meta name="theme-color" content="#00a6ff">
<link rel="icon" href="/logo.jpg">
<style>
*{box-sizing:border-box}
body{margin:0;background:#0a0a0a;color:#fff;font-family:system-ui,sans-serif;display:flex;flex-direction:column;height:100vh}
.header{padding:14px 16px;border-bottom:1px solid #1f1f1f;display:flex;gap:12px;align-items:center}
.logo{width:42px;height:42px;border-radius:12px;object-fit:cover;border:1px solid #222}
.chat{flex:1;overflow:auto;padding:16px;padding-bottom:110px;display:flex;flex-direction:column;gap:8px}
.msg{padding:12px 16px;border-radius:20px;max-width:88%;line-height:1.6;white-space:pre-wrap;font-size:14.5px;word-wrap:break-word}
.user{background:#00a6ff;margin-left:auto;border-bottom-right-radius:6px;align-self:flex-end;color:#fff}
.bot{background:#151515;border:1px solid #232323;border-bottom-left-radius:6px;align-self:flex-start}
.bot img{max-width:100%;border-radius:12px;margin-top:10px;display:block}
.thinking{display:flex;gap:6px;align-items:center;color:#888}
.dot{width:6px;height:6px;background:#777;border-radius:50%;animation:b 1.4s infinite}
.dot:nth-child(2){animation-delay:.2s}.dot:nth-child(3){animation-delay:.4s}
@keyframes b{0%,60%,100%{transform:translateY(0);opacity:.4}30%{transform:translateY(-5px);opacity:1}}
.bar{position:fixed;bottom:0;left:0;right:0;padding:12px;background:#0a0a0a;display:flex;gap:10px}
.inputWrap{flex:1;display:flex;background:#161616;border:1px solid #2a2a2a;border-radius:28px;padding:4px 6px 4px 16px}
input{flex:1;background:transparent;border:none;color:#fff;outline:none;font-size:15px;padding:10px 0}
button{width:38px;height:38px;border-radius:50%;background:#00a
