from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from dotenv import load_dotenv
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

load_dotenv()

app = Flask(__name__)

app.secret_key = "edugenie-secret-key"

DATABASE = "edugenie.db"


def get_db():
    conn = sqlite3.connect(
        DATABASE,
        timeout=10
    )
    conn.row_factory = sqlite3.Row
    return conn


def create_database():

    conn = get_db()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


create_database()


# ---------------- LOGIN ----------------

@app.route("/")
def home():

    if "user_id" not in session:
        return redirect(url_for("login"))

    return render_template(
        "index.html",
        username=session.get("username")
    )


@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        conn = get_db()

        user = conn.execute(
            "SELECT * FROM users WHERE username = ?",
            (username,)
        ).fetchone()

        conn.close()

        if user and check_password_hash(
            user["password"],
            password
        ):

            session["user_id"] = user["id"]
            session["username"] = user["username"]

            return redirect(url_for("home"))

        return render_template(
            "login.html",
            error="Invalid username or password."
        )

    return render_template("login.html")


# ---------------- REGISTER ----------------

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        if not username or not password:

            return render_template(
                "register.html",
                error="Please fill all fields."
            )

        hashed_password = generate_password_hash(password)

        try:

            conn = get_db()

            conn.execute(
                "INSERT INTO users (username, password) VALUES (?, ?)",
                (username, hashed_password)
            )

            conn.commit()
            conn.close()

            return redirect(url_for("login"))

        except sqlite3.IntegrityError:

            return render_template(
                "register.html",
                error="Username already exists."
            )

    return render_template("register.html")


# ---------------- LOGOUT ----------------

@app.route("/logout")
def logout():

    session.clear()

    return redirect(url_for("login"))


# ---------------- AI CHAT ----------------

@app.route("/api/ask", methods=["POST"])
def ask_question():

    if "user_id" not in session:
        return jsonify({
            "success": False,
            "error": "Please login first."
        }), 401

    try:

        from qna import QnA

        data = request.get_json(silent=True) or {}

        question = str(
            data.get("question", "")
        ).strip()

        if not question:

            return jsonify({
                "success": False,
                "error": "Please enter a question."
            }), 400

        ai = QnA()

        answer = ai.ask(question)

        return jsonify({
            "success": True,
            "answer": answer
        })

    except Exception as error:

        return jsonify({
            "success": False,
            "error": str(error)
        }), 500


# ---------------- EXPLAIN ----------------

@app.route("/api/explain", methods=["POST"])
def explain():

    if "user_id" not in session:
        return jsonify({
            "success": False,
            "error": "Please login first."
        }), 401

    try:

        from explanation_module import explain_topic

        data = request.get_json(silent=True) or {}

        topic = str(
            data.get("topic", "")
        ).strip()

        level = str(
            data.get("level", "college")
        )

        if not topic:

            return jsonify({
                "success": False,
                "error": "Please enter a topic."
            }), 400

        answer = explain_topic(topic, level)

        return jsonify({
            "success": True,
            "answer": answer
        })

    except Exception as error:

        return jsonify({
            "success": False,
            "error": str(error)
        }), 500


# ---------------- QUIZ ----------------

@app.route("/api/quiz", methods=["POST"])
def quiz():

    if "user_id" not in session:
        return jsonify({
            "success": False,
            "error": "Please login first."
        }), 401

    try:

        from quiz_module import generate_quiz

        data = request.get_json(silent=True) or {}

        topic = str(
            data.get("topic", "")
        ).strip()

        difficulty = str(
            data.get("difficulty", "medium")
        )

        count = int(
            data.get("count", 5)
        )

        if not topic:

            return jsonify({
                "success": False,
                "error": "Please enter a topic."
            }), 400

        result = generate_quiz(
            topic,
            difficulty,
            count
        )

        return jsonify({
            "success": True,
            "quiz": result
        })

    except Exception as error:

        return jsonify({
            "success": False,
            "error": str(error)
        }), 500


# ---------------- LEARNING PATH ----------------

@app.route("/api/learning-path", methods=["POST"])
def learning_path():

    if "user_id" not in session:
        return jsonify({
            "success": False,
            "error": "Please login first."
        }), 401

    try:

        from learning_path import create_learning_path

        data = request.get_json(silent=True) or {}

        topic = str(
            data.get("topic", "")
        ).strip()

        level = str(
            data.get("level", "beginner")
        )

        if not topic:

            return jsonify({
                "success": False,
                "error": "Please enter a topic."
            }), 400

        result = create_learning_path(
            topic,
            level
        )

        return jsonify({
            "success": True,
            "answer": result
        })

    except Exception as error:

        return jsonify({
            "success": False,
            "error": str(error)
        }), 500


# ---------------- HEALTH CHECK ----------------

@app.route("/api/health")
def health():

    import os

    return jsonify({
        "success": True,
        "app": "EduGenie",
        "gemini_configured": bool(
            os.getenv("GEMINI_API_KEY")
        )
    })


if __name__ == "__main__":

    app.run(
        debug=True,
        host="127.0.0.1",
        port=5000
    )