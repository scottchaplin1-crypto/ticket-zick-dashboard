from flask import Flask, request, redirect, render_template_string
import sqlite3
import os
import json

app = Flask(__name__)

conn = sqlite3.connect("config.db", check_same_thread=False)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS settings (
    key TEXT PRIMARY KEY,
    value TEXT
)''')
c.execute('''CREATE TABLE IF NOT EXISTS panels (
    id INTEGER PRIMARY KEY,
    name TEXT,
    emoji TEXT,
    category_id TEXT,
    description TEXT,
    support_roles TEXT,
    button_text TEXT,
    button_color TEXT
)''')
conn.commit()

def base_template(content, title="Dashboard"):
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Ticket Zick - {title}</title>
        <style>
            body {{ margin:0; background:#0a0a14; color:#e0e0ff; font-family:Segoe UI,sans-serif; display:flex; height:100vh; }}
            .sidebar {{ width:260px; background:#111827; padding:20px; border-right:1px solid #00f0ff33; }}
            .sidebar h1 {{ color:#00f0ff; text-align:center; }}
            .nav a {{ display:block; padding:12px 15px; color:#c026d3; text-decoration:none; border-radius:8px; margin:4px 0; }}
            .nav a:hover, .nav a.active {{ background:#1e2937; color:#00f0ff; }}
            .main {{ flex:1; padding:30px; overflow:auto; }}
            .card {{ background:#1a1a2e; padding:25px; border-radius:16px; border:1px solid #00f0ff22; }}
            input, select, button {{ padding:12px; margin:8px 0; border-radius:10px; width:100%; }}
            input, select {{ background:#16213e; color:white; border:none; }}
            button {{ background:linear-gradient(45deg,#00f0ff,#c026d3); color:black; font-weight:bold; cursor:pointer; }}
            .toggle {{ display:flex; align-items:center; gap:10px; }}
        </style>
    </head>
    <body>
        <div class="sidebar">
            <h1>🎟️ Ticket Zick</h1>
            <div class="nav">
                <a href="/general" class="active">General</a>
                <a href="/panel">Panel Settings</a>
                <a href="/ticket">Ticket Options</a>
                <a href="/dropdown">Dropdown Style</a>
                <a href="/forms">Forms</a>
                <a href="/transcripts">Transcripts</a>
                <a href="/logging">Logging</a>
                <a href="/automation">Automation</a>
            </div>
        </div>
        <div class="main">
            {content}
        </div>
    </body>
    </html>
    """

@app.route("/")
def home():
    return redirect("/general")

@app.route("/general", methods=["GET", "POST"])
def general():
    if request.method == "POST":
        # Save settings
        for key, value in request.form.items():
            c.execute("REPLACE INTO settings (key, value) VALUES (?, ?)", (key, value))
        conn.commit()
        return redirect("/general")

    # Load settings
    c.execute("SELECT key, value FROM settings")
    settings = dict(c.fetchall())

    content = """
    <h1>General Settings</h1>
    <div class="card">
        <h2>Support Team Roles</h2>
        <input type="text" name="support_roles" value="{}" placeholder="Staff, Admin, Owner">
        
        <h2>Additional Roles</h2>
        <input type="text" name="additional_roles" value="{}" placeholder="Helper, Moderator">
        
        <div class="toggle">
            <label>Two Step Close</label>
            <input type="checkbox" name="two_step_close" {}> 
        </div>
        
        <div class="toggle">
            <label>Two Step Ticket</label>
            <input type="checkbox" name="two_step_ticket" {}> 
        </div>
        
        <div class="toggle">
            <label>Auto Pin Ticket</label>
            <input type="checkbox" name="auto_pin" {}> 
        </div>
        
        <h2>Ticket Padding</h2>
        <input type="number" name="ticket_padding" value="{}" style="width:100px;">
        
        <button type="submit" form="settings">Save General Settings</button>
    </div>
    """.format(
        settings.get("support_roles", "Staff,Admin,Owner"),
        settings.get("additional_roles", ""),
        'checked' if settings.get("two_step_close") == "on" else '',
        'checked' if settings.get("two_step_ticket") == "on" else '',
        'checked' if settings.get("auto_pin") == "on" else '',
        settings.get("ticket_padding", "1")
    )

    return base_template(f'<form id="settings" method="POST">{content}</form>', "General")

# Panel route (kept from before)
@app.route("/panel")
def panel():
    return base_template("<h1>Panel Settings</h1><p>Coming soon...</p>", "Panel Settings")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)