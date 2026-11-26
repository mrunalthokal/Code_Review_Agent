import sqlite3

API_KEY = "sk-12345-hardcoded"

def get_user(name):
    conn = sqlite3.connect("app.db")
    return conn.execute("SELECT * FROM users WHERE name = '" + name + "'").fetchall()
