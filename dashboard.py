from flask import Flask, request, redirect, render_template_string
import sqlite3
import os

app = Flask(__name__)

conn = sqlite3.connect("config.db", check_same_thread=False)
c = conn.cursor()

c.execute('''CREATE TABLE IF NOT EXISTS panels (
    id INTEGER PRIMARY KEY,
    name TEXT,
    emoji TEXT DEFAULT '🎟️',
    category_id TEXT,
    description TEXT,
    support_roles TEXT,
    button_text TEXT DEFAULT 'Create Ticket',
    button_color TEXT DEFAULT '#00f0ff'
)''')

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
            .card {{ background:#1a1a2e; border-radius:16px; padding:25px; border:1px solid #00f0ff33; cursor:pointer; transition:0.3s; }}
            .card:hover {{ transform:scale(1.05); border-color:#c026d3; }}
            .create-btn {{ background:linear-gradient(45deg,#00f0ff,#c026d3); color:black; padding:16px 32px; font-size:18px; border:none; border-radius:12px; cursor:pointer; }}
            .toggle-switch {{ display:flex; align-items:center; justify-content:space-between; background:#16213e; padding:14px 18px; border-radius:12px; margin:12px 0; }}
            input, select, button {{ padding:12px; margin:8px 0; border-radius:10px; width:100%; }}
            input, select {{ background:#16213e; color:white; }}
            button {{ background:linear-gradient(45deg,#00f0ff,#c026d3); color:black; font-weight:bold; cursor:pointer; }}
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

@app.route("/")
@app.route("/dashboard")
def dashboard():
    c.execute("SELECT * FROM panels ORDER BY id DESC")
    panels = c.fetchall()
    
    cards = """
    <div class="grid">
        <div class="card" onclick="window.location='/general'"><h2>General</h2><p>Support team and general items</p></div>
        <div class="card" onclick="window.location='/panel'"><h2>Panel Settings</h2><p>Manage your panels</p></div>
        <div class="card" onclick="window.location='/ticket'"><h2>Ticket</h2><p>General ticket options</p></div>
        <div class="card" onclick="window.location='/dropdown'"><h2>Dropdown</h2><p>Select menu options</p></div>
        <div class="card" onclick="window.location='/forms'"><h2>Forms</h2><p>Form options</p></div>
        <div class="card" onclick="window.location='/transcripts'"><h2>Transcripts</h2><p>Transcript settings</p></div>
        <div class="card" onclick="window.location='/logging'"><h2>Logging</h2><p>Logging options</p></div>
        <div class="card" onclick="window.location='/automation'"><h2>Automation</h2><p>Automation options</p></div>
    </div>
    """
    return base_template(cards)

# ====================== GENERAL ======================
@app.route("/general", methods=["GET", "POST"])
def general():
    if request.method == "POST":
        for key, value in request.form.items():
            if key == "support_roles":
                value = ",".join(request.form.getlist("support_roles"))
            c.execute("REPLACE INTO settings (key, value) VALUES (?, ?)", (key, value))
        conn.commit()
        return redirect("/general")

    c.execute("SELECT key, value FROM settings")
    settings = dict(c.fetchall())

    content = """
    <h1>General Settings</h1>
    <div class="card">
        <form method="POST">
            <h2>Support Team Roles</h2>
            <select name="support_roles" multiple size="8" style="height:200px;">
                <option value="Staff">Staff</option>
                <option value="Admin">Admin</option>
                <option value="Owner">Owner</option>
                <option value="Moderator">Moderator</option>
                <option value="Helper">Helper</option>
            </select>

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
                <label>Save Transcript when ticket is closed</label>
                <input type="checkbox" name="save_transcript" {} >
            </div>
            <input type="text" name="transcript_channel" value="{}" placeholder="Transcript Channel ID">

            <button type="submit" style="margin-top:25px;">Save All Changes</button>
        </form>
    </div>
    """.format(
        'checked' if settings.get("close_ticket") else '',
        'checked' if settings.get("close_and_delete") else '',
        'checked' if settings.get("save_transcript") else '',
        settings.get("transcript_channel", "")
    )
    return base_template(content, "General")

# Placeholder pages
@app.route("/panel")
@app.route("/ticket")
@app.route("/dropdown")
@app.route("/forms")
@app.route("/transcripts")
@app.route("/logging")
@app.route("/automation")
def coming_soon():
    page = request.path.strip("/")
    title = page.replace("/", " ").title()
    return base_template(f"<h1>{title}</h1><p>Coming soon...</p>", title)

@app.route("/create-panel")
def create_panel():
    return base_template("<h2>Create New Panel</h2><p>Full version coming soon...</p>")

@app.route("/<path:path>")
def catch_all(path):
    return redirect("/dashboard")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)