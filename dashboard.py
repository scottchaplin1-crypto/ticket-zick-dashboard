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
        <div style="text-align:center; margin:15px 0 30px 0;">
            <button onclick="window.location='/dashboard'" 
                    style="background:linear-gradient(45deg,#00f0ff,#c026d3); color:black; padding:16px 40px; 
                           border:none; border-radius:12px; cursor:pointer; font-size:18px; font-weight:bold;">
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
            .header {{ text-align:center; margin-bottom:25px; }}
            .header-content {{ display:flex; align-items:center; justify-content:center; gap:20px; flex-wrap:wrap; }}
            .logo {{ 
                height:90px; 
                border-radius:16px; 
                box-shadow: 0 0 30px rgba(0, 240, 255, 0.7), 
                            0 0 50px rgba(192, 38, 211, 0.5);
                transition: all 0.3s ease;
            }}
            .logo:hover {{ 
                height:98px; 
                box-shadow: 0 0 40px rgba(0, 240, 255, 0.9), 
                            0 0 60px rgba(192, 38, 211, 0.7);
            }}
            .header-buttons {{ display:flex; justify-content:center; gap:12px; flex-wrap:wrap; align-items:center; }}
            .btn {{ background:linear-gradient(45deg,#00f0ff,#c026d3); color:black; padding:12px 24px; font-size:16px; border:none; border-radius:12px; cursor:pointer; }}
            .btn.invite {{ background:linear-gradient(45deg,#00ff88,#00f0ff); }}
            .add-btn {{ background:linear-gradient(45deg,#00f0ff,#c026d3); color:black; width:52px; height:52px; border-radius:50%; font-size:28px; border:none; cursor:pointer; display:flex; align-items:center; justify-content:center; box-shadow:0 4px 15px rgba(0,240,255,0.3); }}
            .grid {{ display:grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap:20px; max-width:1200px; margin:auto; }}
            .card {{ background:#1a1a2e; border-radius:16px; padding:25px; border:1px solid #00f0ff33; cursor:pointer; transition:0.3s; }}
            .card:hover {{ transform:scale(1.03); border-color:#c026d3; }}
            input, select {{ padding:12px; margin:8px 0; border-radius:10px; width:100%; background:#16213e; color:white; border:1px solid #334155; }}
            button {{ background:linear-gradient(45deg,#00f0ff,#c026d3); color:black; font-weight:bold; cursor:pointer; padding:14px; }}
            label {{ display:block; margin:20px 0 8px 0; font-weight:600; }}
        </style>
    </head>
    <body>
        <div class="header">
            <div class="header-content">
                <img src="/static/TicketZick.png" class="logo" alt="Ticket Zick">
                <h1>Ticket Zick Dashboard</h1>
            </div>
            <div class="header-buttons">
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

@app.route("/")
@app.route("/dashboard")
def dashboard():
    c.execute("SELECT id, name, emoji FROM panels ORDER BY name")
    panels = c.fetchall()
    options = ''.join([f'<option value="{p[0]}">{p[1]} {p[2]}</option>' for p in panels])

    content = f"""
    <div style="text-align:center; margin:30px 0;">
        <div style="display:flex; justify-content:center; gap:10px; align-items:center; max-width:600px; margin:auto;">
            <select onchange="if(this.value) window.location='/edit-panel/'+this.value" 
                    style="padding:14px; font-size:18px; background:#16213e; color:white; border:2px solid #00f0ff; border-radius:12px; flex:1;">
                <option value="">-- Select a Panel to Edit --</option>
                {options}
            </select>
            <button class="add-btn" onclick="window.location='/create-panel'" title="Create New Panel">+</button>
        </div>
    </div>

    <div style="text-align:center; margin:30px 0 15px; color:#00f0ff; font-size:22px;">General Ticket Options</div>
    <div class="grid">
        <div class="card"><h2>General</h2><p>Support team and general items</p></div>
        <div class="card"><h2>Category</h2><p>Category options for opened/closed tickets</p></div>
        <div class="card"><h2>Ticket</h2><p>General ticket options</p></div>
        <div class="card"><h2>Buttons</h2><p>Button text, colours & emojis</p></div>
    </div>

    <div style="text-align:center; margin:40px 0 15px; color:#00f0ff; font-size:22px;">Advanced Settings</div>
    <div class="grid">
        <div class="card"><h2>Forms</h2><p>Form options</p></div>
        <div class="card"><h2>Transcripts</h2><p>Transcript settings</p></div>
        <div class="card"><h2>Logging</h2><p>Server logging options</p></div>
        <div class="card"><h2>Automation</h2><p>Automation options</p></div>
    </div>
    """
    return base_template(content, show_back=False)

# ====================== CREATE + EDIT PANEL ROUTES ======================
@app.route("/create-panel")
def create_panel():
    # ... (same as before)
    content = """<h1>Create New Ticket Panel</h1> ... (your existing form)"""
    return base_template(content, show_back=True)

# Add your full create-panel, save-panel, edit-panel, update-panel, delete-panel routes here
# If you lost them, tell me and I'll send the complete version with everything.

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)