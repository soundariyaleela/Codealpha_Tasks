from flask import Flask, request, redirect, render_template
import sqlite3
import random
import string
import validators
from datetime import datetime

app = Flask(__name__)

# Database setup
def init_db():
    conn = sqlite3.connect('urls.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS urls (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT UNIQUE NOT NULL,
            long_url TEXT NOT NULL,
            created_at TIMESTAMP NOT NULL,
            clicks INTEGER DEFAULT 0
        )
    ''')
    conn.commit()
    conn.close()

# Generate short code
def generate_code():
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(6))

# Routes
@app.route('/', methods=['GET', 'POST'])
def home():
    short_url = None
    code = None
    
    if request.method == 'POST':
        long_url = request.form.get('long_url', '').strip()
        
        if not validators.url(long_url):
            return render_template('index.html', error='Enter valid URL (include http://)')
        
        code = generate_code()
        
        conn = sqlite3.connect('urls.db')
        cursor = conn.cursor()
        cursor.execute('INSERT INTO urls (code, long_url, created_at) VALUES (?, ?, ?)',
                      (code, long_url, datetime.now()))
        conn.commit()
        conn.close()
        
        short_url = request.host_url + code
    
    return render_template('index.html', short_url=short_url, code=code)

@app.route('/<code>')
def redirect_url(code):
    conn = sqlite3.connect('urls.db')
    cursor = conn.cursor()
    cursor.execute('SELECT long_url FROM urls WHERE code = ?', (code,))
    result = cursor.fetchone()
    conn.close()
    
    if result:
        return redirect(result[0])
    return 'URL not found', 404

if __name__ == '__main__':
    init_db()
    app.run(host="0.0.0.0", port=5000)
