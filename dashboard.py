from flask import Flask, request, redirect, render_template_string
import os
import sqlite3

app = Flask(__name__)

conn = sqlite3.connect("config.db", check_same_thread=False)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS panels (
    id INTEGER PRIMARY KEY,
    name TEXT,
    emoji TEXT,
    category_id TEXT,
    description TEXT
)''')
conn.commit()

@app.route("/")
def home():
    c.execute("SELECT * FROM panels ORDER BY id DESC")
    panels = c.fetchall()
    
    html = """
    <h1>🎟️ Ticket Zick Dashboard</h1>
    <h2>Create New Ticket Panel</h2>
    <form method="POST" action="/create">
        <p>Panel Name: <input type="text" name="name" placeholder="Support / Reports" required></p>
        <p>Emoji: <input type="text" name="emoji" value="🎟️" required></p>
        <p>Description: <input type="text" name="description" placeholder="Click to open a ticket" value="Click to open a ticket"></p>
        <p>Category ID: <input type="text" name="category_id" placeholder="Right-click category → Copy ID" required></p>
        <button type="submit">Create Panel</button>
    </form>
    <hr>
    <h2>Existing Panels</h2>
    """
    
    for p in panels:
        html += f"""
        <div style="border:1px solid #444; padding:10px; margin:10px 0;">
            <h3>{p[2]} {p[1]}</h3>
            <p><b>Category ID:</b> {p[3]}</p>
            <p><b>Description:</b> {p[4]}</p>
        </div>
        """
    
    return html

@app.route("/create", methods=["POST"])
def create():
    name = request.form.get("name")
    emoji = request.form.get("emoji")
    description = request.form.get("description")
    category_id = request.form.get("category_id")
    
    c.execute("INSERT INTO panels (name, emoji, category_id, description) VALUES (?, ?, ?, ?)", 
              (name, emoji, category_id, description))
    conn.commit()
    
    return redirect("/")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)