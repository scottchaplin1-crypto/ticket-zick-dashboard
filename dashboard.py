from flask import Flask, request, redirect, render_template_string
import sqlite3
import os

app = Flask(__name__)

# Database setup
conn = sqlite3.connect("config.db", check_same_thread=False)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS panels (
    id INTEGER PRIMARY KEY,
    name TEXT,
    emoji TEXT DEFAULT '🎟️',
    category_id TEXT,
    description TEXT,
    support_roles TEXT DEFAULT '[]',
    button_text TEXT DEFAULT 'Create Ticket',
    button_color TEXT DEFAULT '#00f0ff'
)''')
conn.commit()

@app.route("/")
def home():
    c.execute("SELECT * FROM panels ORDER BY id DESC")
    panels = c.fetchall()
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Ticket Zick Dashboard</title>
        <style>
            body {{ background: #0f0f1a; color: #e0e0ff; font-family: 'Segoe UI', sans-serif; margin: 0; padding: 20px; }}
            h1 {{ color: #00f0ff; text-align: center; }}
            .container {{ max-width: 1100px; margin: auto; }}
            .card {{ background: #1a1a2e; border-radius: 12px; padding: 20px; margin: 15px 0; border: 1px solid #00f0ff33; }}
            input, select, button {{ padding: 10px; margin: 5px 0; border-radius: 8px; border: none; }}
            input, select {{ background: #16213e; color: white; width: 100%; }}
            button {{ background: linear-gradient(45deg, #00f0ff, #c026d3); color: black; font-weight: bold; cursor: pointer; }}
            .panel {{ border-left: 5px solid #c026d3; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🎟️ Ticket Zick Dashboard</h1>
            
            <div class="card">
                <h2>Create New Ticket Panel</h2>
                <form method="POST" action="/create">
                    <input type="text" name="name" placeholder="Panel Name (e.g. Support)" required>
                    <input type="text" name="emoji" placeholder="Emoji (e.g. 🎟️)" value="🎟️">
                    <input type="text" name="description" placeholder="Description" value="Click to open a ticket">
                    <input type="text" name="category_id" placeholder="Category ID (right-click category → Copy ID)" required>
                    <input type="text" name="support_roles" placeholder="Support Roles (comma separated, e.g. Staff,Admin)">
                    <input type="text" name="button_text" placeholder="Button Text" value="Create Ticket">
                    <select name="button_color">
                        <option value="#00f0ff">Cyan</option>
                        <option value="#c026d3">Purple</option>
                        <option value="#ff00ff">Magenta</option>
                    </select>
                    <button type="submit">Create Panel</button>
                </form>
            </div>

            <h2>Existing Panels</h2>
    """
    
    for p in panels:
        html += f"""
            <div class="card panel">
                <h3>{p[2]} {p[1]}</h3>
                <p><strong>Category:</strong> {p[3]}</p>
                <p><strong>Button:</strong> {p[6]} <span style="color:{p[7]}">■</span></p>
                <p><strong>Support Roles:</strong> {p[5]}</p>
            </div>
        """
    
    html += "</div></body></html>"
    return html

@app.route("/create", methods=["POST"])
def create():
    name = request.form.get("name")
    emoji = request.form.get("emoji")
    description = request.form.get("description")
    category_id = request.form.get("category_id")
    support_roles = request.form.get("support_roles", "")
    button_text = request.form.get("button_text", "Create Ticket")
    button_color = request.form.get("button_color", "#00f0ff")
    
    c.execute("""INSERT INTO panels 
        (name, emoji, category_id, description, support_roles, button_text, button_color)
        VALUES (?, ?, ?, ?, ?, ?, ?)""", 
        (name, emoji, category_id, description, support_roles, button_text, button_color))
    conn.commit()
    
    return redirect("/")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)