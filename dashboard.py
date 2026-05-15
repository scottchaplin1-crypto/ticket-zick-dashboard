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

def base_template(content, title="Ticket Zick Dashboard", show_back=False):
    back_button = '''
        <button onclick="window.location='/dashboard'" 
                style="background:linear-gradient(45deg,#00f0ff,#c026d3); color:black; padding:12px 24px; border:none; border-radius:12px; cursor:pointer; font-size:16px;">
            ← Back to Dashboard
        </button>
    ''' if show_back else ''

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>{title}</title>
        <style>
            body {{ background:#0a0a14; color:#e0e0ff; font-family:Segoe UI,sans-serif; margin:0; padding:20px; }}
            h1 {{ color:#00f0ff; text-align:center; }}
            .header {{ text-align:center; margin-bottom:30px; }}
            .section-title {{ color:#c026d3; margin:40px 0 15px 0; font-size:22px; }}
            .grid {{ display:grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap:20px; max-width:1200px; margin:auto; }}
            .card {{ background:#1a1a2e; border-radius:16px; padding:25px; border:1px solid #00f0ff33; cursor:pointer; transition:0.3s; }}
            .card:hover {{ transform:scale(1.05); border-color:#c026d3; }}
            .create-btn {{ background:linear-gradient(45deg,#00f0ff,#c026d3); color:black; padding:16px 32px; font-size:18px; border:none; border-radius:12px; cursor:pointer; margin:10px; }}
            input[type="checkbox"] {{ width:28px; height:28px; accent-color:#00f0ff; }}
            .option {{ display:flex; align-items:center; gap:15px; padding:12px 0; border-bottom:1px solid #334155; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🎟️ Ticket Zick Dashboard</h1>
            
            <a href="https://discord.com/oauth2/authorize?client_id=YOUR_CLIENT_ID_HERE&scope=bot+applications.commands&permissions=8" target="_blank">
                <button class="create-btn" style="background:linear-gradient(45deg,#00ff88,#00f0ff); font-size:20px; padding:18px 40px;">
                    ➕ Invite Ticket Zick to Your Server
                </button>
            </a>
            
            {back_button}
        </div>
        {content}
    </body>
    </html>
    """

@app.route("/")
@app.route("/dashboard")
def dashboard():
    content = """
    <div class="section-title">Panel Settings</div>
    <div class="grid">
        <div class="card" onclick="window.location='/general'"><h2>General</h2><p>Support team and general items</p></div>
        <div class="card"><h2>Panel</h2><p>Options for the message used to create tickets</p></div>
        <div class="card"><h2>Command Style</h2><p>Options for creating tickets using commands</p></div>
        <div class="card"><h2>Dropdown Style</h2><p>Options for select menu</p></div>
        <div class="card"><h2>Thread Style</h2><p>Thread style tickets</p></div>
        <div class="card"><h2>Forms</h2><p>Form Options</p></div>
    </div>

    <div class="section-title">Advanced Settings</div>
    <div class="grid">
        <div class="card" onclick="window.location='/transcripts'"><h2>Transcript</h2><p>Options for saving transcripts</p></div>
        <div class="card"><h2>Logging</h2><p>Server logging options</p></div>
        <div class="card"><h2>Automation</h2><p>Automation options</p></div>
        <div class="card"><h2>Limits</h2><p>Limits and scheduling</p></div>
    </div>
    """
    return base_template(content)

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
            <div class="option">
                <input type="checkbox" name="close_ticket" {} id="c1">
                <label for="c1">Close Ticket (keep channel)</label>
            </div>
            <div class="option">
                <input type="checkbox" name="close_and_delete" {} id="c2">
                <label for="c2">Close & Delete Ticket</label>
            </div>

            <h2>Transcripts</h2>
            <div class="option">
                <input type="checkbox" name="save_transcript" {} id="t1">
                <label for="t1">Save Transcript when ticket is closed/deleted</label>
            </div>
            <input type="text" name="transcript_channel" value="{}" placeholder="Transcript Channel ID">

            <button type="submit" style="margin-top:30px;">Save All Changes</button>
        </form>
    </div>
    """.format(
        'checked' if settings.get("close_ticket") else '',
        'checked' if settings.get("close_and_delete") else '',
        'checked' if settings.get("save_transcript") else '',
        settings.get("transcript_channel", "")
    )
    return base_template(content, "General Settings", show_back=True)

@app.route("/<path:path>")
def catch_all(path):
    return redirect("/dashboard")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)