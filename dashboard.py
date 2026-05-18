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
            <button onclick="handleBack()" 
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
            .header-content {{ display:flex; align-items:center; justify-content:center; gap:20px; }}
            .logo {{ height:80px; border-radius:16px; }}
            .btn {{ background:linear-gradient(45deg,#00f0ff,#c026d3); color:black; padding:12px 24px; font-size:16px; border:none; border-radius:12px; cursor:pointer; }}
            .btn.invite {{ background:linear-gradient(45deg,#00ff88,#00f0ff); }}
            .add-btn {{ background:linear-gradient(45deg,#00f0ff,#c026d3); color:black; width:52px; height:52px; border-radius:50%; font-size:28px; border:none; cursor:pointer; }}
            .grid {{ display:grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap:20px; max-width:1300px; margin:auto; }}
            .card {{ background:#1a1a2e; border-radius:16px; padding:25px; border:1px solid #00f0ff33; cursor:pointer; transition:0.3s; text-align:center; }}
            .card:hover {{ transform:scale(1.04); border-color:#c026d3; }}
            .setting-card {{ background:#16213e; padding:25px; border-radius:16px; margin:20px 0; border:1px solid #00f0ff33; }}
            input, select, textarea {{ background:#0f0f1a; color:#e0e0ff; border:2px solid #334155; border-radius:10px; padding:12px; width:100%; font-size:16px; }}
            input:focus, select:focus, textarea:focus {{ border-color:#00f0ff; box-shadow:0 0 0 3px rgba(0,240,255,0.2); }}
            label {{ display:block; margin:12px 0 8px; font-weight:600; color:#a0a0ff; }}
            .toggle {{ accent-color:#00f0ff; transform:scale(1.4); }}
            .row {{ display:flex; align-items:center; justify-content:space-between; margin:12px 0; }}
            
            .save-btn {{ background:#334155; color:white; padding:14px 40px; border:none; border-radius:12px; font-size:17px; font-weight:bold; cursor:not-allowed; margin:30px auto; display:block; }}
            .save-btn.active {{ background:linear-gradient(45deg,#00ff88,#00f0ff); color:black; cursor:pointer; }}
            
            .modal {{ display:none; position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.9); z-index:1000; }}
            .modal-content {{ background:#1a1a2e; padding:35px; border-radius:16px; width:90%; max-width:420px; margin:120px auto; text-align:center; border:2px solid #00f0ff; }}
            .modal button {{ padding:14px 32px; margin:10px; border:none; border-radius:10px; font-size:16px; font-weight:bold; cursor:pointer; }}
            
            .tooltip {{ position:relative; display:inline-block; margin-left:8px; cursor:help; color:#00f0ff; }}
            .tooltip .tooltiptext {{ visibility:hidden; background:#16213e; color:#e0e0ff; text-align:left; border-radius:8px; padding:12px; position:absolute; z-index:1; bottom:125%; left:50%; transform:translateX(-50%); width:280px; box-shadow:0 0 15px rgba(0,240,255,0.3); }}
            .tooltip:hover .tooltiptext {{ visibility:visible; }}
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

        <div id="unsavedModal" class="modal">
            <div class="modal-content">
                <h2>You have unsaved changes</h2>
                <p style="margin:20px 0 30px;">What would you like to do?</p>
                <button onclick="saveAndExit()" style="background:#00ff88; color:black;">Save and Return</button>
                <button onclick="discardAndExit()" style="background:#ff4444; color:white;">Discard Changes</button>
                <button onclick="closeModal()" style="background:#334155; color:white;">Cancel (Stay Here)</button>
            </div>
        </div>

        <div id="toast" style="visibility:hidden; position:fixed; top:20px; right:20px; background:#00ff88; color:black; padding:16px 24px; border-radius:12px; font-weight:bold; box-shadow:0 4px 20px rgba(0,255,136,0.4); z-index:2000;">
            ✅ Changes Saved!
        </div>

        <script>
            let formChanged = false;

            function markChanged() {{
                formChanged = true;
                const saveBtn = document.getElementById('saveBtn');
                if (saveBtn) saveBtn.classList.add('active');
            }}

            function saveChanges() {{
                const toast = document.getElementById('toast');
                toast.style.visibility = 'visible';
                setTimeout(() => {{ toast.style.visibility = 'hidden'; }}, 5000);
                formChanged = false;
                const saveBtn = document.getElementById('saveBtn');
                if (saveBtn) saveBtn.classList.remove('active');
            }}

            function handleBack() {{
                if (formChanged) {{
                    document.getElementById('unsavedModal').style.display = 'block';
                }} else {{
                    window.location = '/dashboard';
                }}
            }}

            function saveAndExit() {{
                saveChanges();
                window.location = '/dashboard';
            }}

            function discardAndExit() {{
                window.location = '/dashboard';
            }}

            function closeModal() {{
                document.getElementById('unsavedModal').style.display = 'none';
            }}

            document.addEventListener('DOMContentLoaded', () => {{
                document.querySelectorAll('input, textarea, select').forEach(el => {{
                    el.addEventListener('change', markChanged);
                    el.addEventListener('input', markChanged);
                }});
            }});
        </script>
    </body>
    </html>
    """

# ====================== GENERAL MENU (Text Left, Checkbox Right) ======================
@app.route("/settings/general")
def settings_general():
    content = """
    <h1>General</h1>
    
    <div class="setting-card">
        <h2>Support Team</h2>
        <label>Support Team Roles</label>
        <input type="text" value="Admin, Staff, Moderator, Helper" placeholder="Comma separated roles" onchange="markChanged()">
    </div>

    <div class="setting-card">
        <h2>Ticket Claiming</h2>
        <div class="row" style="justify-content:space-between;">
            <label style="margin:0; font-size:17px;">Enable Ticket Claiming</label>
            <input type="checkbox" class="toggle" checked onchange="markChanged()">
        </div>
        <p style="color:#888; margin-top:8px;">Users with support roles can claim tickets</p>
    </div>

    <div class="setting-card">
        <h2>Default Ticket Name</h2>
        <label>Ticket Channel Name Format 
            <span class="tooltip">ℹ️
                <span class="tooltiptext">
                    Available placeholders:<br>
                    • {user} → User's name<br>
                    • {mention} → @User mention<br>
                    • {server} → Server name<br>
                    • {ticket} → Ticket number<br>
                    • {username} → Full username
                </span>
            </span>
        </label>
        <input type="text" value="ticket-{username}" style="font-family: monospace;" onchange="markChanged()">
    </div>

    <div class="setting-card">
        <h2>Permissions</h2>
        <div class="row" style="justify-content:space-between;">
            <label style="margin:0;">Mention Support Team when ticket opens</label>
            <input type="checkbox" class="toggle" checked onchange="markChanged()">
        </div>
        <div class="row" style="justify-content:space-between;">
            <label style="margin:0;">Allow users to view their own ticket history</label>
            <input type="checkbox" class="toggle" checked onchange="markChanged()">
        </div>
    </div>

    <div class="setting-card">
        <h2>Other Options</h2>
        <div class="row" style="justify-content:space-between;">
            <label style="margin:0;">Delete ticket channel when closed</label>
            <input type="checkbox" class="toggle" onchange="markChanged()">
        </div>
        <div class="row" style="justify-content:space-between;">
            <label style="margin:0;">Send transcript when ticket is closed</label>
            <input type="checkbox" class="toggle" checked onchange="markChanged()">
        </div>
    </div>

    <button id="saveBtn" class="save-btn" onclick="saveChanges()">Save Changes</button>
    """
    return base_template(content)

# Other menus (unchanged)
@app.route("/settings/category")
def settings_category():
    content = """<h1>Category</h1><div class="setting-card"><label>Open Tickets Category ID</label><input type="text" placeholder="Category ID"></div><div class="setting-card"><label>Closed Tickets Category ID</label><input type="text" placeholder="Category ID"></div>"""
    return base_template(content)

@app.route("/settings/ticket")
def settings_ticket():
    content = """<h1>Ticket</h1><div class="setting-card"><label>Welcome Message</label><textarea style="height:120px;">👋 Welcome to your ticket! Staff will be with you shortly.</textarea></div><div class="setting-card"><label>Auto Close After (hours)</label><input type="number" value="48"></div>"""
    return base_template(content)

@app.route("/settings/panel")
def settings_panel():
    content = """<h1>Panel</h1><div class="setting-card"><label>Panel Name</label><input type="text" value="Support"></div><div class="setting-card"><label>Panel Description</label><input type="text" value="Click to open a ticket"></div>"""
    return base_template(content)

@app.route("/settings/buttons")
def settings_buttons():
    content = """<h1>Buttons</h1><div class="setting-card"><label>Button Text</label><input type="text" value="Create Ticket"></div><div class="setting-card"><label>Button Color</label><div style="display:flex; gap:15px; flex-wrap:wrap;"><div style="background:#00f0ff;width:60px;height:60px;border-radius:12px;cursor:pointer;border:3px solid white;"></div><div style="background:#c026d3;width:60px;height:60px;border-radius:12px;cursor:pointer;"></div><div style="background:#ff0088;width:60px;height:60px;border-radius:12px;cursor:pointer;"></div></div></div>"""
    return base_template(content)

@app.route("/settings/commandstyle")
def settings_commandstyle():
    content = """<h1>Command Style</h1><div class="setting-card"><label><input type="checkbox" class="toggle" checked> Enable Slash Commands</label></div>"""
    return base_template(content)

@app.route("/settings/dropdownstyle")
def settings_dropdownstyle():
    content = """<h1>Dropdown Style</h1><div class="setting-card"><label><input type="checkbox" class="toggle" checked> Use Dropdown Menu</label></div>"""
    return base_template(content)

@app.route("/settings/forms")
def settings_forms():
    content = """<h1>Forms</h1><div class="setting-card"><label><input type="checkbox" class="toggle" checked> Enable Custom Forms</label></div>"""
    return base_template(content)

@app.route("/settings/transcripts")
def settings_transcripts():
    content = """<h1>Transcripts</h1><div class="setting-card"><label><input type="checkbox" class="toggle" checked> Save Transcripts</label></div><div class="setting-card"><label>Transcript Channel ID</label><input type="text"></div>"""
    return base_template(content)

@app.route("/settings/logging")
def settings_logging():
    content = """<h1>Logging</h1><div class="setting-card"><label>Log Channel ID</label><input type="text"></div><div class="setting-card"><label><input type="checkbox" class="toggle" checked> Log Ticket Events</label></div>"""
    return base_template(content)

@app.route("/settings/automation")
def settings_automation():
    content = """<h1>Automation</h1><div class="setting-card"><label><input type="checkbox" class="toggle"> Auto Close Inactive Tickets</label></div><div class="setting-card"><label><input type="checkbox" class="toggle"> Send Welcome DM</label></div>"""
    return base_template(content)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)