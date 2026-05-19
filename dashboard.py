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
            
            .top-bar {{ display: flex; justify-content: space-between; align-items: center; margin: 25px 0 45px; gap: 20px; }}
            .center-section {{ display: flex; align-items: center; gap: 12px; margin: 0 auto; }}
            .panel-selector {{ background:#16213e; border:2px solid #334155; color:#e0e0ff; padding:14px 20px; border-radius:12px; font-size:17px; min-width:380px; }}
            .add-btn {{ background:linear-gradient(45deg,#00f0ff,#c026d3); color:black; width:58px; height:58px; border-radius:50%; font-size:32px; border:none; cursor:pointer; }}
            
            .right-section {{ display: flex; flex-direction: column; align-items: flex-end; gap: 12px; }}
            button {{ padding:14px 32px; border:none; border-radius:12px; font-size:16px; font-weight:bold; cursor:pointer; }}
            .invite-btn {{ background:linear-gradient(45deg,#5865F2,#7289da); color:white; }}
            .send-btn {{ background:linear-gradient(45deg,#00ff88,#00cc66); color:black; }}
            .update-btn {{ background:linear-gradient(45deg,#ffaa00,#ff8800); color:black; }}
            
            .setting-card {{ background:#16213e; padding:32px 45px; border-radius:16px; margin:18px 0; border:1px solid #00f0ff22; }}
            .toggle-row {{ display: flex; align-items: center; justify-content: space-between; margin: 18px 0; min-height: 52px; }}
            .toggle-row label {{ flex: 1; font-size: 17px; color: #a0a0ff; font-weight: 600; padding-right: 60px; }}
            .toggle {{ accent-color: #00f0ff; transform: scale(1.7); }}
            
            .modal {{ display:none; position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.9); z-index:2000; }}
            .modal-content {{ background:#1a1a2e; padding:35px; border-radius:16px; width:90%; max-width:480px; margin:80px auto; }}
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
                <label style="display:block; margin:20px 0 8px;">Panel Name</label>
                <input type="text" id="newPanelName" value="New Support Panel" style="width:100%; padding:14px;"/>
                <div style="margin-top:30px;">
                    <button onclick="createNewPanel()" style="background:#00ff88; color:black;">Create</button>
                    <button onclick="closeCreateModal()" style="background:#334155; color:white; margin-left:12px;">Cancel</button>
                </div>
            </div>
        </div>

        <div id="toast" style="visibility:hidden; position:fixed; top:20px; right:20px; background:#00ff88; color:black; padding:16px 24px; border-radius:12px; font-weight:bold; z-index:3000;">
            ✅ Changes Saved!
        </div>

        <script>
            function showToast(msg) {{
                const t = document.getElementById('toast');
                t.textContent = msg;
                t.style.visibility = 'visible';
                setTimeout(() => t.style.visibility = 'hidden', 4000);
            }}
            function openCreatePanel() {{ document.getElementById('createPanelModal').style.display = 'block'; }}
            function closeCreateModal() {{ document.getElementById('createPanelModal').style.display = 'none'; }}
            function createNewPanel() {{
                showToast('✅ Panel Created!');
                closeCreateModal();
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
            <button class="invite-btn" onclick="window.open('https://discord.com/oauth2/authorize?client_id=1504522333208051872&scope=bot&permissions=8', '_blank')">Invite Ticket Zick</button>
            <div class="action-btns">
                <button class="send-btn" onclick="showToast('✅ Panel Sent!')">Send Panel</button>
                <button class="update-btn" onclick="showToast('✅ Panel Updated!')">Update Panel</button>
            </div>
        </div>
    </div>

    <h2 style="color:#c026d3; text-align:center; margin:40px 0 20px;">General Ticket Options</h2>
    <div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(260px,1fr)); gap:20px; max-width:1100px; margin:0 auto;">
        <div class="card" onclick="window.location='/settings/general'" style="background:#16213e; padding:25px; border-radius:12px; cursor:pointer;">
            <h3>General</h3><p>Support team and general items</p>
        </div>
        <div class="card" style="background:#16213e; padding:25px; border-radius:12px; cursor:pointer;"><h3>Category</h3><p>Category options</p></div>
        <div class="card" style="background:#16213e; padding:25px; border-radius:12px; cursor:pointer;"><h3>Ticket</h3><p>General ticket options</p></div>
        <div class="card" style="background:#16213e; padding:25px; border-radius:12px; cursor:pointer;"><h3>Panel</h3><p>Panel and button setup</p></div>
        <div class="card" style="background:#16213e; padding:25px; border-radius:12px; cursor:pointer;"><h3>Buttons</h3><p>Button text, colours & emojis</p></div>
    </div>
    """
    return base_template(content, show_back=False)

@app.route("/settings/general")
def settings_general():
    content = """
    <h1>General</h1>
    <div class="setting-card" style="background:#16213e; padding:32px; border-radius:16px; margin:20px auto; max-width:900px;">
        <h2>Support Team</h2>
        <label>Support Team Roles</label>
        <input type="text" value="Admin, Staff, Moderator, Helper" style="width:100%; padding:12px; margin:8px 0;" onchange="markChanged()">
    </div>
    <!-- More sections can be added later -->
    <button onclick="showToast('✅ Saved!')" style="padding:14px 40px; background:#00ff88; color:black; border:none; border-radius:12px; font-size:17px;">Save Changes</button>
    """
    return base_template(content, show_back=True, current_panel="Main Support Panel")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)