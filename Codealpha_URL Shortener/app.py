from flask import Flask, request, redirect, render_template
import sqlite3
import random
import string
import validators
from datetime import datetime

app = Flask(__name__)

DB_NAME = "urls.db"

# ---------------- DATABASE ----------------
def get_db():
    return sqlite3.connect(DB_NAME)

def init_db():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS urls (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT UNIQUE NOT NULL,
            long_url TEXT NOT NULL,
            created_at TIMESTAMP NOT NULL,
            clicks INTEGER DEFAULT 0
        )
    """)
    conn.commit()
    conn.close()

# 🔥 VERY IMPORTANT FOR RENDER
init_db()

# ---------------- HELPERS ----------------
def generate_code():
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(6))

# ---------------- ROUTES ----------------
@app.route('/', methods=['GET', 'POST'])
def home():
    short_url = None
    code = None
    error = None

    if request.method == 'POST':
        long_url = request.form.get('long_url', '').strip()

        if not validators.url(long_url):
            error = "Enter a valid URL (include http:// or https://)"
        else:
            code = generate_code()
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO urls (code, long_url, created_at) VALUES (?, ?, ?)",
                (code, long_url, datetime.now())
            )
            conn.commit()
            conn.close()

            short_url = request.host_url + code

    return render_template(
        "index.html",
        short_url=short_url,
        code=code,
        error=error
    )

@app.route('/<code>')
def redirect_url(code):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT long_url FROM urls WHERE code = ?", (code,))
    result = cursor.fetchone()

    if result:
        cursor.execute(
            "UPDATE urls SET clicks = clicks + 1 WHERE code = ?",
            (code,)
        )
        conn.commit()
        conn.close()
        return redirect(result[0])

    conn.close()
    return "URL not found", 404

@app.route('/favicon.ico')
def favicon():
    return '', 204

# ---------------- LOCAL RUN ----------------
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
