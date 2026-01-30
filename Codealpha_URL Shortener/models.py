import sqlite3
import os

DB_NAME = 'swiftlink.db'

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize database with click tracking"""
    if os.path.exists(DB_NAME):
        return
    
    conn = get_db_connection()
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
    
    # Create index for faster lookups
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_code ON urls (code)')
    
    conn.commit()
    conn.close()

def insert_url(code, long_url, created_at):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO urls (code, long_url, created_at) VALUES (?, ?, ?)',
                   (code, long_url, created_at))
    conn.commit()
    conn.close()

def get_long_url(code):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT long_url FROM urls WHERE code = ?', (code,))
    result = cursor.fetchone()
    conn.close()
    return result['long_url'] if result else None

def get_click_count(code):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT clicks FROM urls WHERE code = ?', (code,))
    result = cursor.fetchone()
    conn.close()
    return result['clicks'] if result else 0

def increment_click(code):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE urls SET clicks = clicks + 1 WHERE code = ?', (code,))
    conn.commit()
    conn.close()

def get_recent_links(limit=10):
    """Get recently created links for dashboard"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT code, long_url, created_at, clicks 
        FROM urls 
        ORDER BY created_at DESC 
        LIMIT ?
    ''', (limit,))
    results = cursor.fetchall()
    conn.close()
    return [dict(row) for row in results]