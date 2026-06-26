from flask import Flask, redirect, jsonify, Response
import os
import socket
import subprocess
import time
import threading

app = Flask(__name__)

NAS_IP = os.getenv("NAS_IP")
NAS_MAC = os.getenv("NAS_MAC")
REDIRECT_URL = os.getenv("REDIRECT_URL")
CHECK_PORT = int(os.getenv("CHECK_PORT", 80))

CUSTOM_URL_1 = os.getenv("CUSTOM_URL_1", "https://google.com")
CUSTOM_LABEL_1 = os.getenv("CUSTOM_LABEL_1", "Custom URL 1")
CUSTOM_URL_2 = os.getenv("CUSTOM_URL_2", "https://github.com")
CUSTOM_LABEL_2 = os.getenv("CUSTOM_LABEL_2", "Custom URL 2")

nas_state = {
    "online": False,
    "last_check": 0
}

CHECK_INTERVAL = 3

def check_nas():
    try:
        sock = socket.create_connection((NAS_IP, CHECK_PORT), timeout=1)
        sock.close()
        return True
    except:
        return False

def wake_nas():
    subprocess.run([
        "wakeonlan",
        "-i", "255.255.255.255",
        NAS_MAC
    ])

def refresh_state():
    while True:
        nas_state["online"] = check_nas()
        if nas_state["online"]:
            nas_state["wake_sent"] = False
        nas_state["last_check"] = time.time()
        time.sleep(CHECK_INTERVAL)

threading.Thread(target=refresh_state, daemon=True).start()

@app.route("/")
def index():
    return Response("""
    <!DOCTYPE html>
    <html lang="en">
    <head>
    <meta charset="UTF-8"/>
    <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
    <title>Gateway Portal</title>
    <style>
        :root { 
            --color-bg-start: #0f172a;
            --color-bg-end: #1e1b4b;
            --color-card-bg: rgba(30, 41, 59, 0.7);
            --color-text-primary: #f8fafc;
            --color-text-secondary: #94a3b8;
            --color-accent-1: linear-gradient(135deg, #3b82f6, #8b5cf6);
            --color-accent-2: linear-gradient(135deg, #10b981, #059669);
            --color-accent-3: linear-gradient(135deg, #ff9a86, #e08775);
            --color-border: rgba(255, 255, 255, 0.1);
        }
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { 
            background: linear-gradient(135deg, var(--color-bg-start), var(--color-bg-end)); 
            font-family: 'Outfit', 'Inter', -apple-system, sans-serif; 
            min-height: 100vh; 
            display: flex; 
            align-items: center; 
            justify-content: center; 
            color: var(--color-text-primary);
            overflow: hidden;
        }
        .container {
            position: relative;
            z-index: 10;
            width: 100%;
            max-width: 440px;
            padding: 20px;
        }
        .card { 
            background: var(--color-card-bg); 
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
            border: 1px solid var(--color-border);
            border-radius: 24px; 
            padding: 40px; 
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.4); 
            text-align: center;
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }
        .card:hover {
            transform: translateY(-2px);
            box-shadow: 0 24px 48px rgba(0, 0, 0, 0.5);
        }
        h1 { 
            font-size: 26px; 
            font-weight: 700;
            margin-bottom: 8px; 
            background: linear-gradient(to right, #3b82f6, #a855f7);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        p.subtitle { 
            font-size: 15px; 
            color: var(--color-text-secondary); 
            margin-bottom: 32px;
        }
        .btn-list {
            display: flex;
            flex-direction: column;
            gap: 16px;
        }
        .btn {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 12px;
            padding: 16px 24px;
            border-radius: 12px;
            font-size: 16px;
            font-weight: 600;
            color: #ffffff;
            text-decoration: none;
            border: none;
            cursor: pointer;
            transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
            position: relative;
            overflow: hidden;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        }
        .btn-1 {
            background: var(--color-accent-1);
        }
        .btn-1:hover {
            box-shadow: 0 6px 20px rgba(59, 130, 246, 0.4);
            transform: translateY(-2px);
        }
        .btn-2 {
            background: var(--color-accent-2);
        }
        .btn-2:hover {
            box-shadow: 0 6px 20px rgba(16, 185, 129, 0.4);
            transform: translateY(-2px);
        }
        .btn-3 {
            background: var(--color-accent-3);
        }
        .btn-3:hover {
            box-shadow: 0 6px 20px rgba(245, 158, 11, 0.4);
            transform: translateY(-2px);
        }
        .btn:active {
            transform: translateY(0);
        }
        /* Background decorative glow */
        .glow {
            position: absolute;
            width: 300px;
            height: 300px;
            background: radial-gradient(circle, rgba(99, 102, 241, 0.15) 0%, rgba(0,0,0,0) 70%);
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            z-index: 1;
            pointer-events: none;
        }
    </style>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@400;600;700&display=swap" rel="stylesheet">
    </head>
    <body>
    <div class="glow"></div>
    <div class="container">
        <div class="card">
            <h1>Gateway Portal</h1>
            <p class="subtitle">Select a destination below</p>
            <div class="btn-list">
                <a href="/redirect/1" class="btn btn-1">""" + CUSTOM_LABEL_1 + """</a>
                <a href="/redirect/2" class="btn btn-2">""" + CUSTOM_LABEL_2 + """</a>
                <a href="/wake" class="btn btn-3">NAS</a>
            </div>
        </div>
    </div>
    </body>
    </html>
    """, mimetype="text/html")

