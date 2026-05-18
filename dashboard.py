from flask import Flask, request, redirect, render_template_string
import sqlite3
import os

app = Flask(__name__, static_folder='static')

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
conn.commit()

def base_template(content, title="Ticket Zick Dashboard", show_back=True):
    back_button = '''
        <div style="text-align:center; margin:20px 0;">
            <button onclick="window.location='/dashboard'" 
                    style="background:linear-gradient(45deg,#00f0ff,#c026d3); color:black; padding:14px 36px; 
                           border:none; border-radius:12px; cursor:pointer; font-size:17px; font-weight:bold;">
                ← Back to Dashboard
            </button>
        </div>
    ''' if show_back else ''

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>{title}</title>
        <style>
            body {{ background:#0a0a14; color:#e0e0ff; font-family:Segoe UI,sans-serif; margin:0; padding:20px; }}
            h1 {{ color:#00f0ff; text-align:center; margin:0; }}
            .header {{ text-align:center; margin-bottom:30px; }}
            .header-content {{ display:flex; align-items:center; justify-content:center; gap:20px; flex-wrap:wrap; }}
            .logo {{ height:80px; border-radius:16px; }}
            .btn {{ background:linear-gradient(45deg,#00f0ff,#c026d3); color:black; padding:12px 24px; font-size:16px; border:none; border-radius:12px; cursor:pointer; }}
            .btn.invite {{ background:linear-gradient(45deg,#00ff88,#00f0ff); }}
            .add-btn {{ background:linear-gradient(45deg,#00f0ff,#c026d3); color:black; width:52px; height:52px; border-radius:50%; font-size:28px; border:none; cursor:pointer; }}
            .grid {{ display:grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap:20px; max-width:1200px; margin:auto; }}
            .card {{ background:#1a1a2e; border-radius:16px; padding:25px; border:1px solid #00f0ff33; cursor:pointer; transition:0.3s; text-align:center; }}
            .card:hover {{ transform:scale(1.04); border-color:#c026d3; }}
            .card h2 {{ margin:0 0 10px 0; color:#00f0ff; }}
            .setting-card {{ background:#16213e; padding:20px; border-radius:12px; margin:15px 0; }}
        </style>
    </head>
    <body>
        <div class="header">
            <div class="header-content">
                <img src="/static/TicketZick.png" class="logo" alt="Ticket Zick">
                <h1>Ticket Zick Dashboard</h1>
            </div>
            <div style="margin-top:15px;">
                <a href="https://discord.com/oauth2/authorize?client_id=1504522333208051872&scope=bot+applications.commands&permissions=8" target="_blank">
                    <button class="btn invite">Invite Ticket Zick</button>
                </a>
            </div>
        </div>
        {back_button}
        {content}
    </body>
    </html>
    """

# ====================== MAIN DASHBOARD ======================
@app.route("/")
@app.route("/dashboard")
def dashboard():
    c.execute("SELECT id, name, emoji FROM panels ORDER BY name")
    panels = c.fetchall()
    options = ''.join([f'<option value="{p[0]}">{p[1]} {p[2]}</option>' for p in panels])

    content = f"""
    <div style="text-align:center; margin:30px 0 40px;">
        <div style="display:flex; justify-content:center; gap:12px; align-items:center; max-width:650px; margin:auto;">
            <select onchange="if(this.value) window.location='/edit-panel/'+this.value" 
                    style="padding:14px; font-size:18px; background:#16213e; color:white; border:2px solid #00f0ff; border-radius:12px; flex:1;">
                <option value="">-- Select a Panel to Edit --</option>
                {options}
            </select>
            <button class="add-btn" onclick="window.location='/create-panel'" title="Create New Panel">+</button>
        </div>
    </div>

    <h2 style="text-align:center; color:#00f0ff; margin:40px 0 20px;">General Ticket Options</h2>
    <div class="grid">
        <div class="card" onclick="window.location='/settings/general'"><h2>General</h2><p>Support team and general items</p></div>
        <div class="card" onclick="window.location='/settings/category'"><h2>Category</h2><p>Category options for opened/closed tickets</p></div>
        <div class="card" onclick="window.location='/settings/ticket'"><h2>Ticket</h2><p>General ticket options</p></div>
        <div class="card" onclick="window.location='/settings/buttons'"><h2>Buttons</h2><p>Button text, colours & emojis</p></div>
    </div>

    <h2 style="text-align:center; color:#00f0ff; margin:50px 0 20px;">Advanced Settings</h2>
    <div class="grid">
        <div class="card" onclick="window.location='/settings/forms'"><h2>Forms</h2><p>Form options</p></div>
        <div class="card" onclick="window.location='/settings/transcripts'"><h2>Transcripts</h2><p>Transcript settings</p></div>
        <div class="card" onclick="window.location='/settings/logging'"><h2>Logging</h2><p>Server logging options</p></div>
        <div class="card" onclick="window.location='/settings/automation'"><h2>Automation</h2><p>Automation options</p></div>
    </div>
    """
    return base_template(content, show_back=False)

# ====================== SETTINGS PAGES (with real options) ======================
@app.route("/settings/general")
def settings_general():
    content = """
    <h1>General Settings</h1>
    <div class="setting-card">
        <h2>Support Team Roles</h2>
        <p>Roles that can see and respond to tickets</p>
        <input type="text" placeholder="Admin, Staff, Moderator" style="width:100%; padding:12px;">
    </div>
    <div class="setting-card">
        <h2>Ticket Claiming</h2>
        <label><input type="checkbox" checked> Enable ticket claiming</label>
    </div>
    <div class="setting-card">
        <h2>Default Ticket Name</h2>
        <input type="text" value="ticket-{user}" style="width:100%; padding:12px;">
    </div>
    """
    return base_template(content)

@app.route("/settings/category")
def settings_category():
    content = """
    <h1>Category Settings</h1>
    <div class="setting-card">
        <h2>Open Tickets Category</h2>
        <input type="text" placeholder="Category ID" style="width:100%; padding:12px;">
    </div>
    <div class="setting-card">
        <h2>Closed Tickets Category</h2>
        <input type="text" placeholder="Category ID" style="width:100%; padding:12px;">
    </div>
    """
    return base_template(content)

@app.route("/settings/ticket")
def settings_ticket():
    content = """
    <h1>Ticket Settings</h1>
    <div class="setting-card">
        <h2>Welcome Message</h2>
        <textarea style="width:100%; height:100px;">👋 Welcome to your ticket! Staff will be here soon.</textarea>
    </div>
    <div class="setting-card">
        <h2>Auto Close After Inactivity</h2>
        <input type="number" value="48" style="width:100%; padding:12px;"> hours
    </div>
    """
    return base_template(content)

@app.route("/settings/buttons")
def settings_buttons():
    content = """
    <h1>Buttons Settings</h1>
    <div class="setting-card">
        <h2>Button Text</h2>
        <input type="text" value="Create Ticket" style="width:100%; padding:12px;">
    </div>
    <div class="setting-card">
        <h2>Button Color</h2>
        <div style="display:flex; gap:10px; flex-wrap:wrap;">
            <div style="background:#00f0ff; width:50px; height:50px; border-radius:8px; cursor:pointer;"></div>
            <div style="background:#c026d3; width:50px; height:50px; border-radius:8px; cursor:pointer;"></div>
            <div style="background:#ff0088; width:50px; height:50px; border-radius:8px; cursor:pointer;"></div>
        </div>
    </div>
    """
    return base_template(content)

@app.route("/settings/forms")
def settings_forms():
    content = "<h1>Forms</h1><p>Custom modal forms for opening tickets (coming next).</p>"
    return base_template(content)

@app.route("/settings/transcripts")
def settings_transcripts():
    content = "<h1>Transcripts</h1><p>Save transcripts to channel, HTML format, etc.</p>"
    return base_template(content)

@app.route("/settings/logging")
def settings_logging():
    content = "<h1>Logging</h1><p>Log channel for ticket events.</p>"
    return base_template(content)

@app.route("/settings/automation")
def settings_automation():
    content = "<h1>Automation</h1><p>Auto close, reactions, welcome DMs, etc.</p>"
    return base_template(content)

# Keep your existing create-panel / edit-panel routes here if you want them

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)