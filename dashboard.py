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
conn.commit()

def base_template(content, title="Ticket Zick Dashboard", show_back=True):
    back_button = '''
        <div style="text-align:center; margin:20px 0 35px 0;">
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
            body {{ background:#0a0a14; color:#e0e0ff; font-family:Segoe UI,sans-serif; margin:0; padding:30px 20px; }}
            h1 {{ color:#00f0ff; text-align:center; font-size:42px; margin-bottom:10px; letter-spacing:1px; }}
            .header-buttons {{ display:flex; justify-content:center; gap:15px; flex-wrap:wrap; margin-bottom:40px; }}
            .btn {{ background:linear-gradient(45deg,#00f0ff,#c026d3); color:black; padding:16px 32px; font-size:18px; border:none; border-radius:12px; cursor:pointer; font-weight:600; transition:0.3s; }}
            .btn:hover {{ transform:scale(1.05); }}
            .btn.invite {{ background:linear-gradient(45deg,#00ff88,#00f0ff); }}

            .panel-selector {{ display:flex; align-items:center; gap:12px; justify-content:center; margin:40px 0 50px; }}
            select {{ padding:16px 20px; font-size:18px; background:#16213e; color:white; border:2px solid #00f0ff; border-radius:12px; width:420px; cursor:pointer; }}
            .add-btn {{ background:#22c55e; color:black; width:56px; height:56px; border-radius:50%; font-size:28px; display:flex; align-items:center; justify-content:center; cursor:pointer; transition:0.3s; }}
            .add-btn:hover {{ transform:scale(1.1); background:#4ade80; }}

            .section-title {{ text-align:center; color:#00f0ff; font-size:24px; margin:50px 0 20px; letter-spacing:1px; }}
            .grid {{ display:grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap:20px; max-width:1300px; margin:auto; }}
            .card {{ 
                background:#1a1a2e; border-radius:16px; padding:28px; border:1px solid #334155; 
                cursor:pointer; transition:0.4s; box-shadow:0 4px 15px rgba(0,0,0,0.3);
            }}
            .card:hover {{ 
                transform:translateY(-8px); border-color:#00f0ff; box-shadow:0 10px 25px rgba(0,240,255,0.2);
            }}
            .card h2 {{ color:#00f0ff; margin:0 0 8px 0; font-size:22px; }}
            .card p {{ color:#a0a0cc; margin:0; }}
        </style>
    </head>
    <body>
        <div class="header-buttons">
            <a href="https://discord.com/oauth2/authorize?client_id=1504522333208051872&scope=bot+applications.commands&permissions=8" target="_blank">
                <button class="btn invite">➕ Invite Ticket Zick to Your Server</button>
            </a>
            <button class="btn" onclick="window.location='/create-panel'">+ Create New Ticket Panel</button>
        </div>

        <div class="panel-selector">
            <select onchange="if(this.value) window.location='/edit-panel/'+this.value">
                <option value="">-- Select a Panel to Edit --</option>
                {get_panel_options()}
            </select>
            <div class="add-btn" onclick="window.location='/create-panel'">+</div>
        </div>

        {content}
    </body>
    </html>
    """

def get_panel_options():
    c.execute("SELECT id, name, emoji FROM panels ORDER BY name")
    panels = c.fetchall()
    return ''.join([f'<option value="{p[0]}">{p[1]} {p[2]}</option>' for p in panels])

@app.route("/")
@app.route("/dashboard")
def dashboard():
    content = """
    <div class="section-title">General Ticket Options</div>
    <div class="grid">
        <div class="card"><h2>General</h2><p>Support team and general items</p></div>
        <div class="card"><h2>Category</h2><p>Category options for opened/closed tickets</p></div>
        <div class="card"><h2>Ticket</h2><p>General ticket options</p></div>
        <div class="card"><h2>Buttons</h2><p>Button text, colours & emojis</p></div>
    </div>

    <div class="section-title">Advanced Settings</div>
    <div class="grid">
        <div class="card"><h2>Forms</h2><p>Form options</p></div>
        <div class="card"><h2>Transcripts</h2><p>Transcript settings</p></div>
        <div class="card"><h2>Logging</h2><p>Server logging options</p></div>
        <div class="card"><h2>Automation</h2><p>Automation options</p></div>
        <div class="card"><h2>Limits</h2><p>Ticket limits</p></div>
    </div>
    """
    return base_template(content, show_back=False)

# Keep your existing create/edit/save/delete routes (unchanged as requested)
# ... paste them here from previous version ...

@app.route("/<path:path>")
def catch_all(path):
    return redirect("/dashboard")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)