@app.route("/redirect/1")
def redirect_1():
    return redirect(CUSTOM_URL_1)

@app.route("/redirect/2")
def redirect_2():
    return redirect(CUSTOM_URL_2)

@app.route("/wake")
def wake():
    if not nas_state["online"]:
        wake_nas()

    return Response("""
    <!DOCTYPE html>
    <html lang="en">
    <head>
    <meta charset="UTF-8"/>
    <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
    <title>NAS Starting</title>
    <style>
        :root { 
            --color-bg-start: #0f172a;
            --color-bg-end: #1e1b4b;
            --color-card-bg: rgba(30, 41, 59, 0.7);
            --color-text-primary: #f8fafc;
            --color-text-secondary: #94a3b8;
            --color-primary: #dfd0b8;
            --color-border: rgba(255, 255, 255, 0.1);
        }
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { 
            background: linear-gradient(135deg, var(--color-bg-start), var(--color-bg-end)); 
            font-family: 'Outfit', 'Inter', -apple-system, sans-serif; 
            min-height: 100vh; 
            display: flex; 
            align-items: center; 
            justify-content: center;
            color: var(--color-text-primary);
        }
        .card { 
            background: var(--color-card-bg); 
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
            border: 1px solid var(--color-border);
            border-radius: 24px; 
            padding: 48px; 
            width: 380px; 
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.4); 
            text-align: center; 
        }
        .spinner { 
            width: 50px; 
            height: 50px; 
            border: 4px solid rgba(255, 255, 255, 0.1); 
            border-top-color: var(--color-primary); 
            border-radius: 50%; 
            margin: 0 auto 28px; 
            animation: spin 1s cubic-bezier(0.5, 0, 0.5, 1) infinite; 
        }
        @keyframes spin { to { transform: rotate(360deg); } }
        h1 { font-size: 22px; font-weight: 700; color: #FFFFFF; margin-bottom: 12px; }
        p { font-size: 15px; color: var(--color-text-secondary); display: flex; align-items: center; justify-content: center;}
        .status-dot { display: inline-block; width: 8px; height: 8px; background: var(--color-primary); border-radius: 50%; margin-right: 8px; animation: pulse 1.5s infinite ease-in-out; }
        @keyframes pulse {
            0%, 100% { opacity: 0.5; transform: scale(1); }
            50% { opacity: 1; transform: scale(1.2); }
        }
    </style>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@400;600;700&display=swap" rel="stylesheet">
    </head>
    <body>
    <div class="card">
        <div class="spinner"></div>
        <h1>NAS is starting up</h1>
        <p id="status-text"><span class="status-dot"></span>Checking connection...</p>
    </div>

    <script>
        const REDIRECT_URL = '""" + REDIRECT_URL + """';
        
        async function checkStatus() {
            try {
                const response = await fetch('/status');
                const data = await response.json();
                
                if (data.nas === "online") {
                    document.getElementById('status-text').innerText = "Ready! Redirecting...";
                    setTimeout(() => {
                        window.location.href = REDIRECT_URL;
                    }, 500);
                } else {
                    setTimeout(checkStatus, 3000);
                }
            } catch (error) {
                console.error("Error checking status:", error);
                setTimeout(checkStatus, 5000);
            }
        }

        checkStatus();
    </script>
    </body>
    </html>
    """, mimetype="text/html")

@app.route("/status")
def status():
    return jsonify({
        "nas": "online" if nas_state["online"] else "offline",
        "last_check": nas_state["last_check"]
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)