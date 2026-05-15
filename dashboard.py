from flask import Flask, request, redirect, render_template_string
import sqlite3
import os

app = Flask(__name__)

conn = sqlite3.connect("config.db", check_same_thread=False)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS panels (...)''')  # your existing table
c.execute('''CREATE TABLE IF NOT EXISTS settings (
    key TEXT PRIMARY KEY,
    value TEXT
)''')
conn.commit()

def base_template(content, title="Ticket Zick Dashboard"):
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>{title}</title>
        <style>
            body {{ background:#0a0a14; color:#e0e0ff; font-family:Segoe UI,sans-serif; margin:0; padding:20px; }}
            h1 {{ color:#00f0ff; text-align:center; }}
            .header {{ text-align:center; margin-bottom:30px; }}
            .grid {{ display:grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap:20px; max-width:1200px; margin:auto; }}
            .card {{ background:#1a1a2e; border-radius:16px; padding:25px; border:1px solid #00f0ff33; }}
            .create-btn {{ background:linear-gradient(45deg,#00f0ff,#c026d3); color:black; padding:16px 32px; font-size:18px; border:none; border-radius:12px; cursor:pointer; }}
            input, select, button {{ padding:12px; margin:8px 0; border-radius:10px; }}
            input, select {{ background:#16213e; color:white; width:100%; }}
            button {{ background:linear-gradient(45deg,#00f0ff,#c026d3); color:black; font-weight:bold; cursor:pointer; }}
            
            /* Better Toggle Switches */
            .toggle-switch {{
                display: flex;
                align-items: center;
                justify-content: space-between;
                background: #16213e;
                padding: 12px 16px;
                border-radius: 12px;
                margin: 12px 0;
            }}
            .toggle-switch label {{ cursor: pointer; }}
            input[type="checkbox"] {{
                width: 50px;
                height: 26px;
                appearance: none;
                background: #334155;
                border-radius: 50px;
                position: relative;
                cursor: pointer;
            }}
            input[type="checkbox"]:checked {{
                background: #00f0ff;
            }}
            input[type="checkbox"]::after {{
                content: '';
                position: absolute;
                top: 3px;
                left: 3px;
                width: 20px;
                height: 20px;
                background: white;
                border-radius: 50%;
                transition: 0.3s;
            }}
            input[type="checkbox"]:checked::after {{
                left: 27px;
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🎟️ Ticket Zick Dashboard</h1>
            <button class="create-btn" onclick="window.location='/dashboard'">← Back to Dashboard</button>
        </div>
        {content}
    </body>
    </html>
    """

@app.route("/general", methods=["GET", "POST"])
def general():
    if request.method == "POST":
        for key, value in request.form.items():
            if key.startswith("support_roles"):
                value = ",".join(request.form.getlist("support_roles"))
            c.execute("REPLACE INTO settings (key, value) VALUES (?, ?)", (key, str(value)))
        conn.commit()
        return redirect("/general")

    c.execute("SELECT key, value FROM settings")
    settings = dict(c.fetchall())

    content = """
    <h1>General Settings</h1>
    <div class="card">
        <form method="POST">
            <h2>Support Team Roles</h2>
            <select name="support_roles" multiple size="8" style="height:180px;">
                <option value="Staff" selected>Staff</option>
                <option value="Admin">Admin</option>
                <option value="Owner">Owner</option>
                <option value="Moderator">Moderator</option>
                <option value="Helper">Helper</option>
            </select>
            <p><small>Hold CTRL (or CMD) to select multiple roles</small></p>

            <h2>Ticket Close Behaviour</h2>
            <div class="toggle-switch">
                <label>Close Ticket (keep channel)</label>
                <input type="checkbox" name="close_ticket" {} >
            </div>
            <div class="toggle-switch">
                <label>Close & Delete Ticket</label>
                <input type="checkbox" name="close_and_delete" {} >
            </div>

            <h2>Transcripts</h2>
            <div class="toggle-switch">
                <label>Save Transcript when ticket is closed/deleted</label>
                <input type="checkbox" name="save_transcript" {} >
            </div>
            <input type="text" name="transcript_channel" value="{}" placeholder="Transcript Channel ID (optional)">

            <button type="submit" style="margin-top:25px; padding:16px; font-size:17px;">Save All Changes</button>
        </form>
    </div>
    """.format(
        'checked' if settings.get("close_ticket") == "True" else '',
        'checked' if settings.get("close_and_delete") == "True" else '',
        'checked' if settings.get("save_transcript") == "True" else '',
        settings.get("transcript_channel", "")
    )
    return base_template(content, "General")

# Keep your other routes (dashboard, create-panel, etc.)
@app.route("/dashboard")
def dashboard():
    return base_template("<h1>Welcome to Dashboard</h1><p>Use the cards above or go to <a href='/general'>General</a></p>")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)