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

def base_template(content, title="Ticket Zick Dashboard"):
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>{title}</title>
        <style>
            body {{ background:#0a0a14; color:#e0e0ff; font-family:Segoe UI,sans-serif; margin:0; padding:20px; }}
            h1 {{ color:#00f0ff; text-align:center; }}
            .header {{ text-align:center; margin-bottom:30px; }}
            .grid {{ display:grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap:20px; max-width:1200px; margin:auto; }}
            .card {{ background:#1a1a2e; border-radius:16px; padding:20px; border:1px solid #00f0ff33; cursor:pointer; transition:0.3s; }}
            .card:hover {{ transform:scale(1.05); border-color:#c026d3; }}
            .create-btn {{ background:linear-gradient(45deg,#00f0ff,#c026d3); color:black; padding:16px 32px; font-size:18px; border:none; border-radius:12px; cursor:pointer; }}
            .panel-list {{ margin-top:40px; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🎟️ Ticket Zick Dashboard</h1>
            <button class="create-btn" onclick="window.location='/create-panel'">+ Create New Ticket Panel</button>
        </div>
        {content}
    </body>
    </html>
    """

@app.route("/")
def home():
    c.execute("SELECT * FROM panels ORDER BY id DESC")
    panels = c.fetchall()
    
    cards = """
    <div class="grid">
        <div class="card" onclick="window.location='/general'"><h2>General</h2><p>Support team and other general items</p></div>
        <div class="card" onclick="window.location='/panel'"><h2>Panel Settings</h2><p>Options for the message used to create tickets</p></div>
        <div class="card" onclick="window.location='/ticket'"><h2>Ticket</h2><p>General Ticket options</p></div>
        <div class="card" onclick="window.location='/dropdown'"><h2>Dropdown Style</h2><p>Select menu options</p></div>
        <div class="card" onclick="window.location='/forms'"><h2>Forms</h2><p>Form options</p></div>
        <div class="card" onclick="window.location='/transcripts'"><h2>Transcripts</h2><p>Transcript settings</p></div>
        <div class="card" onclick="window.location='/logging'"><h2>Logging</h2><p>Server logging options</p></div>
        <div class="card" onclick="window.location='/automation'"><h2>Automation</h2><p>Automation options</p></div>
    </div>
    """

    panel_list = '<div class="panel-list"><h2>Your Ticket Panels</h2>'
    for p in panels:
        panel_list += f"""
        <div class="card" onclick="window.location='/edit-panel/{p[0]}'">
            <h3>{p[2]} {p[1]}</h3>
            <p>Category: {p[3]}</p>
            <p>Button: {p[6]}</p>
        </div>
        """
    panel_list += "</div>"

    return base_template(cards + panel_list)

@app.route("/create-panel")
def create_panel():
    return base_template("""
        <h2>Create New Ticket Panel</h2>
        <form method="POST" action="/save-panel">
            <input type="text" name="name" placeholder="Panel Name (e.g. Support)" required><br><br>
            <input type="text" name="emoji" placeholder="Emoji" value="🎟️"><br><br>
            <input type="text" name="description" placeholder="Description" value="Click to open a ticket"><br><br>
            <input type="text" name="category_id" placeholder="Category ID" required><br><br>
            <input type="text" name="support_roles" placeholder="Support Roles (Staff,Admin)"><br><br>
            <input type="text" name="button_text" placeholder="Button Text" value="Create Ticket"><br><br>
            <select name="button_color">
                <option value="#00f0ff">Cyan</option>
                <option value="#c026d3">Purple</option>
            </select><br><br>
            <button type="submit" class="create-btn">Create Panel</button>
        </form>
    """, "Create New Panel")

@app.route("/save-panel", methods=["POST"])
def save_panel():
    # Save to database
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
    return redirect("/")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)