from flask import Flask, render_template_string
import sqlite3
import os

app = Flask(__name__, static_folder='static')

conn = sqlite3.connect("config.db", check_same_thread=False)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS panels (
    id INTEGER PRIMARY KEY,
    name TEXT UNIQUE,
    emoji TEXT DEFAULT '🎟️',
    category_id TEXT,
    description TEXT,
    support_roles TEXT,
    button_text TEXT DEFAULT 'Create Ticket',
    button_color TEXT DEFAULT '#00f0ff'
)''')
conn.commit()

def base_template(content, title="Ticket Zick Dashboard", show_back=True, current_panel=None):
    back_button = '''
        <div style="text-align:center; margin:25px 0;">
            <button onclick="handleBack()" style="background:linear-gradient(45deg,#00f0ff,#c026d3); color:black; padding:14px 36px; border:none; border-radius:12px; cursor:pointer; font-size:17px; font-weight:bold;">
                ← Back to Dashboard
            </button>
        </div>
    ''' if show_back else ''

    panel_header = f'<h2 style="color:#c026d3; text-align:center; margin:20px 0 30px;">Editing: <span style="color:#00f0ff;">{current_panel}</span></h2>' if show_back and current_panel else ''

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
            .logo {{ height:90px; border-radius:16px; }}
            .panel-area {{ display:flex; justify-content:center; align-items:center; gap:12px; margin:30px 0; }}
            .panel-selector {{ background:#16213e; border:2px solid #334155; color:#e0e0ff; padding:14px 20px; border-radius:12px; font-size:17px; width:380px; }}
            .add-btn {{ background:linear-gradient(45deg,#00f0ff,#c026d3); color:black; width:52px; height:52px; border-radius:50%; font-size:28px; border:none; cursor:pointer; }}
            .setting-card {{ background:#16213e; padding:32px 40px; border-radius:16px; margin:18px 0; border:1px solid #00f0ff22; }}
            input, select, textarea {{ background:#0f0f1a; color:#e0e0ff; border:2px solid #334155; border-radius:10px; padding:12px 18px; width:100%; font-size:16px; margin-top:8px; box-sizing:border-box; }}
            input:focus, select:focus, textarea:focus {{ border-color:#00f0ff; box-shadow:0 0 0 3px rgba(0,240,255,0.2); }}
            label {{ 
                display:block; 
                margin:14px 0 8px; 
                font-weight:600; 
                color:#a0a0ff; 
                font-size:17px;
                line-height:1.4;
            }}
            .toggle {{ accent-color:#00f0ff; transform:scale(1.5); }}
            .row {{ 
                display:flex; 
                align-items:center; 
                gap:20px; 
                margin:20px 0; 
            }}
            .row label {{ 
                margin:0; 
                flex:1; 
            }}
            .save-btn {{ 
                background:#334155; 
                color:white; 
                padding:14px 40px; 
                border:none; 
                border-radius:12px; 
                font-size:17px; 
                font-weight:bold; 
                cursor:not-allowed; 
                margin:40px auto; 
                display:block; 
            }}
            .save-btn.active {{ background:linear-gradient(45deg,#00ff88,#00f0ff); color:black; cursor:pointer; }}
            .modal {{ display:none; position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.9); z-index:1000; }}
            .modal-content {{ background:#1a1a2e; padding:35px; border-radius:16px; width:90%; max-width:420px; margin:120px auto; text-align:center; border:2px solid #00f0ff; }}
            .modal button {{ padding:14px 32px; margin:10px; border:none; border-radius:10px; font-size:16px; font-weight:bold; cursor:pointer; }}
            .tooltip {{ position:relative; display:inline-block; margin-left:8px; cursor:help; color:#00f0ff; }}
            .tooltip .tooltiptext {{ visibility:hidden; background:#16213e; color:#e0e0ff; text-align:left; border-radius:8px; padding:12px; position:absolute; z-index:1; bottom:125%; left:50%; transform:translateX(-50%); width:280px; box-shadow:0 0 15px rgba(0,240,255,0.3); }}
            .tooltip:hover .tooltiptext {{ visibility:visible; }}
            .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 22px; max-width: 1150px; margin: 30px auto; }}
            .card {{ background: linear-gradient(145deg, #16213e, #0f1629); border-radius:16px; padding:28px 20px; text-align:center; border:1px solid #00f0ff33; cursor:pointer; transition:0.3s; box-shadow:0 4px 15px rgba(0,0,0,0.4); }}
            .card:hover {{ transform:scale(1.06); border-color:#c026d3; box-shadow:0 0 25px rgba(192,38,211,0.5); }}
            .card h3 {{ margin:0 0 8px 0; color:#00f0ff; }}
            .card p {{ margin:0; color:#888; font-size:14px; }}
        </style>
    </head>
    <body>
        <div class="header">
            <div class="header-content">
                <img src="/static/TicketZick.png" class="logo" alt="Ticket Zick">
                <h1>Ticket Zick Dashboard</h1>
            </div>
        </div>
        {back_button}
        {panel_header}
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
                document.getElementById('saveBtn').classList.add('active'); 
            }}
            function saveChanges() {{ 
                const toast = document.getElementById('toast'); 
                toast.style.visibility = 'visible';
                setTimeout(() => {{ toast.style.visibility = 'hidden'; }}, 4000);
                formChanged = false; 
                document.getElementById('saveBtn').classList.remove('active');
            }}
            function handleBack() {{
                if (formChanged) {{ 
                    document.getElementById('unsavedModal').style.display = 'block'; 
                }} else {{ 
                    window.location = '/dashboard'; 
                }}
            }}
            function saveAndExit() {{ saveChanges(); window.location = '/dashboard'; }}
            function discardAndExit() {{ window.location = '/dashboard'; }}
            function closeModal() {{ document.getElementById('unsavedModal').style.display = 'none'; }}
        </script>
    </body>
    </html>
    """

# ====================== GENERAL MENU (Fixed stacking + clean layout) ======================
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
        <div class="row">
            <label>Enable Ticket Claiming</label>
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
        <div class="row">
            <label>Mention Support Team when ticket opens</label>
            <input type="checkbox" class="toggle" checked onchange="markChanged()">
        </div>
    </div>

    <div class="setting-card">
        <h2>Permissions</h2>
        <div class="row">
            <label>Allow users to view their own ticket history</label>
            <input type="checkbox" class="toggle" checked onchange="markChanged()">
        </div>
    </div>

    <div class="setting-card">
        <h2>Other Options</h2>
        <div class="row">
            <label>Delete ticket channel when closed</label>
            <input type="checkbox" class="toggle" onchange="markChanged()">
        </div>
    </div>

    <div class="setting-card">
        <h2>Other Options</h2>
        <div class="row">
            <label>Send transcript when ticket is closed</label>
            <input type="checkbox" class="toggle" checked onchange="markChanged()">
        </div>
    </div>

    <button id="saveBtn" class="save-btn" onclick="saveChanges()">Save Changes</button>
    """
    return base_template(content, show_back=True, current_panel="Main Support Panel")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)