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
            h1 {{ color:#00f0ff; text-align:center; margin:0; }}
            .header {{ text-align:center; margin-bottom:25px; }}
            .header-content {{ display:flex; align-items:center; justify-content:center; gap:15px; flex-wrap:wrap; }}
            .logo {{ height:60px; border-radius:12px; }}
            .header-buttons {{ display:flex; justify-content:center; gap:12px; flex-wrap:wrap; align-items:center; }}
            .btn {{ background:linear-gradient(45deg,#00f0ff,#c026d3); color:black; padding:12px 24px; font-size:16px; border:none; border-radius:12px; cursor:pointer; }}
            .btn.invite {{ background:linear-gradient(45deg,#00ff88,#00f0ff); }}
            .add-btn {{ background:linear-gradient(45deg,#00f0ff,#c026d3); color:black; width:52px; height:52px; border-radius:50%; font-size:28px; border:none; cursor:pointer; display:flex; align-items:center; justify-content:center; box-shadow:0 4px 15px rgba(0,240,255,0.3); }}
            .grid {{ display:grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap:20px; max-width:1200px; margin:auto; }}
            .card {{ background:#1a1a2e; border-radius:16px; padding:25px; border:1px solid #00f0ff33; cursor:pointer; transition:0.3s; }}
            .card:hover {{ transform:scale(1.03); border-color:#c026d3; }}
            .panel-item {{ background:#16213e; padding:15px; border-radius:12px; margin:10px 0; display:flex; justify-content:space-between; align-items:center; }}
            input, select {{ padding:12px; margin:8px 0; border-radius:10px; width:100%; background:#16213e; color:white; border:1px solid #334155; }}
            button {{ background:linear-gradient(45deg,#00f0ff,#c026d3); color:black; font-weight:bold; cursor:pointer; padding:14px; }}
            label {{ display:block; margin:20px 0 8px 0; font-weight:600; }}
        </style>
    </head>
    <body>
        <div class="header">
            <div class="header-content">
                <img src="TicketZick.jpg" class="logo" alt="Ticket Zick">
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
        <label style="font-size:18px; color:#00f0ff;">Select Ticket Panel to Edit:</label><br><br>
        <div style="display:flex; justify-content:center; gap:10px; align-items:center; max-width:600px; margin:auto;">
            <select onchange="if(this.value) window.location='/edit-panel/'+this.value" 
                    style="padding:14px; font-size:18px; background:#16213e; color:white; border:2px solid #00f0ff; border-radius:12px; flex:1;">
                <option value="">-- Select a Panel to Edit --</option>
                {options}
            </select>
            <button class="add-btn" onclick="window.location='/create-panel'" title="Create New Panel">+</button>
        </div>
    </div>

    <div class="section-title" style="text-align:center; margin:30px 0 15px; color:#00f0ff;">General Ticket Options</div>
    <div class="grid">
        <div class="card"><h2>General</h2><p>Support team and general items</p></div>
        <div class="card"><h2>Category</h2><p>Category options for opened/closed tickets</p></div>
        <div class="card"><h2>Ticket</h2><p>General ticket options</p></div>
        <div class="card"><h2>Buttons</h2><p>Button text, colours & emojis</p></div>
    </div>

    <div class="section-title" style="text-align:center; margin:40px 0 15px; color:#00f0ff;">Advanced Settings</div>
    <div class="grid">
        <div class="card"><h2>Forms</h2><p>Form options</p></div>
        <div class="card"><h2>Transcripts</h2><p>Transcript settings</p></div>
        <div class="card"><h2>Logging</h2><p>Server logging options</p></div>
        <div class="card"><h2>Automation</h2><p>Automation options</p></div>
    </div>
    """
    return base_template(content, show_back=False)

# ====================== CREATE / EDIT / SAVE ======================
@app.route("/create-panel")
def create_panel():
    content = """
    <h1>Create New Ticket Panel</h1>
    <div class="card">
        <form method="POST" action="/save-panel">
            <label>1. Panel Name</label>
            <input type="text" name="name" placeholder="e.g. Support, Bug Report" required>

            <label>2. Emoji / Icon</label>
            <select name="emoji" id="emoji-select" onchange="updatePreview()">
                <option value="🎟️">🎟️ Ticket</option>
                <option value="❓">❓ Question</option>
                <option value="🚨">🚨 Report</option>
                <option value="💰">💰 Donation</option>
                <option value="🤝">🤝 Support</option>
                <option value="🛠️">🛠️ Technical</option>
                <option value="🎮">🎮 Gaming</option>
                <option value="📝">📝 Application</option>
                <option value="❤️">❤️ Help</option>
                <option value="⚠️">⚠️ Urgent</option>
                <option value="🔨">🔨 Ban Appeal</option>
                <option value="💸">💸 Payment</option>
                <option value="🎉">🎉 Event</option>
                <option value="📢">📢 Announcement</option>
                <option value="🐛">🐛 Bug Report</option>
                <option value="🔥">🔥 Important</option>
            </select>

            <label>3. Button Text</label>
            <input type="text" name="button_text" id="button-text" value="Create Ticket" onkeyup="updatePreview()">

            <label>4. Button Color</label>
            <div style="margin:10px 0;">
                <span class="color-box" style="background:#00f0ff" onclick="setColor('#00f0ff')"></span>
                <span class="color-box" style="background:#c026d3" onclick="setColor('#c026d3')"></span>
                <span class="color-box" style="background:#ff00ff" onclick="setColor('#ff00ff')"></span>
                <span class="color-box" style="background:#00ff88" onclick="setColor('#00ff88')"></span>
                <span class="color-box" style="background:#ff8800" onclick="setColor('#ff8800')"></span>
                <span class="color-box" style="background:#ffff00" onclick="setColor('#ffff00')"></span>
                <span class="color-box" style="background:#ff0088" onclick="setColor('#ff0088')"></span>
                <span class="color-box" style="background:#ff4444" onclick="setColor('#ff4444')"></span>
                <span class="color-box" style="background:#44ff44" onclick="setColor('#44ff44')"></span>
            </div>

            <label>5. Description</label>
            <input type="text" name="description" value="Our team will assist you shortly.">

            <label>6. Category ID</label>
            <input type="text" name="category_id" placeholder="123456789012345678" required>

            <label>7. Support Roles</label>
            <input type="text" name="support_roles" placeholder="Staff, Admin, Moderator">

            <button type="submit" style="margin-top:30px; width:100%;">Create This Ticket Panel</button>
        </form>

        <h3>Live Button Preview</h3>
        <div id="preview" style="padding:25px; background:#0f0f1a; border-radius:12px; text-align:center; font-size:22px;">
            🎟️ Create Ticket
        </div>
    </div>

    <script>
        function updatePreview() {
            const emoji = document.getElementById('emoji-select').value || '🎟️';
            const text = document.getElementById('button-text').value || 'Create Ticket';
            document.getElementById('preview').innerHTML = emoji + ' ' + text;
        }
        function setColor(color) {
            document.querySelectorAll('.color-box').forEach(b => b.classList.remove('selected'));
            event.currentTarget.classList.add('selected');
            updatePreview();
        }
        setTimeout(updatePreview, 300);
    </script>
    """
    return base_template(content, show_back=True)

# Save, Edit, Update, Delete routes
@app.route("/save-panel", methods=["POST"])
def save_panel():
    c.execute("""INSERT INTO panels (name, emoji, category_id, description, support_roles, button_text, button_color)
                 VALUES (?, ?, ?, ?, ?, ?, ?)""", (
        request.form.get("name"), request.form.get("emoji"), request.form.get("category_id"),
        request.form.get("description"), request.form.get("support_roles"),
        request.form.get("button_text"), request.form.get("button_color")
    ))
    conn.commit()
    return redirect("/dashboard")

@app.route("/edit-panel/<int:panel_id>")
def edit_panel(panel_id):
    c.execute("SELECT * FROM panels WHERE id = ?", (panel_id,))
    panel = c.fetchone()
    if not panel: return redirect("/dashboard")

    current_color = panel[7] or '#00f0ff'

    content = f"""
    <h1>Edit Ticket Panel</h1>
    <div class="card">
        <form method="POST" action="/update-panel/{panel[0]}">
            <label>1. Panel Name</label>
            <input type="text" name="name" value="{panel[1]}" required>

            <label>2. Emoji / Icon</label>
            <select name="emoji" id="emoji-select" onchange="updatePreview()">
                <option value="🎟️" {'selected' if panel[2]=='🎟️' else ''}>🎟️ Ticket</option>
                <option value="❓" {'selected' if panel[2]=='❓' else ''}>❓ Question</option>
                <option value="🚨" {'selected' if panel[2]=='🚨' else ''}>🚨 Report</option>
                <option value="💰" {'selected' if panel[2]=='💰' else ''}>💰 Donation</option>
                <option value="🤝" {'selected' if panel[2]=='🤝' else ''}>🤝 Support</option>
            </select>

            <label>3. Button Text</label>
            <input type="text" name="button_text" id="button-text" value="{panel[6] or 'Create Ticket'}" onkeyup="updatePreview()">

            <label>4. Button Color</label>
            <input type="hidden" name="button_color" id="selected-color" value="{current_color}">
            <div style="margin:10px 0;">
                <span class="color-box {'selected' if current_color == '#00f0ff' else ''}" style="background:#00f0ff" onclick="setColor('#00f0ff')"></span>
                <span class="color-box {'selected' if current_color == '#c026d3' else ''}" style="background:#c026d3" onclick="setColor('#c026d3')"></span>
                <span class="color-box {'selected' if current_color == '#ff00ff' else ''}" style="background:#ff00ff" onclick="setColor('#ff00ff')"></span>
                <span class="color-box {'selected' if current_color == '#00ff88' else ''}" style="background:#00ff88" onclick="setColor('#00ff88')"></span>
                <span class="color-box {'selected' if current_color == '#ff8800' else ''}" style="background:#ff8800" onclick="setColor('#ff8800')"></span>
                <span class="color-box {'selected' if current_color == '#ffff00' else ''}" style="background:#ffff00" onclick="setColor('#ffff00')"></span>
                <span class="color-box {'selected' if current_color == '#ff0088' else ''}" style="background:#ff0088" onclick="setColor('#ff0088')"></span>
                <span class="color-box {'selected' if current_color == '#ff4444' else ''}" style="background:#ff4444" onclick="setColor('#ff4444')"></span>
                <span class="color-box {'selected' if current_color == '#44ff44' else ''}" style="background:#44ff44" onclick="setColor('#44ff44')"></span>
            </div>

            <label>5. Description</label>
            <input type="text" name="description" value="{panel[4] or ''}">

            <label>6. Category ID</label>
            <input type="text" name="category_id" value="{panel[3]}" required>

            <label>7. Support Roles</label>
            <input type="text" name="support_roles" value="{panel[5] or ''}" placeholder="Staff, Admin, Moderator">

            <button type="submit" style="margin-top:30px; width:100%;">Save Changes</button>
        </form>

        <h3>Live Button Preview</h3>
        <div id="preview" style="padding:25px; background:#0f0f1a; border-radius:12px; text-align:center; font-size:22px;">
            {panel[2] or '🎟️'} {panel[6] or 'Create Ticket'}
        </div>
    </div>

    <script>
        function updatePreview() {{
            const emoji = document.getElementById('emoji-select').value || '🎟️';
            const text = document.getElementById('button-text').value || 'Create Ticket';
            document.getElementById('preview').innerHTML = emoji + ' ' + text;
        }}
        function setColor(color) {{
            document.querySelectorAll('.color-box').forEach(b => b.classList.remove('selected'));
            event.currentTarget.classList.add('selected');
            document.getElementById('selected-color').value = color;
            updatePreview();
        }}
    </script>
    """
    return base_template(content, show_back=True)

@app.route("/update-panel/<int:panel_id>", methods=["POST"])
def update_panel(panel_id):
    c.execute("""UPDATE panels SET name=?, emoji=?, category_id=?, description=?, 
                 support_roles=?, button_text=?, button_color=? WHERE id=?""",
              (request.form.get("name"), request.form.get("emoji"), request.form.get("category_id"),
               request.form.get("description"), request.form.get("support_roles"),
               request.form.get("button_text"), request.form.get("button_color"), panel_id))
    conn.commit()
    return redirect("/dashboard")

@app.route("/delete-panel/<int:panel_id>")
def delete_panel(panel_id):
    c.execute("DELETE FROM panels WHERE id = ?", (panel_id,))
    conn.commit()
    return redirect("/dashboard")

@app.route("/<path:path>")
def catch_all(path):
    return redirect("/dashboard")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)