import sqlite3

db = sqlite3.connect("users.db")
c = db.cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS users (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE,
  password TEXT
)
""")

db.commit()
db.close()

print("DB CREATED")
