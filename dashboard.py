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

def base_template(content, title="Ticket Zick Dashboard", show_back=False):
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
            .card {{ background:#1a1a2e; border-radius:16px; padding:30px; border:1px solid #00f0ff33; max-width:700px; margin:auto; }}
            input, select, textarea {{ padding:12px; margin:8px 0; border-radius:10px; width:100%; background:#16213e; color:white; border:1px solid #334155; }}
            button {{ background:linear-gradient(45deg,#00f0ff,#c026d3); color:black; font-weight:bold; cursor:pointer; padding:16px; font-size:18px; }}
            label {{ display:block; margin:20px 0 8px 0; font-weight:600; }}
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
            <select name="emoji" style="height:180px;">
                <option value="🎟️">🎟️ Ticket</option>
                <option value="❓">❓ Question</option>
                <option value="🚨">🚨 Report</option>
                <option value="💰">💰 Donation</option>
                <option value="🤝">🤝 Support</option>
                <option value="🛠️">🛠️ Technical</option>
                <option value="🎮">🎮 Gaming</option>
                <option value="📝">📝 Application</option>
                <option value="❤️">❤️ Love / Help</option>
                <option value="⚠️">⚠️ Warning</option>
                <option value="🔨">🔨 Ban Appeal</option>
                <option value="💸">💸 Payment</option>
                <option value="🎉">🎉 Event</option>
                <option value="📢">📢 Announcement</option>
                <option value="🕹️">🕹️ Gameplay</option>
                <option value="📋">📋 Feedback</option>
                <option value="🔒">🔒 Private</option>
                <option value="🌟">🌟 VIP</option>
                <option value="🧩">🧩 Puzzle / Help</option>
                <option value="📞">📞 Contact</option>
                <option value="🛡️">🛡️ Protection</option>
                <option value="🎨">🎨 Creative</option>
                <option value="📚">📚 Study</option>
                <option value="🍕">🍕 Food</option>
                <option value="🎵">🎵 Music</option>
                <option value="🏆">🏆 Competition</option>
                <option value="🌍">🌍 General</option>
            </select>

            <label>3. Description</label>
            <p><small>This text appears when someone opens the ticket.</small></p>
            <input type="text" name="description" value="Our team will assist you shortly." style="width:100%;">

            <label>4. Category ID</label>
            <p><small>Right-click the category in your server → Copy ID</small></p>
            <input type="text" name="category_id" placeholder="123456789012345678" required>

            <label>5. Support Roles</label>
            <p><small>Who can view and reply in these tickets? (comma separated)</small></p>
            <input type="text" name="support_roles" placeholder="Staff, Admin, Moderator">

            <label>6. Button Text</label>
            <p><small>What should the button say?</small></p>
            <input type="text" name="button_text" value="Create Ticket">

            <label>7. Button Color</label>
            <p><small>Choose the color of the button</small></p>
            <select name="button_color">
                <option value="#00f0ff">Cyan</option>
                <option value="#c026d3">Purple</option>
                <option value="#ff00ff">Magenta</option>
                <option value="#00ff88">Green</option>
                <option value="#ff8800">Orange</option>
            </select>

            <button type="submit" style="margin-top:30px; width:100%;">Create This Ticket Panel</button>
        </form>
    </div>
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