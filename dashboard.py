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
            h1 {{ color:#00f0ff; text-align:center; }}
            .header {{ text-align:center; margin-bottom:20px; }}
            .header-buttons {{ display:flex; justify-content:center; gap:15px; flex-wrap:wrap; align-items:center; }}
            .btn {{ background:linear-gradient(45deg,#00f0ff,#c026d3); color:black; padding:16px 32px; font-size:18px; border:none; border-radius:12px; cursor:pointer; min-width:280px; }}
            .btn.invite {{ background:linear-gradient(45deg,#00ff88,#00f0ff); }}
            .panel-selector {{ display:flex; align-items:center; gap:10px; justify-content:center; margin:30px 0; }}
            select {{ padding:14px; font-size:18px; background:#16213e; color:white; border:2px solid #00f0ff; border-radius:12px; width:400px; }}
            .add-btn {{ background:#22c55e; color:black; width:50px; height:50px; border-radius:50%; font-size:24px; display:flex; align-items:center; justify-content:center; cursor:pointer; }}
            .grid {{ display:grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap:20px; max-width:1200px; margin:auto; }}
            .card {{ background:#1a1a2e; border-radius:16px; padding:25px; border:1px solid #00f0ff33; cursor:pointer; transition:0.3s; }}
            .card:hover {{ transform:scale(1.03); border-color:#c026d3; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🎟️ Ticket Zick Dashboard</h1>
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
    <div class="section-title" style="text-align:center; margin:30px 0 15px; color:#00f0ff;">General Ticket Options</div>
    <div class="grid">
        <div class="card"><h2>General</h2><p>Support team and general items</p></div>
        <div class="card"><h2>Category</h2><p>Category options</p></div>
        <div class="card"><h2>Ticket</h2><p>General ticket options</p></div>
        <div class="card"><h2>Buttons</h2><p>Button text, colours & emojis</p></div>
    </div>

    <div class="section-title" style="text-align:center; margin:40px 0 15px; color:#00f0ff;">Advanced Settings</div>
    <div class="grid">
        <div class="card"><h2>Forms</h2><p>Form options</p></div>
        <div class="card"><h2>Transcripts</h2><p>Transcript settings</p></div>
        <div class="card"><h2>Logging</h2><p>Logging options</p></div>
        <div class="card"><h2>Automation</h2><p>Automation options</p></div>
        <div class="card"><h2>Limits</h2><p>Ticket limits</p></div>
    </div>
    """
    return base_template(content, show_back=False)

# Keep all your existing routes (create-panel, save-panel, edit-panel, etc.)
# Paste them here from the previous working version...

@app.route("/create-panel")
def create_panel():
    # Your existing create panel code (unchanged)
    content = """
    <h1>Create New Ticket Panel</h1>
    <div class="card">
        <form method="POST" action="/save-panel">
            <label>Panel Name</label>
            <input type="text" name="name" placeholder="e.g. Support, Bug Report" required>
            <!-- Rest of your create form -->
            <button type="submit" style="margin-top:30px; width:100%;">Create Panel</button>
        </form>
    </div>
    """
    return base_template(content, show_back=True)

# ... (add the rest of your save, edit, update, delete routes here) ...

@app.route("/<path:path>")
def catch_all(path):
    return redirect("/dashboard")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)