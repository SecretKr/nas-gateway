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

nas_state = {
    "online": False,
    "last_check": 0
}

CHECK_INTERVAL = 3

def check_nas():
    try:
        sock = socket.create_connection((NAS_IP, 80), timeout=1)
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
    if nas_state["online"]:
        return redirect(REDIRECT_URL)

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
            --color-primary: #DFD0B8; 
            --color-secondary: #222831; 
        }
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { background: var(--color-secondary); font-family: sans-serif; min-height: 100vh; display: flex; align-items: center; justify-content: center; }
        .card { background: #393E46; border-radius: 16px; padding: 48px; width: 350px; box-shadow: 0 12px 32px rgba(0, 0, 0, 0.3); text-align: center; }
        .spinner { width: 40px; height: 40px; border: 3px solid #222831; border-top-color: var(--color-primary); border-radius: 50%; margin: 0 auto 24px; animation: spin 0.9s linear infinite; }
        @keyframes spin { to { transform: rotate(360deg); } }
        h1 { font-size: 19px; color: #FFFFFF; margin-bottom: 8px; }
        p { font-size: 14px; color: #D1D5DB; display: flex; align-items: center; justify-content: center;}
        .status-dot { display: inline-block; width: 8px; height: 8px; background: #DFD0B8; border-radius: 50%; margin-right: 5px; }
        </style>
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
                    // Small delay so the user sees the 'Ready' state
                    setTimeout(() => {
                        window.location.href = REDIRECT_URL;
                    }, 500);
                } else {
                    // Still offline, check again in 3 seconds
                    setTimeout(checkStatus, 3000);
                }
            } catch (error) {
                console.error("Error checking status:", error);
                setTimeout(checkStatus, 5000); // Wait longer if server is down
            }
        }

        // Start polling
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