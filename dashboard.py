from flask import Flask, request, redirect

app = Flask(__name__)

@app.route("/")
def home():
    return """
    <h1>🎟️ Ticket Zick Dashboard</h1>
    <h2>✅ Dashboard is Online!</h2>
    <p>You can now create multiple ticket panels from here.</p>
    <p>Full features coming in next update.</p>
    """

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)