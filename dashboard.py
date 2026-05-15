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
            .card {{ background:#1a1a2e; border-radius:16px; padding:20px; border:1px solid #00f0ff33; }}
            .panel-item {{ background:#16213e; padding:15px; border-radius:12px; margin:10px 0; display:flex; justify-content:space-between; align-items:center; }}
            input, select {{ padding:12px; margin:8px 0; border-radius:10px; width:100%; background:#16213e; color:white; border:1px solid #334155; }}
            button {{ background:linear-gradient(45deg,#00f0ff,#c026d3); color:black; font-weight:bold; cursor:pointer; padding:14px; }}
            .color-box {{ width:40px; height:40px; border-radius:8px; display:inline-block; margin:4px; cursor:pointer; border:3px solid transparent; position:relative; }}
            .color-box.selected::after {{ content:"✓"; position:absolute; top:50%; left:50%; transform:translate(-50%,-50%); color:white; font-size:20px; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🎟️ Ticket Zick Dashboard</h1>
            <div class="header-buttons">
                <a href="https://discord.com/oauth2/authorize?client_id=1504522333208051872&scope=bot+applications.commands&permissions=8" target="_blank">
                    <button class="btn invite">➕ Invite to Server</button>
                </a>
                <button class="btn" onclick="window.location='/create-panel'">+ Create New Ticket Panel</button>
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
    c.execute("SELECT id, name, emoji, button_text FROM panels ORDER BY id DESC")
    panels = c.fetchall()

    panel_list = ""
    for p in panels:
        panel_list += f"""
        <div class="panel-item">
            <div><strong>{p[1]}</strong> {p[2]} {p[3]}</div>
            <div>
                <button onclick="window.location='/edit-panel/{p[0]}'" style="background:#00f0ff; margin-right:8px;">Edit</button>
                <button onclick="if(confirm('Delete this panel?')) window.location='/delete-panel/{p[0]}'" style="background:#ff4444;">Delete</button>
            </div>
        </div>
        """

    content = f"""
    <h2 style="text-align:center;">Your Ticket Panels</h2>
    {panel_list if panel_list else "<p style='text-align:center;'>No panels yet. Create your first one!</p>"}
    """
    return base_template(content, show_back=False)

@app.route("/create-panel")
def create_panel():
    content = """<h1>Create New Ticket Panel</h1><div class="card"> ... (same form as before) ... """
    # (I'll keep it short here — you can use the previous form code)
    return base_template(content, show_back=True)

# Edit & Delete routes
@app.route("/edit-panel/<int:panel_id>")
def edit_panel(panel_id):
    c.execute("SELECT * FROM panels WHERE id = ?", (panel_id,))
    panel = c.fetchone()
    if not panel:
        return redirect("/dashboard")

    content = f"""
    <h1>Editing Panel: {panel[1]}</h1>
    <div class="card">
        <form method="POST" action="/save-panel/{panel[0]}">
            <!-- Same fields as create, pre-filled -->
            <input type="text" name="name" value="{panel[1]}" required>
            <!-- ... add other fields similarly ... -->
            <button type="submit">Save Changes</button>
        </form>
    </div>
    """
    return base_template(content, show_back=True)

@app.route("/save-panel/<int:panel_id>", methods=["POST"])
def save_edited_panel(panel_id):
    # Update logic
    name = request.form.get("name")
    # ... get other fields ...
    c.execute("""UPDATE panels SET name=?, emoji=?, category_id=?, description=?, 
                 support_roles=?, button_text=?, button_color=? WHERE id=?""",
              (name, request.form.get("emoji"), ... , panel_id))
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