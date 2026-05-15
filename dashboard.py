from flask import Flask, request, redirect, render_template_string
import sqlite3
import os
import json

app = Flask(__name__)

conn = sqlite3.connect("config.db", check_same_thread=False)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS panels (
    id INTEGER PRIMARY KEY,
    name TEXT,
    emoji TEXT,
    category_id TEXT,
    description TEXT,
    support_roles TEXT,
    button_text TEXT,
    button_color TEXT
)''')
conn.commit()

# Navigation Menu
MENU = [
    ("General", "/general"),
    ("Panel Settings", "/panel"),
    ("Ticket Options", "/ticket"),
    ("Dropdown Style", "/dropdown"),
    ("Forms", "/forms"),
    ("Transcripts", "/transcripts"),
    ("Logging", "/logging"),
    ("Automation", "/automation")
]

def base_template(content, title="Dashboard"):
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Ticket Zick - {title}</title>
        <style>
            body {{ margin:0; background:#0a0a14; color:#e0e0ff; font-family:Segoe UI,sans-serif; display:flex; height:100vh; }}
            .sidebar {{ width:260px; background:#111827; padding:20px; border-right:1px solid #00f0ff33; }}
            .sidebar h1 {{ color:#00f0ff; text-align:center; }}
            .nav a {{ display:block; padding:12px 15px; color:#c026d3; text-decoration:none; border-radius:8px; margin:4px 0; }}
            .nav a:hover, .nav a.active {{ background:#1e2937; color:#00f0ff; }}
            .main {{ flex:1; padding:30px; overflow:auto; }}
            .card {{ background:#1a1a2e; padding:25px; border-radius:16px; border:1px solid #00f0ff22; }}
            input, select, button {{ padding:12px; margin:8px 0; border-radius:10px; width:100%; }}
            input, select {{ background:#16213e; color:white; border:none; }}
            button {{ background:linear-gradient(45deg,#00f0ff,#c026d3); color:black; font-weight:bold; cursor:pointer; }}
        </style>
    </head>
    <body>
        <div class="sidebar">
            <h1>🎟️ Ticket Zick</h1>
            <div class="nav">
                {"".join(f'<a href="{url}">{name}</a>' for name, url in MENU)}
            </div>
        </div>
        <div class="main">
            {content}
        </div>
    </body>
    </html>
    """

@app.route("/")
def home():
    return redirect("/general")

@app.route("/general")
def general():
    content = "<h1>General Settings</h1><p>Coming soon - Support roles, Two-step close, etc.</p>"
    return base_template(content, "General")

@app.route("/panel")
def panel():
    c.execute("SELECT * FROM panels ORDER BY id DESC")
    panels = c.fetchall()
    
    form = """
    <h1>Panel Settings</h1>
    <div class="card">
        <h2>Create New Panel</h2>
        <form method="POST" action="/create">
            <input type="text" name="name" placeholder="Panel Name" required>
            <input type="text" name="emoji" placeholder="Emoji" value="🎟️">
            <input type="text" name="description" placeholder="Description" value="Click to open a ticket">
            <input type="text" name="category_id" placeholder="Category ID" required>
            <input type="text" name="support_roles" placeholder="Support Roles (Staff,Admin)">
            <input type="text" name="button_text" placeholder="Button Text" value="Create Ticket">
            <select name="button_color">
                <option value="#00f0ff">Cyan</option>
                <option value="#c026d3">Purple</option>
            </select>
            <button type="submit">Create Panel</button>
        </form>
    </div>
    """
    
    for p in panels:
        form += f"""
        <div class="card">
            <h3>{p[2]} {p[1]}</h3>
            <p>Category: {p[3]}</p>
            <p>Button: {p[6]} <span style="color:{p[7]}">⬛</span></p>
        </div>
        """
    return base_template(form, "Panel Settings")

@app.route("/create", methods=["POST"])
def create():
    # ... (same as before)
    name = request.form.get("name")
    emoji = request.form.get("emoji")
    description = request.form.get("description")
    category_id = request.form.get("category_id")
    support_roles = request.form.get("support_roles", "")
    button_text = request.form.get("button_text", "Create Ticket")
    button_color = request.form.get("button_color", "#00f0ff")
    
    c.execute("""INSERT INTO panels (name, emoji, category_id, description, support_roles, button_text, button_color)
                 VALUES (?, ?, ?, ?, ?, ?, ?)""", 
              (name, emoji, category_id, description, support_roles, button_text, button_color))
    conn.commit()
    return redirect("/panel")

# Add more routes later (ticket, dropdown, etc.)
@app.route("/ticket")
def ticket():
    return base_template("<h1>Ticket Options</h1><p>Channel names, roles on open/close, etc. (Coming soon)</p>", "Ticket Options")

@app.route("/dropdown")
def dropdown():
    return base_template("<h1>Dropdown Style</h1><p>Coming soon</p>", "Dropdown Style")

# Add the rest as needed

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)