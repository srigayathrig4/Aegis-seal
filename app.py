import os
import sqlite3
import uuid
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "change-this-to-any-long-random-text"
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024  # 5 MB limit
DB = "database.db"
UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {"txt", "png", "jpg", "jpeg"}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS uploads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            original_name TEXT NOT NULL,
            stored_name TEXT NOT NULL,
            file_type TEXT NOT NULL,
            uploaded_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS text_checks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            content TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    """)
    conn.commit()
    conn.close()

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    error = None
    if request.method == "POST":
        name = request.form["name"].strip()
        email = request.form["email"].strip().lower()
        password = request.form["password"]

        if len(password) < 6:
            error = "Password must be at least 6 characters."
        else:
            conn = get_db()
            try:
                conn.execute(
                    "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
                    (name, email, generate_password_hash(password)),
                )
                conn.commit()
                return redirect(url_for("login"))
            except sqlite3.IntegrityError:
                error = "This email is already registered."
            finally:
                conn.close()
    return render_template("register.html", error=error)

@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        email = request.form["email"].strip().lower()
        password = request.form["password"]

        conn = get_db()
        user = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
        conn.close()

        if user and check_password_hash(user["password_hash"], password):
            session["user_id"] = user["id"]
            session["user_name"] = user["name"]
            return redirect(url_for("dashboard"))
        error = "Invalid email or password."
    return render_template("login.html", error=error)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))

@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect(url_for("login"))
    conn = get_db()
    uploads = conn.execute(
        "SELECT * FROM uploads WHERE user_id = ? ORDER BY id DESC",
        (session["user_id"],),
    ).fetchall()
    texts = conn.execute(
        "SELECT * FROM text_checks WHERE user_id = ? ORDER BY id DESC",
        (session["user_id"],),
    ).fetchall()
    conn.close()
    return render_template("dashboard.html", uploads=uploads, texts=texts)

@app.route("/upload", methods=["GET", "POST"])
def upload():
    if "user_id" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        file = request.files.get("file")

        if not file or file.filename == "":
            flash("Please choose a file.", "error")
        elif not allowed_file(file.filename):
            flash("Only .txt, .png, .jpg and .jpeg files are allowed.", "error")
        else:
            original_name = secure_filename(file.filename)
            extension = original_name.rsplit(".", 1)[1].lower()
            stored_name = f"{uuid.uuid4().hex}.{extension}"
            file.save(os.path.join(UPLOAD_FOLDER, stored_name))

            conn = get_db()
            conn.execute(
                "INSERT INTO uploads (user_id, original_name, stored_name, file_type) VALUES (?, ?, ?, ?)",
                (session["user_id"], original_name, stored_name, extension),
            )
            conn.commit()
            conn.close()

            flash("File uploaded successfully.", "success")
            return redirect(url_for("dashboard"))

    return render_template("upload.html")
@app.route("/text", methods=["GET", "POST"])
def check_text():
    if "user_id" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        content = request.form.get("content", "").strip()

        if len(content) < 20:
            flash("Please enter at least 20 characters.", "error")
        elif len(content) > 5000:
            flash("Text is too long. The limit is 5000 characters.", "error")
        else:
            conn = get_db()
            conn.execute(
                "INSERT INTO text_checks (user_id, content) VALUES (?, ?)",
                (session["user_id"], content),
            )
            conn.commit()
            conn.close()
            flash("Text saved successfully.", "success")
            return redirect(url_for("dashboard"))

    return render_template("text.html")
@app.errorhandler(413)
def file_too_large(e):
    flash("File is too large. The limit is 5 MB.", "error")
    return redirect(url_for("upload"))

if __name__ == "__main__":
    init_db()
    app.run(debug=True)