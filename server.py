from flask import Flask, request, jsonify, send_from_directory
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)

DB_FILE = "users.db"
UPLOAD_FOLDER = "uploads"
THUMB_FOLDER = "thumbnails"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(THUMB_FOLDER, exist_ok=True)


# helper to get db connection
def get_db():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

@app.route("/register", methods=["POST"])
def register():
    data = request.json
    username = data["username"]
    password = data["password"]

    password_hash = generate_password_hash(password)

    db = get_db()
    try:
        db.execute(
            "INSERT INTO users (username, password_hash) VALUES (?, ?)",
            (username, password_hash)
        )
        db.commit()
        return jsonify({"status": "ok"})
    except:
        return jsonify({"error": "user exists"}), 409
    finally:
        db.close()

@app.route("/login", methods=["POST"])
def login():
    data = request.json
    db = get_db()
    user = db.execute(
        "SELECT * FROM users WHERE username = ?",
        (data["username"],)
    ).fetchone()
    db.close()

    if user and check_password_hash(user["password_hash"], data["password"]):
        return jsonify({"status": "ok", "user_id": user["id"]})
    return jsonify({"status": "fail"}), 401

@app.route("/upload", methods=["POST"])
def upload():
    video = request.files["video"]
    thumbnail = request.files.get("thumbnail", None)
    title = request.form.get("title", "")
    desc = request.form.get("description", "")
    uploader = request.form.get("user_id", None)

    if not video or not uploader:
        return jsonify({"error": "missing video or user_id"}), 400

    filename = secure_filename(video.filename)
    video.save(os.path.join(UPLOAD_FOLDER, filename))

    thumb_filename = None
    if thumbnail:
        thumb_filename = secure_filename(thumbnail.filename)
        thumbnail.save(os.path.join(THUMB_FOLDER, thumb_filename))

    db = get_db()
    db.execute(
        "INSERT INTO videos (title, description, filename, thumbnail, uploader_id) VALUES (?, ?, ?, ?, ?)",
        (title, desc, filename, thumb_filename, uploader)
    )
    db.commit()
    db.close()
    return jsonify({"status": "uploaded"})

@app.route("/like/<int:vid>", methods=["POST"])
def like(vid):
    data = request.json
    user_id = data.get("user_id")
    if not user_id:
        return jsonify({"error": "missing user_id"}), 400

    db = get_db()
    # add like if not exists
    db.execute(
        "INSERT OR IGNORE INTO likes (user_id, video_id) VALUES (?, ?)",
        (user_id, vid)
    )
    db.execute(
        "UPDATE videos SET likes = likes + 1 WHERE id = ?",
        (vid,)
    )
    db.commit()
    db.close()
    return jsonify({"liked": True})

@app.route("/videos/<int:vid_id>", methods=["GET"])
def get_video(vid_id):
    db = get_db()
    v = db.execute(
        "SELECT id, title, description, uploader_id, thumbnail, filename, likes FROM videos WHERE id=?",
        (vid_id,)
    ).fetchone()
    db.close()
    if not v:
        return jsonify({"error": "Video not found"}), 404
    return jsonify(dict(v))

@app.route("/videos/<path:filename>")
def serve_video(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

@app.route("/thumbnails/<path:filename>")
def serve_thumbnail(filename):
    return send_from_directory(THUMB_FOLDER, filename)

@app.route("/")
def home():
    return "CrystalTube backend online 🔥"

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000))
    )
