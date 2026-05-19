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
            .logo {{ height:85px; border-radius:16px; }}
            
            .top-bar {{ 
                display: flex; 
                align-items: center; 
                justify-content: center; 
                gap: 30px; 
                margin: 30px 0 50px; 
                max-width: 1350px; 
                margin-left: auto; 
                margin-right: auto;
            }}
            .center-section {{ display: flex; align-items: center; gap: 12px; }}
            .panel-selector {{ 
                background:#16213e; border:2px solid #334155; color:#e0e0ff; 
                padding:14px 20px; border-radius:12px; font-size:17px; min-width:380px; 
            }}
            .add-btn {{ 
                background:linear-gradient(45deg,#00f0ff,#c026d3); 
                color:black; 
                width:62px; height:62px; 
                border-radius:50%; 
                font-size:34px; 
                border:none; 
                cursor:pointer; 
                box-shadow: 0 0 25px rgba(0,240,255,0.7);
                display:flex; align-items:center; justify-content:center;
            }}
            
            .right-section {{ display: flex; flex-direction: column; align-items: flex-end; gap: 12px; }}
            .action-btns {{ display: flex; gap: 12px; }}
            
            .invite-img {{ 
                height: 72px; 
                border-radius:12px; 
                cursor:pointer; 
                box-shadow:0 0 25px rgba(0,240,255,0.5); 
                transition: all 0.3s;
            }}
            .invite-img:hover {{ 
                box-shadow:0 0 40px rgba(0,240,255,0.9); 
                transform: translateY(-3px); 
            }}
            
            button {{ 
                padding:16px 32px; border:none; border-radius:12px; 
                font-size:16px; font-weight:bold; cursor:pointer; 
                transition: all 0.3s; min-width: 170px;
            }}
            .send-btn {{ background:linear-gradient(45deg,#00ff88,#00cc66); color:black; }}
            .update-btn {{ background:linear-gradient(45deg,#ffaa00,#ff8800); color:black; }}
            button:hover {{ transform: translateY(-4px); box-shadow: 0 10px 30px rgba(0,240,255,0.5); }}
            
            .setting-card {{ background:#16213e; padding:32px 45px; border-radius:16px; margin:18px 0; border:1px solid #00f0ff22; }}
            .toggle-row {{ display: flex; align-items: center; justify-content: space-between; margin: 18px 0; min-height: 52px; }}
            .toggle-row label {{ flex: 1; font-size: 17px; color: #a0a0ff; font-weight: 600; line-height: 1.45; padding-right: 60px; }}
            .toggle {{ accent-color: #00f0ff; transform: scale(1.7); cursor: pointer; flex-shrink: 0; }}
            
            input {{ background:#0f0f1a; color:#e0e0ff; border:2px solid #334155; border-radius:10px; padding:12px 18px; width:100%; font-size:16px; margin-top:8px; }}
            
            .modal {{ display:none; position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.9); z-index:2000; }}
            .modal-content {{ background:#1a1a2e; padding:35px; border-radius:16px; width:90%; max-width:480px; margin:80px auto; }}
            
            #toast {{ visibility:hidden; position:fixed; top:20px; right:20px; background:#00ff88; color:black; padding:16px 24px; border-radius:12px; font-weight:bold; z-index:3000; box-shadow:0 0 20px #00ff88; }}
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

        <div id="createPanelModal" class="modal">
            <div class="modal-content">
                <h2 style="color:#00f0ff;">Create New Panel</h2>
                <p style="color:#888;">Give your new ticket panel a name.</p>
                <input type="text" id="newPanelName" value="Support Panel" style="width:100%; padding:14px; font-size:17px; margin:15px 0;"/>
                <div style="text-align:center; margin-top:20px;">
                    <button onclick="createNewPanel()" style="background:#00ff88; color:black; padding:14px 40px;">Create</button>
                    <button onclick="closeCreateModal()" style="background:#334155; color:white; padding:14px 40px; margin-left:12px;">Cancel</button>
                </div>
            </div>
        </div>

        <div id="toast">✅ Changes Saved!</div>

        <script>
            let formChanged = false;
            function markChanged() {{ formChanged = true; document.getElementById('saveBtn').classList.add('active'); }}
            function saveChanges() {{ 
                showToast('✅ Changes Saved!');
                formChanged = false;
                document.getElementById('saveBtn').classList.remove('active');
            }}
            function showToast(msg) {{
                const toast = document.getElementById('toast');
                toast.textContent = msg;
                toast.style.visibility = 'visible';
                setTimeout(() => toast.style.visibility = 'hidden', 4000);
            }}
            function openCreatePanel() {{ document.getElementById('createPanelModal').style.display = 'block'; }}
            function closeCreateModal() {{ document.getElementById('createPanelModal').style.display = 'none'; }}
            function createNewPanel() {{
                showToast('✅ New Panel Created!');
                closeCreateModal();
            }}
            function handleBack() {{
                if (formChanged) {{
                    if (confirm("You have unsaved changes!\\n\\nSave before leaving?")) saveChanges();
                }}
                window.location = '/dashboard';
            }}
        </script>
    </body>
    </html>
    """

@app.route("/")
@app.route("/dashboard")
def dashboard():
    content = """
    <div class="top-bar">
        <div class="center-section">
            <select class="panel-selector" onchange="if(this.value) window.location = '/settings/general'">
                <option value="" selected>-- Select a Panel to Edit --</option>
            </select>
            <button class="add-btn" onclick="openCreatePanel()">+</button>
        </div>
        
        <div class="right-section">
            <a href="https://discord.com/oauth2/authorize?client_id=1504522333208051872&scope=bot&permissions=8" target="_blank">
                <img src="/static/TicketZickButton.png" class="invite-img" alt="Invite Ticket Zick">
            </a>
            <div class="action-btns">
                <button class="send-btn" onclick="showToast('✅ Ticket Panel Sent to Discord!')">Send Panel</button>
                <button class="update-btn" onclick="showToast('✅ Existing Panel Updated!')">Update Panel</button>
            </div>
        </div>
    </div>

    <h2 style="color:#c026d3; text-align:center; margin:40px 0 20px;">General Ticket Options</h2>
    <div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(260px,1fr)); gap:20px; max-width:1100px; margin:0 auto;">
        <div onclick="window.location='/settings/general'" style="background:#16213e; padding:25px; border-radius:12px; cursor:pointer;">
            <h3>General</h3><p>Support team and general items</p>
        </div>
        <div style="background:#16213e; padding:25px; border-radius:12px; cursor:pointer;"><h3>Category</h3><p>Category options</p></div>
        <div style="background:#16213e; padding:25px; border-radius:12px; cursor:pointer;"><h3>Ticket</h3><p>General ticket options</p></div>
        <div style="background:#16213e; padding:25px; border-radius:12px; cursor:pointer;"><h3>Panel</h3><p>Panel and button setup</p></div>
        <div style="background:#16213e; padding:25px; border-radius:12px; cursor:pointer;"><h3>Buttons</h3><p>Button text, colours & emojis</p></div>
    </div>

    <h2 style="color:#c026d3; text-align:center; margin:50px 0 20px;">Advanced Settings</h2>
    <div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(260px,1fr)); gap:20px; max-width:1100px; margin:0 auto;">
        <div style="background:#16213e; padding:25px; border-radius:12px; cursor:pointer;"><h3>Command Style</h3><p>Slash command settings</p></div>
        <div style="background:#16213e; padding:25px; border-radius:12px; cursor:pointer;"><h3>Dropdown Style</h3><p>Dropdown menu options</p></div>
        <div style="background:#16213e; padding:25px; border-radius:12px; cursor:pointer;"><h3>Forms</h3><p>Form options</p></div>
        <div style="background:#16213e; padding:25px; border-radius:12px; cursor:pointer;"><h3>Transcripts</h3><p>Transcript settings</p></div>
        <div style="background:#16213e; padding:25px; border-radius:12px; cursor:pointer;"><h3>Logging</h3><p>Server logging options</p></div>
        <div style="background:#16213e; padding:25px; border-radius:12px; cursor:pointer;"><h3>Automation</h3><p>Automation options</p></div>
    </div>
    """
    return base_template(content, show_back=False)

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
        <div class="toggle-row">
            <label>Enable Ticket Claiming</label>
            <div style="flex-shrink:0;"><input type="checkbox" class="toggle" checked onchange="markChanged()"></div>
        </div>
    </div>

    <div class="setting-card">
        <h2>Default Ticket Name</h2>
        <label>Ticket Channel Name Format</label>
        <input type="text" value="ticket-{username}" style="font-family: monospace;" onchange="markChanged()">
    </div>

    <div class="setting-card">
        <h2>Permissions</h2>
        <div class="toggle-row">
            <label>Mention Support Team when ticket opens</label>
            <div style="flex-shrink:0;"><input type="checkbox" class="toggle" checked onchange="markChanged()"></div>
        </div>
    </div>

    <div class="setting-card">
        <h2>Other Options</h2>
        <div class="toggle-row">
            <label>Delete ticket channel when closed</label>
            <div style="flex-shrink:0;"><input type="checkbox" class="toggle" onchange="markChanged()"></div>
        </div>
    </div>

    <div class="setting-card">
        <h2>Other Options</h2>
        <div class="toggle-row">
            <label>Send transcript when ticket is closed</label>
            <div style="flex-shrink:0;"><input type="checkbox" class="toggle" checked onchange="markChanged()"></div>
        </div>
    </div>

    <button id="saveBtn" class="save-btn" onclick="saveChanges()">Save Changes</button>
    """
    return base_template(content, show_back=True, current_panel="Main Support Panel")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)