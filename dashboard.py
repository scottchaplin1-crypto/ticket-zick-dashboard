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

c.execute('''CREATE TABLE IF NOT EXISTS settings (
    key TEXT PRIMARY KEY,
    value TEXT
)''')
conn.commit()

def base_template(content, title="Ticket Zick Dashboard", show_back=True):
    back_button = '''
        <button onclick="window.location='/dashboard'" 
                style="background:linear-gradient(45deg,#00f0ff,#c026d3); color:black; padding:12px 24px; border:none; border-radius:12px; cursor:pointer; font-size:16px;">
            ← Back to Dashboard
        </button>
    ''' if show_back else ''

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>{title}</title>
        <style>
            body {{ background:#0a0a14; color:#e0e0ff; font-family:Segoe UI,sans-serif; margin:0; padding:20px; }}
            h1 {{ color:#00f0ff; text-align:center; }}
            .header {{ text-align:center; margin-bottom:35px; }}
            .header-buttons {{ display:flex; justify-content:center; gap:15px; flex-wrap:wrap; }}
            .btn {{ background:linear-gradient(45deg,#00f0ff,#c026d3); color:black; padding:16px 32px; font-size:18px; border:none; border-radius:12px; cursor:pointer; min-width:280px; }}
            .btn.invite {{ background:linear-gradient(45deg,#00ff88,#00f0ff); }}
            .grid {{ display:grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap:20px; max-width:1200px; margin:auto; }}
            .card {{ background:#1a1a2e; border-radius:16px; padding:25px; border:1px solid #00f0ff33; cursor:pointer; transition:0.3s; }}
            .card:hover {{ transform:scale(1.05); border-color:#c026d3; }}
            input, select, textarea {{ padding:12px; margin:8px 0; border-radius:10px; width:100%; background:#16213e; color:white; border:1px solid #334155; }}
            button {{ background:linear-gradient(45deg,#00f0ff,#c026d3); color:black; font-weight:bold; cursor:pointer; padding:16px; font-size:18px; }}
            label {{ display:block; margin:20px 0 8px 0; font-weight:600; }}
            .preview {{ margin:20px 0; padding:20px; background:#0f0f1a; border-radius:12px; text-align:center; font-size:20px; }}
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
        {content}
    </body>
    </html>
    """

@app.route("/")
@app.route("/dashboard")
def dashboard():
    content = """
    <div class="section-title">Panel Settings</div>
    <div class="grid">
        <div class="card" onclick="window.location='/general'"><h2>General</h2><p>Support team and general items</p></div>
        <div class="card"><h2>Panel</h2><p>Options for the message used to create tickets</p></div>
        <div class="card"><h2>Command Style</h2><p>Options for creating tickets using commands</p></div>
        <div class="card"><h2>Dropdown Style</h2><p>Select menu options</p></div>
    </div>

    <div class="section-title">Advanced Settings</div>
    <div class="grid">
        <div class="card" onclick="window.location='/transcripts'"><h2>Transcript</h2><p>Options for saving transcripts</p></div>
        <div class="card"><h2>Logging</h2><p>Server logging options</p></div>
        <div class="card"><h2>Automation</h2><p>Automation options</p></div>
    </div>
    """
    return base_template(content, show_back=False)

@app.route("/create-panel")
def create_panel():
    content = """
    <h1>Create New Ticket Panel</h1>
    <div class="card">
        <form method="POST" action="/save-panel">
            <label>1. Panel Name</label>
            <p><small>This is the name members will see when choosing a ticket type.</small></p>
            <input type="text" name="name" placeholder="e.g. Support, Bug Report, Appeal" required>

            <label>2. Emoji / Icon</label>
            <p><small>Choose an icon for this ticket button</small></p>
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
                <option value="🕹️">🕹️ Gameplay</option>
                <option value="📋">📋 Feedback</option>
                <option value="🔒">🔒 Private</option>
                <option value="🌟">🌟 VIP</option>
                <option value="🐛">🐛 Bug Report</option>
                <option value="🔥">🔥 Important</option>
                <option value="💡">💡 Idea</option>
            </select>

            <label>3. Description</label>
            <p><small>This text appears when someone opens the ticket.</small></p>
            <input type="text" name="description" value="Our team will assist you shortly." id="desc-input" onkeyup="updatePreview()">

            <label>4. Category ID</label>
            <p><small>Right-click the category in your server → Copy ID</small></p>
            <input type="text" name="category_id" placeholder="123456789012345678" required>

            <label>5. Support Roles</label>
            <p><small>Who can view and reply in these tickets? (comma separated)</small></p>
            <input type="text" name="support_roles" placeholder="Staff, Admin, Moderator">

            <label>6. Button Text</label>
            <p><small>What should the button say?</small></p>
            <input type="text" name="button_text" id="button-text" value="Create Ticket" onkeyup="updatePreview()">

            <label>7. Button Color</label>
            <p><small>Choose the color of the button</small></p>
            <div style="margin:10px 0;">
                <span onclick="setColor('#00f0ff')" style="background:#00f0ff;width:45px;height:45px;display:inline-block;border-radius:8px;cursor:pointer;margin:5px;border:3px solid #fff;"></span>
                <span onclick="setColor('#c026d3')" style="background:#c026d3;width:45px;height:45px;display:inline-block;border-radius:8px;cursor:pointer;margin:5px;"></span>
                <span onclick="setColor('#ff00ff')" style="background:#ff00ff;width:45px;height:45px;display:inline-block;border-radius:8px;cursor:pointer;margin:5px;"></span>
                <span onclick="setColor('#00ff88')" style="background:#00ff88;width:45px;height:45px;display:inline-block;border-radius:8px;cursor:pointer;margin:5px;"></span>
                <span onclick="setColor('#ff8800')" style="background:#ff8800;width:45px;height:45px;display:inline-block;border-radius:8px;cursor:pointer;margin:5px;"></span>
            </div>
            <select name="button_color" id="button-color" onchange="updatePreview()">
                <option value="#00f0ff">Cyan</option>
                <option value="#c026d3">Purple</option>
                <option value="#ff00ff">Magenta</option>
                <option value="#00ff88">Green</option>
                <option value="#ff8800">Orange</option>
            </select>

            <h3 style="margin-top:30px;">Live Button Preview</h3>
            <div id="preview" style="padding:20px; background:#0f0f1a; border-radius:12px; text-align:center; font-size:20px; margin:15px 0;">
                🎟️ Create Ticket
            </div>

            <button type="submit" style="margin-top:30px; width:100%;">Create This Ticket Panel</button>
        </form>
    </div>

    <script>
        function updatePreview() {
            const emoji = document.getElementById('emoji-select').value || '🎟️';
            const text = document.getElementById('button-text').value || 'Create Ticket';
            const color = document.getElementById('button-color').value;
            document.getElementById('preview').innerHTML = emoji + ' ' + text;
            document.getElementById('preview').style.color = color;
        }
        setTimeout(updatePreview, 300);
    </script>
    """
    return base_template(content, show_back=True)

@app.route("/save-panel", methods=["POST"])
def save_panel():
    name = request.form.get("name")
    emoji = request.form.get("emoji")
    description = request.form.get("description")
    category_id = request.form.get("category_id")
    support_roles = request.form.get("support_roles")
    button_text = request.form.get("button_text")
    button_color = request.form.get("button_color")
    
    c.execute("""INSERT INTO panels (name, emoji, category_id, description, support_roles, button_text, button_color)
                 VALUES (?, ?, ?, ?, ?, ?, ?)""", 
              (name, emoji, category_id, description, support_roles, button_text, button_color))
    conn.commit()
    return redirect("/dashboard")

@app.route("/<path:path>")
def catch_all(path):
    return redirect("/dashboard")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)