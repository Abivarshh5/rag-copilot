import sqlite3
import os

db_path = "app.db"
if not os.path.exists(db_path):
    print("app.db does not exist")
    exit()

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    print(f"Tables: {tables}")
    
    if ('users',) in tables:
        cursor.execute("SELECT email FROM users")
        users = cursor.fetchall()
        print(f"Users: {users}")
    else:
        print("No users table found in app.db")
        
except Exception as e:
    print(f"Error: {e}")
