#flask --app app --debug run#
from flask import Flask, render_template, request, redirect
import sqlite3
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)
app.config["SECRET_KEY"] = "your-secret-key"

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")

        conn = sqlite3.connect("login.db")
        cursor = conn.cursor()

        cursor.execute(
            "SELECT password FROM users WHERE username = ?",
            (username,)
        )

        user = cursor.fetchone()
        conn.close()

        if user and check_password_hash(user[0], password):
            return redirect("/dashboard")
        else:
            return "Invalid credentials"

    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")

        hashed_password = generate_password_hash(password)

        conn = sqlite3.connect("login.db")
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)",
            (username, hashed_password)
        )

        conn.commit()
        conn.close()

        return redirect("/login")

    return render_template("register.html")

@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")

if __name__ == "__main__":
    app.run(debug=True)