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
            .header-buttons {{ display:flex; justify-content:center; gap:15px; flex-wrap:wrap; }}
            .btn {{ background:linear-gradient(45deg,#00f0ff,#c026d3); color:black; padding:16px 32px; font-size:18px; border:none; border-radius:12px; cursor:pointer; min-width:280px; }}
            .btn.invite {{ background:linear-gradient(45deg,#00ff88,#00f0ff); }}
            .grid {{ display:grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap:20px; max-width:1200px; margin:auto; }}
            .card {{ background:#1a1a2e; border-radius:16px; padding:25px; border:1px solid #00f0ff33; max-width:700px; margin:auto; }}
            .panel-item {{ background:#16213e; padding:15px; border-radius:12px; margin:10px 0; display:flex; justify-content:space-between; align-items:center; }}
            input, select {{ padding:12px; margin:8px 0; border-radius:10px; width:100%; background:#16213e; color:white; border:1px solid #334155; }}
            button {{ background:linear-gradient(45deg,#00f0ff,#c026d3); color:black; font-weight:bold; cursor:pointer; padding:14px; }}
            label {{ display:block; margin:20px 0 8px 0; font-weight:600; }}
            .preview {{ margin:20px 0; padding:25px; background:#0f0f1a; border-radius:12px; text-align:center; font-size:22px; border:2px solid #334155; }}
            .color-box {{ width:48px; height:48px; border-radius:10px; display:inline-block; margin:6px; cursor:pointer; border:3px solid transparent; position:relative; }}
            .color-box.selected::after {{ content:"✓"; position:absolute; top:50%; left:50%; transform:translate(-50%,-50%); color:white; font-size:24px; font-weight:bold; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🎟️ Ticket Zick Dashboard</h1>
            <div class="header-buttons">
                <a href="https://discord.com/oauth2/authorize?client_id=1504522333208051872&scope=bot+applications.commands&permissions=8" target="_blank">
                    <button class="btn invite">➕ Invite Ticket Zick to Your Server</button>
                </a>
                <button class="btn" onclick="window.location='/create-panel'">+ Create New Ticket Panel</button>
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
    c.execute("SELECT id, name, emoji, button_text FROM panels ORDER BY id DESC")
    panels = c.fetchall()

    panel_html = ""
    for p in panels:
        panel_html += f'''
        <div class="panel-item">
            <div><strong>{p[1]}</strong> {p[2]} {p[3]}</div>
            <div>
                <button onclick="window.location='/edit-panel/{p[0]}'" style="background:#00f0ff; margin-right:8px;">Edit</button>
                <button onclick="if(confirm('Delete this panel?')) window.location='/delete-panel/{p[0]}'" style="background:#ff4444;">Delete</button>
            </div>
        </div>
        '''

    content = f"""
    <h2 style="text-align:center; color:#00f0ff;">Your Ticket Panels</h2>
    {panel_html if panel_html else "<p style='text-align:center; font-size:18px;'>No panels yet. Create your first one!</p>"}
    """
    return base_template(content, show_back=False)

# ====================== CREATE PANEL ======================
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
                <span class="color-box" style="background:#00ffff" onclick="setColor('#00ffff')"></span>
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

# ====================== SAVE / EDIT / DELETE ======================
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
            </select>

            <label>3. Button Text</label>
            <input type="text" name="button_text" id="button-text" value="{panel[6] or 'Create Ticket'}" onkeyup="updatePreview()">

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
                <span class="color-box" style="background:#00ffff" onclick="setColor('#00ffff')"></span>
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