import sqlite3
import os

# ensure folders exist
os.makedirs("uploads", exist_ok=True)
os.makedirs("thumbnails", exist_ok=True)

db = sqlite3.connect("users.db")
c = db.cursor()

# users table
c.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL
)
""")

# videos table
c.execute("""
CREATE TABLE IF NOT EXISTS videos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    description TEXT,
    filename TEXT,
    thumbnail TEXT,
    likes INTEGER DEFAULT 0,
    uploader_id INTEGER
)
""")

# likes table
c.execute("""
CREATE TABLE IF NOT EXISTS likes (
    user_id INTEGER,
    video_id INTEGER,
    UNIQUE(user_id, video_id)
)
""")

db.commit()
db.close()
print("Database initialized ✅")
