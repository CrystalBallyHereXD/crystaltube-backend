from flask import Flask, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3

app = Flask(__name__)

DB_NAME = "users.db"

def get_db():
    return sqlite3.connect(DB_NAME)

@app.route("/")
def home():
    return "CrystalTube backend online"

@app.route("/signup", methods=["POST"])
def signup():
    data = request.json
    username = data["username"]
    password = data["password"]

    hashed = generate_password_hash(password)

    db = get_db()
    c = db.cursor()

    try:
        c.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)",
            (username, hashed)
        )
        db.commit()
    except sqlite3.IntegrityError:
        return jsonify({"error": "user exists"})

    db.close()
    return jsonify({"ok": True})

@app.route("/login", methods=["POST"])
def login():
    data = request.json
    username = data["username"]
    password = data["password"]

    db = get_db()
    c = db.cursor()

    c.execute("SELECT password FROM users WHERE username = ?", (username,))
    row = c.fetchone()
    db.close()

    if not row:
        return jsonify({"error": "no user"})

    if check_password_hash(row[0], password):
        return jsonify({"ok": True})
    else:
        return jsonify({"error": "wrong password"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
