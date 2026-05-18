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
        <div style="text-align:center; margin:25px 0;">
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
            h1, h2 {{ color:#00f0ff; }}
            .header {{ text-align:center; margin-bottom:30px; }}
            .header-content {{ display:flex; align-items:center; justify-content:center; gap:20px; flex-wrap:wrap; }}
            .logo {{ height:80px; border-radius:16px; }}
            .btn {{ background:linear-gradient(45deg,#00f0ff,#c026d3); color:black; padding:12px 24px; font-size:16px; border:none; border-radius:12px; cursor:pointer; }}
            .btn.invite {{ background:linear-gradient(45deg,#00ff88,#00f0ff); }}
            .add-btn {{ background:linear-gradient(45deg,#00f0ff,#c026d3); color:black; width:52px; height:52px; border-radius:50%; font-size:28px; border:none; cursor:pointer; }}
            .grid {{ display:grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap:20px; max-width:1200px; margin:auto; }}
            .card {{ 
                background:#1a1a2e; border-radius:16px; padding:25px; border:1px solid #00f0ff33; 
                cursor:pointer; transition:0.3s; text-align:center;
            }}
            .card:hover {{ transform:scale(1.04); border-color:#c026d3; }}
            .setting-card {{ 
                background:#16213e; padding:25px; border-radius:16px; margin:20px 0; 
                border:1px solid #00f0ff33;
            }}
            input, select, textarea {{ 
                background:#0f0f1a; color:#e0e0ff; border:2px solid #334155; 
                border-radius:10px; padding:12px; width:100%; font-size:16px;
            }}
            input:focus, select:focus, textarea:focus {{ 
                border-color:#00f0ff; outline:none; box-shadow:0 0 0 3px rgba(0,240,255,0.2);
            }}
            label {{ display:block; margin:15px 0 8px; font-weight:600; color:#a0a0ff; }}
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

# Main Dashboard
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

    <h2 style="text-align:center; margin:40px 0 20px;">General Ticket Options</h2>
    <div class="grid">
        <div class="card" onclick="window.location='/settings/general'"><h2>General</h2><p>Support team and general items</p></div>
        <div class="card" onclick="window.location='/settings/category'"><h2>Category</h2><p>Category options for opened/closed tickets</p></div>
        <div class="card" onclick="window.location='/settings/ticket'"><h2>Ticket</h2><p>General ticket options</p></div>
        <div class="card" onclick="window.location='/settings/buttons'"><h2>Buttons</h2><p>Button text, colours & emojis</p></div>
    </div>

    <h2 style="text-align:center; margin:50px 0 20px;">Advanced Settings</h2>
    <div class="grid">
        <div class="card" onclick="window.location='/settings/forms'"><h2>Forms</h2><p>Form options</p></div>
        <div class="card" onclick="window.location='/settings/transcripts'"><h2>Transcripts</h2><p>Transcript settings</p></div>
        <div class="card" onclick="window.location='/settings/logging'"><h2>Logging</h2><p>Server logging options</p></div>
        <div class="card" onclick="window.location='/settings/automation'"><h2>Automation</h2><p>Automation options</p></div>
    </div>
    """
    return base_template(content, show_back=False)

# ====================== FULL SUB MENUS ======================
@app.route("/settings/general")
def settings_general():
    content = """
    <h1>General</h1>
    <div class="setting-card">
        <label>Support Team Roles (who can view & respond to tickets)</label>
        <input type="text" value="Admin, Staff, Moderator" placeholder="Comma separated roles">
    </div>
    <div class="setting-card">
        <label><input type="checkbox" checked> Allow users to claim tickets</label>
    </div>
    <div class="setting-card">
        <label>Default Ticket Prefix</label>
        <input type="text" value="ticket-" style="width:100%;">
    </div>
    """
    return base_template(content)

@app.route("/settings/category")
def settings_category():
    content = """
    <h1>Category</h1>
    <div class="setting-card">
        <label>Open Tickets Category ID</label>
        <input type="text" placeholder="123456789012345678">
    </div>
    <div class="setting-card">
        <label>Closed Tickets Category ID</label>
        <input type="text" placeholder="123456789012345678">
    </div>
    """
    return base_template(content)

@app.route("/settings/ticket")
def settings_ticket():
    content = """
    <h1>Ticket</h1>
    <div class="setting-card">
        <label>Welcome Message in Ticket</label>
        <textarea style="height:120px;">👋 Welcome to your ticket! {user} Staff will be here soon.</textarea>
    </div>
    <div class="setting-card">
        <label>Auto-close after inactivity (hours)</label>
        <input type="number" value="48">
    </div>
    """
    return base_template(content)

@app.route("/settings/buttons")
def settings_buttons():
    content = """
    <h1>Buttons</h1>
    <div class="setting-card">
        <label>Button Text</label>
        <input type="text" value="Create Ticket">
    </div>
    <div class="setting-card">
        <label>Button Color</label>
        <div style="display:flex; gap:12px; flex-wrap:wrap;">
            <div style="background:#00f0ff;width:50px;height:50px;border-radius:10px;cursor:pointer;border:3px solid #00f0ff;"></div>
            <div style="background:#c026d3;width:50px;height:50px;border-radius:10px;cursor:pointer;"></div>
            <div style="background:#ff0088;width:50px;height:50px;border-radius:10px;cursor:pointer;"></div>
            <div style="background:#00ff88;width:50px;height:50px;border-radius:10px;cursor:pointer;"></div>
        </div>
    </div>
    """
    return base_template(content)

@app.route("/settings/forms")
def settings_forms():
    content = "<h1>Forms</h1><div class='setting-card'><p>Custom form fields for opening tickets (Modal support)</p></div>"
    return base_template(content)

@app.route("/settings/transcripts")
def settings_transcripts():
    content = """
    <h1>Transcripts</h1>
    <div class="setting-card">
        <label><input type="checkbox" checked> Save transcripts when ticket closes</label>
    </div>
    <div class="setting-card">
        <label>Transcript Log Channel ID</label>
        <input type="text" placeholder="Channel ID">
    </div>
    """
    return base_template(content)

@app.route("/settings/logging")
def settings_logging():
    content = """
    <h1>Logging</h1>
    <div class="setting-card">
        <label>Log Channel ID</label>
        <input type="text" placeholder="Channel ID">
    </div>
    <div class="setting-card">
        <label><input type="checkbox" checked> Log when tickets are created</label><br>
        <label><input type="checkbox" checked> Log when tickets are closed</label>
    </div>
    """
    return base_template(content)

@app.route("/settings/automation")
def settings_automation():
    content = """
    <h1>Automation</h1>
    <div class="setting-card">
        <label><input type="checkbox"> Auto close inactive tickets</label>
    </div>
    <div class="setting-card">
        <label><input type="checkbox"> Send welcome DM to user</label>
    </div>
    """
    return base_template(content)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)